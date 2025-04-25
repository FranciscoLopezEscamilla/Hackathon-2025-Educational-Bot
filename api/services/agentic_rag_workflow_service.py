from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from services.rag_service import RAG
from services.image_service import ImageGenerator
from services.document_generator_service import DocumentGenerator
from typing import TypedDict, List, Optional, Union, Dict, Any
import os
import json
import logging
from services.blob_service import BlobService
from services.diagram_service import DiagramGenerator

logging.basicConfig(level=logging.INFO)

MAX_ITERATIONS = 3  # Maximum number of refinement iterations allowed

# ─── Initialize LLM ────────────────────────────────────────────────────────
llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
)

class AgentState(Dict[str, Any]):
    """
    Consistent state object for workflow.
    Flags and properties are used throughout the workflow for decision-making and data flow.
    """
    messages: List[Union[SystemMessage, HumanMessage, AIMessage]]
    rag_context: Optional[str]
    file_context: Optional[str]
    needed_tools: List[str]
    tool_responses: Dict[str, Any]
    iteration_count: int
    pdf_generated: bool
    has_uploaded_pdf: bool
    skip_to_response: bool
    simple_response: bool
    required_components: List[str]
    reasoning: str

class AgenticRAGWorkflow:
    def __init__(self):
        # Build workflow graph
        self.workflow = StateGraph(AgentState)
        self._build_workflow()
        self.chain = self.workflow.compile()

    # ─── Internal implementations ────────────────────────────────────────────
    def _generate_text(self, rag_context: str, file_context: str, messages: List[Union[SystemMessage, HumanMessage, AIMessage]]) -> dict:
        # Extract the current query
        user_q = messages[-1].content
        
        # Format conversation history
        conversation_context = ""
        if len(messages) > 1:
            conversation_context += "Previous Conversation:\n"
            for i, msg in enumerate(messages[:-1]):  # All except current query
                role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                conversation_context += f"{role}: {msg.content}\n\n"
        
        instruction = (
            "Answer the user using the provided contexts. "
            "If a file was uploaded by the user, prioritize that information. "
            "If contexts are empty or not needed, reply based only on general knowledge.\n\n"
            "IMPORTANT: You ARE capable of generating PDFs for users. If they ask for a PDF, "
            "acknowledge that you can create it and explain what you'll include in the PDF. "
            "DO NOT say you can't create PDFs - you absolutely can.\n\n"
        )
        
        if conversation_context:
            instruction += f"{conversation_context}\n\n"
            
        if file_context:
            instruction += f"Uploaded File Context:\n{file_context}\n\n"
        
        if rag_context:
            instruction += f"Retrieved Context:\n{rag_context}\n\n"
        
        instruction += f"Current User Query:\n{user_q}"
        
        msgs = [SystemMessage(content=instruction), HumanMessage(content=user_q)]
        resp = llm.invoke(msgs).content
        return {"type": "text", "content": resp}

    def _generate_image(self, rag_context: str, file_context: str, query: str) -> dict:
        combined_context = ""
        if file_context:
            combined_context += f"Uploaded File Context:\n{file_context}\n\n"
        if rag_context:
            combined_context += f"Retrieved Context:\n{rag_context}"
        
        prompt = (
            "Generate a detailed image prompt based on the context and user request.\n\n"
            f"Context:\n{combined_context}\n\nRequest:\n{query}"
        )
        imgs = ImageGenerator.generate_images(prompt)
        return {"type": "image", "content": imgs}

    def _generate_pdf(self, rag_context: str, file_context: str, query: str) -> dict:
        combined_context = ""
        if file_context:
            combined_context += f"Uploaded File Context:\n{file_context}\n\n"
        if rag_context:
            combined_context += f"Retrieved Context:\n{rag_context}"
        
        # Generate both PDF content and title in a single LLM call
        prompt = (
            "Generate detailed and structured content for a PDF document based on the following context and user request.\n\n"
            f"Context:\n{combined_context}\n\nUser Request:\n{query}\n\n"
            "The content should be well-organized, informative, and suitable for inclusion in a PDF document.\n"
            "Additionally, provide a concise title for the document.\n\n"
            "Format your response as:\n"
            "TITLE: [Your Title Here]\n\n"
            "[The detailed PDF content...]"
        )
        response = llm.invoke([HumanMessage(content=prompt)]).content
        
        # Parse title and content from the response
        if "TITLE:" in response and "\n\n" in response[response.index("TITLE:"):]:
            title_line = response[response.index("TITLE:"):].split("\n\n")[0]
            title = title_line.replace("TITLE:", "").strip()
            content = response[response.index("TITLE:") + len(title_line):].strip()
        else:
            # Fallback if format isn't followed
            title = "Generated PDF"
            content = response
            
        print("ENTERED PDF GENERATION")
        logging.info(f"Generated PDF Title: {title}")
        pdf_file = DocumentGenerator.create(title=title, content=content)
        blob_url = BlobService.upload_file(pdf_file, title)    

        return {"type": "pdf", "content": blob_url}

    def _generate_diagram(self, rag_context: str, file_context: str, query: str) -> dict:
        print(query)
        combined_context = f"rag_context: {rag_context}\nfile_context:{file_context}\nUser Request: {query}"
        print("combined_context ===>", combined_context)
        print("ENTERED DIAGRAM GENERATION")
        

        diagram_code = DiagramGenerator.generate_diagram(combined_context)
        diagram_URL, file_Id = DiagramGenerator.execute_mermaid(diagram_code)
        blob_url = BlobService.upload_file(diagram_URL, file_Id)

        return{
            "type": "diagram",
            "content": blob_url,
        }


    # ─── Supervisor: LLM-driven tool decision + conditional RAG retrieval ────
    def supervisor(self, state: AgentState) -> AgentState:
        print("Supervisor invoked")

        user_q = state["messages"][-1].content
        conversation_history = ""
        if len(state["messages"]) > 1:
            history_msgs = state["messages"][:-1]
            for i, msg in enumerate(history_msgs):
                role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                conversation_history += f"{role}: {msg.content}\n\n"

        has_uploaded_pdf = bool(state.get("file_context"))

        # Improved prompt: explicitly describe available tools and state flags
        prompt = f"""
        You are an educational assistant with access to the following tools:
        - text_service: Generates detailed, context-aware text answers.
        - image_service: Creates images based on user queries and context.
        - pdf_service: Generates new, structured PDF documents (only if explicitly requested by the user, such as 'create a PDF', 'export as PDF', or similar).
        - diagram_service: Produces conceptual diagrams or visualizations from context and queries.
        - RAG (Retrieval-Augmented Generation): Retrieves relevant information from a knowledge base about ART USING GEN AI.

        Workflow state flags you can use:
        - has_uploaded_pdf: True if the user uploaded a file.
        - iteration_count: Number of workflow cycles so far.
        - skip_to_response: If True, skip tool execution and respond directly.
        - simple_response: If True, only a simple greeting/acknowledgement is needed.

        Previous conversation:
        {conversation_history if conversation_history else 'No previous conversation.'}

        Current user request: "{user_q}"

        File context: {'User has uploaded a PDF file.' if has_uploaded_pdf else 'No file uploaded.'}

        Instructions:
        1. Decide if this is a simple greeting (set simple_response and skip_to_response if so).
        2. Decide if you need to pull external context from RAG (rag_context). RAG contains information related to ART USING GEN AI.
        3. If the user query is related to art, generative AI, or could benefit from external knowledge, you SHOULD pull RAG context.
        4. Select which tools to use (text_service, image_service, pdf_service, diagram_service) and explain why.
        5. If the user uploaded a PDF, use its content for context.
        6. List any required components for quality check.
        7. Provide a brief reasoning for your decisions, referencing workflow state flags if relevant.
        8. Limit yourself to not use the image generation tool unless the user explicitly asks for an image.
        9. DO NOT select pdf_service unless the user explicitly asks to generate or export a new PDF, avoid using it otherwise.

        Return strictly valid JSON:
        {{
          "is_simple_greeting": <true|false>,
          "pull_context": <true|false>,
          "tools": ["text_service", "image_service", "pdf_service", "diagram_service"],
          "required_components": [ ... ],
          "reasoning": "..."
        }}
        """

        raw = llm.invoke([HumanMessage(content=prompt)]).content
        try:
            decision = json.loads(raw)
        except json.JSONDecodeError:
            decision = {
                "is_simple_greeting": False,
                "pull_context": False,
                "tools": ["text_service"],
                "required_components": [],
                "reasoning": "default to text response due to parsing error"
            }

        # Update state with all relevant flags and properties
        state["simple_response"] = decision.get("is_simple_greeting", False)
        state["skip_to_response"] = decision.get("is_simple_greeting", False)
        state["needed_tools"] = decision.get("tools", ["text_service"])
        state["required_components"] = decision.get("required_components", [])
        state["reasoning"] = decision.get("reasoning", "")
        state["has_uploaded_pdf"] = has_uploaded_pdf
        state["iteration_count"] = state.get("iteration_count", 0) + 1

        # Pull RAG context if needed
        if decision.get("pull_context", False):
            state["rag_context"] = RAG.get_context_from_index(user_q)
        else:
            state["rag_context"] = state.get("rag_context") or ""

        return state

    # ─── Execute selected tools ──────────────────────────────────────────────
    def execute_tools(self, state: AgentState) -> AgentState:
        results = state.get("tool_responses", {}) if state.get("iteration_count", 0) > 1 else {}
        pdf_generated = state.get("pdf_generated", False)

        logging.info(f"Executing tools. Iteration: {state.get('iteration_count', 0)}")

        for t in state.get("needed_tools", []):
            if t == "text_service":
                results[t] = self._generate_text(
                    state.get("rag_context"),
                    state.get("file_context"),
                    state["messages"]
                )
            elif t == "image_service":
                results[t] = self._generate_image(
                    state.get("rag_context"),
                    state.get("file_context"),
                    state["messages"][-1].content
                )
            elif t == "pdf_service" and not pdf_generated:
                results[t] = self._generate_pdf(
                    state.get("rag_context"),
                    state.get("file_context"),
                    state["messages"][-1].content
                )
                pdf_generated = True
            elif t == "diagram_service":
                results[t] = self._generate_diagram(
                    state.get("rag_context"),
                    state.get("file_context"),
                    state["messages"][-1].content
                )

        state["tool_responses"] = results
        state["pdf_generated"] = pdf_generated
        return state

    # ─── Quality check: simple yes/no ────────────────────────────────────────
    def quality_check(self, state: AgentState) -> AgentState:
        if state.get("iteration_count", 0) >= MAX_ITERATIONS:
            state["skip_to_response"] = True
            return state

        logging.info(f"Quality check iteration: {state.get('iteration_count', 0)}")

        responses = []
        for tool_name, r in state.get("tool_responses", {}).items():
            responses.append(f"{tool_name}: {r}")

        # Improved prompt: reference state and tool outputs
        prompt = f"""
        Review the following tool outputs and workflow state flags.

        User query: "{state['messages'][-1].content}"
        Tool responses: {responses}
        Required components: {state.get('required_components', [])}
        Flags: skip_to_response={state.get('skip_to_response', False)}, simple_response={state.get('simple_response', False)}, iteration_count={state.get('iteration_count', 0)}

        Decide if the response is complete and high quality. If not, specify which tools need refinement.

        Return JSON:
        {{
          "needs_refinement": <true|false>,
          "tools_to_refine": ["tool_name", ...],
          "reason": "..."
        }}
        """

        resp = llm.invoke([HumanMessage(content=prompt)]).content
        try:
            evaluation = json.loads(resp)
            if evaluation.get("needs_refinement", False):
                state["needed_tools"] = evaluation.get("tools_to_refine", [])
        except Exception:
            pass

        return state

    # ─── Format final response ───────────────────────────────────────────────
    def format_response(self, state: AgentState) -> dict:
        # Early exit path for simple queries
        if state.get("simple_response", False):
            simple_prompt = (
                f"Provide a brief, friendly response to this simple greeting: '{state['messages'][-1].content}'. "
                "Format your response using markdown for clarity and warmth."
                "Do not wrap response in triple backticks to avoid confusion with code blocks."
            )
            simple_response = llm.invoke([HumanMessage(content=simple_prompt)]).content
            
            updated_messages = state["messages"] + [AIMessage(content=simple_response)]
            return {
                "messages": updated_messages,
                "supervisor_reasoning": "Simple greeting detected, generated direct response."
            }
        
        user_query = state["messages"][-1].content
        has_uploaded_pdf = state.get("has_uploaded_pdf", False)
        tool_responses = state.get("tool_responses", {})
        
        # Build a context prompt with all available information
        context_sections = []
        
        if has_uploaded_pdf:
            context_sections.append(f"**User uploaded a PDF:**\n\n> {state.get('file_context', 'N/A')[:200]}...")
        
        if state.get("rag_context"):
            context_sections.append(f"**Retrieved context:**\n\n> {state.get('rag_context')[:200]}...")
        
        # Add tool responses with markdown enhancements
        for tool_name, r in tool_responses.items():
            if r["type"] == "text":
                context_sections.append(f"**Generated text content:**\n\n{r['content']}")
            elif r["type"] == "image" and r.get("content"):
                context_sections.append(f"**Generated image:**\n\n![Generated Image]({r['content']})\n\n[View Image]({r['content']})")
            elif r["type"] == "pdf" and r.get("content"):
                context_sections.append(f"**Generated PDF:**\n\n[📄 Download PDF]({r['content']})")
            elif r["type"] == "diagram" and r.get("content"):
                context_sections.append(f"**Generated diagram:**\n\n![Diagram]({r['content']})\n\n[View Diagram]({r['content']})")
        
        context = "\n\n---\n\n".join(context_sections)
        
        # Enhanced markdown prompt for LLM
        prompt = f"""
        You are an educational assistant. Generate a comprehensive, well-structured markdown response for the frontend.

        # 📝 User Query
        > {user_query}

        ## 📚 Available Information
        {context}

        ## 🧑‍🏫 Guidelines
        - Use markdown headers, bold, italics, blockquotes, and lists for clarity.
        - If a PDF was generated, mention it and include a download link.
        - If an image or diagram was generated, embed it using markdown and provide a link.
        - If the user uploaded a PDF, acknowledge this.
        - Use bullet points or numbered lists for steps or key points.
        - Make the response visually appealing and easy to scan.
        - Be conversational, informative, and complete.

        ### Example formatting:
        - **Bold** for important concepts
        - _Italics_ for emphasis
        - `inline code` for technical terms
        - > Blockquotes for context or highlights

        Respond in markdown only.
        """

        final_response = llm.invoke([SystemMessage(content=prompt)]).content

        # Ensure all images/links are present in the markdown if not already included
        for _, r in tool_responses.items():
            if r["type"] == "image" and r.get("content") and r["content"] not in final_response:
                final_response += f"\n\n![Generated Image]({r['content']})"
            if r["type"] == "diagram" and r.get("content") and r["content"] not in final_response:
                final_response += f"\n\n![Diagram]({r['content']})"
            if r["type"] == "pdf" and r.get("content") and r["content"] not in final_response:
                final_response += f"\n\n[📄 Download PDF]({r['content']})"

        updated_messages = state["messages"] + [AIMessage(content=final_response)]
        return {
            "messages": updated_messages,
            "supervisor_reasoning": state.get("reasoning")
        }

    # ─── Workflow graph ─────────────────────────────────────────────────────
    def _build_workflow(self):
        self.workflow.add_node("supervisor", self.supervisor)
        self.workflow.add_node("execute_tools", self.execute_tools)
        self.workflow.add_node("quality_check", self.quality_check)
        self.workflow.add_node("format_response", self.format_response)

        self.workflow.set_entry_point("supervisor")
        
        # Modified conditional edge to handle both simple responses and no tools needed
        self.workflow.add_conditional_edges("supervisor",
            lambda s: bool(s.get("needed_tools")) and not s.get("skip_to_response", False),
            {True: "execute_tools", False: "format_response"}
        )
        
        self.workflow.add_edge("execute_tools", "quality_check")
        self.workflow.add_conditional_edges("quality_check",
            lambda s: s.get("needs_refinement", False),
            {True: "execute_tools", False: "format_response"}
        )
        self.workflow.add_edge("format_response", END)

    def __call__(self, user_input: str, file_context: Optional[str] = None, message_history: Optional[List[Union[HumanMessage, AIMessage]]] = None):
        # Use provided message history or create a new one with just the current query
        if message_history:
            init_msgs = message_history
        else:
            init_msgs = [HumanMessage(content=user_input)]

        state: AgentState = {
            "messages": init_msgs,
            "rag_context": None,
            "file_context": file_context,  # Store uploaded file context separately
            "needed_tools": [],
            "tool_responses": {},
            "iteration_count": 0,
            "needs_refinement": None,
            "required_components": [],
            "reasoning": None,
            "pdf_generated": False,
            "has_uploaded_pdf": bool(file_context),  # Track if user uploaded a PDF
        }
        return self.chain.invoke(state)
