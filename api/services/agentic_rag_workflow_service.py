from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from services.rag_service import RAG
from services.image_service import ImageGenerator
from services.document_generator_service import DocumentGenerator
from typing import TypedDict, List, Optional, Union
import os
import json
import logging
from services.blob_service import BlobService
from services.diagram_service import DiagramGenerator
from services.document_service import PptGenerator
from models.document import DocumentRequest, DocumentContent, TextItem, ImageItem

logging.basicConfig(level=logging.INFO)

MAX_ITERATIONS = 3  # Maximum number of refinement iterations allowed

# ─── Initialize LLM ────────────────────────────────────────────────────────
llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
)

class AgentState(TypedDict):
    messages: List[Union[SystemMessage, HumanMessage, AIMessage]]
    rag_context: Optional[str]  # Renamed from just "context" to be more specific
    file_context: Optional[str]  # Separate context from uploaded files
    needed_tools: List[str]
    tool_responses: dict
    iteration_count: int
    needs_refinement: Optional[bool]
    required_components: List[str]
    reasoning: Optional[str]
    pdf_generated: Optional[bool]
    has_uploaded_pdf: Optional[bool]  # Track if user uploaded PDFs

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
        combined_context = f"{rag_context}\n{file_context}"
        print("combined_context ===>", combined_context)
        print("ENTERED DIAGRAM GENERATION")
        

        diagram_code = DiagramGenerator.generate_diagram(combined_context)
        diagram_URL, file_Id = DiagramGenerator.execute_mermaid(diagram_code)
        blob_url = BlobService.upload_file(diagram_URL, file_Id)

        return{
            "type": "diagram",
            "content": blob_url,
        }

    def _generate_powerpoint(self, rag_context: str, file_context: str, query: str) -> dict:
        print("ENTERED PPT GENERATION")

        
        sample_request = DocumentRequest(
            title="Demo Document",
            pages=[
                DocumentContent(
                    text_items=[
                        TextItem(type="header", content="Welcome"),
                        TextItem(type="paragraph", content="This is a sample slide."),
                    ],
                    images=[
                        #ImageItem(path="sample_image.png")
                    ]
                ),

                DocumentContent(
                    text_items=[
                        TextItem(type="subheader", content="Second Slide"),
                        TextItem(type="paragraph", content="Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus luctus urna sed urna ultricies ac tempor dui sagittis. In condimentum facilisis porta.\nFusce sed felis eget velit aliquet faucibus. Praesent ac massa at ligula laoreet iaculis."),
                    ],
                    images=[]
                )
            ]
        )

        output_path = "../output"

        ppt_file = PptGenerator.generate_ppt(sample_request, output_path)
        blob_url = BlobService.upload_file(output_path, "demo.pptx")
        return {"type": "pptx", "content": blob_url}

    # ─── Supervisor: LLM-driven tool decision + conditional RAG retrieval ────
    def supervisor(self, state: AgentState) -> AgentState:
        print("Supervisor invoked")
        
        # Get the last user message (current query)
        user_q = state["messages"][-1].content
        
        # Extract conversation history for context
        conversation_history = ""
        if len(state["messages"]) > 1:
            # Format previous messages for the LLM prompt
            history_msgs = state["messages"][:-1]  # All except current query
            for i, msg in enumerate(history_msgs):
                role = "User" if isinstance(msg, HumanMessage) else "Assistant"
                conversation_history += f"{role}: {msg.content}\n\n"
        
        # Check if user uploaded a PDF
        has_uploaded_pdf = bool(state.get("file_context"))
        
        # Let the LLM make decisions with awareness of conversation history
        prompt = f"""
        Analyze the user request in the context of the conversation history and decide:
        1. Whether this is a simple greeting (yes/no).
        2. Whether to pull external context from RAG (yes/no). contents within RAG are related to Gen AI in art or music using Python.
        3. Which tools to invoke (text_service/image_service/pdf_service/diagram_service/powerpoint_service).
        4. Any required components for final quality check.
        5. A brief reasoning for your decisions.

        {{'Previous conversation:\n' + conversation_history if conversation_history else 'No previous conversation.'}}
        
        Current user request: "{user_q}"

        {{'User has uploaded a PDF file. ' if has_uploaded_pdf else ''}}
        {{'If the user is asking questions about their uploaded PDF, you should NOT generate a new PDF but answer with text_service.' if has_uploaded_pdf else ''}}
        
        **Important:** Only select pdf_service if the user explicitly requests to create/generate/export a NEW PDF.
        If the user is asking ABOUT PDF content or has questions about their uploaded PDF, use text_service instead.

        **Important:** You can create diagrams using the diagram_service.
        If the user is asking for a diagram, use diagram_service instead of image_service.


        Return strictly valid JSON:
        {{
        "is_simple_greeting": <true|false>,
        "pull_context": <true|false>,
        "tools": ["text_service", "image_service", "pdf_service", "diagram_service","powerpoint_service],
        "required_components": [ ... ],
        "reasoning": "..."
        }}
        """
        
        raw = llm.invoke([HumanMessage(content=prompt)]).content
        try:
            decision = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback defaults
            decision = {
                "is_simple_greeting": False,
                "pull_context": False,
                "tools": ["text_service"],
                "required_components": [],
                "reasoning": "default to text response due to parsing error"
            }
        
        # Handle simple greeting flow
        if decision.get("is_simple_greeting", False):
            state["skip_to_response"] = True
            state["simple_response"] = True
            state["needed_tools"] = []
            state["has_uploaded_pdf"] = has_uploaded_pdf
            return state
                
        # Conditionally retrieve context
        state["rag_context"] = RAG.get_context_from_index(user_q)
        # if decision.get("pull_context"):
        #     print("Retrieving context from RAG")
        # else:
        #     state["rag_context"] = state.get("rag_context") or ""
        
        # Store state information
        state["has_uploaded_pdf"] = has_uploaded_pdf
        state["needed_tools"] = decision.get("tools", ["text_service"])
        state["required_components"] = decision.get("required_components", [])
        state["reasoning"] = decision.get("reasoning", "")
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        return state

    # ─── Execute selected tools ──────────────────────────────────────────────
    def execute_tools(self, state: AgentState) -> AgentState:
        # Initialize with existing results if in refinement
        if state.get("iteration_count", 0) > 1:
            results = state.get("tool_responses", {})
            pdf_generated = state.get("pdf_generated", False)
        else:
            results = {}
            pdf_generated = False
            
        logging.info(f"Executing tools. Iteration: {state.get('iteration_count', 0)}")
        
        # Execute only needed tools that haven't been executed yet (or need refinement)
        for t in state.get("needed_tools", []):
            if t == "text_service":
                results[t] = self._generate_text(
                    state.get("rag_context"), 
                    state.get("file_context"), 
                    state["messages"]  # Pass the full message history
                )
            elif t == "image_service":
                results[t] = self._generate_image(
                    state.get("rag_context"), 
                    state.get("file_context"), 
                    state["messages"][-1].content  # Use just the current query for image generation
                )
            elif t == "pdf_service" and not pdf_generated:
                results[t] = self._generate_pdf(
                    state.get("rag_context"), 
                    state.get("file_context"), 
                    state["messages"][-1].content  # Use just the current query for PDF generation
                )
                pdf_generated = True
            elif t == "diagram_service":
                results[t] = self._generate_diagram(
                    state.get("rag_context"), 
                    state.get("file_context"), 
                    state["messages"][-1].content  # Use just the current query for diagram generation
                )
                
            elif t == "powerpoint_service":
                results[t] = self._generate_powerpoint(
                    state.get("rag_context"), 
                    state.get("file_context"), 
                    state["messages"][-1].content  # Use just the current query for powerpoint generation
                )


        state["tool_responses"] = results
        state["pdf_generated"] = pdf_generated
        return state

    # ─── Quality check: simple yes/no ────────────────────────────────────────
    def quality_check(self, state: AgentState) -> AgentState:
        # Enforce maximum iteration limit
        if state.get("iteration_count", 0) >= MAX_ITERATIONS:
            logging.warning(f"Maximum iteration count ({MAX_ITERATIONS}) reached. Proceeding to final response.")
            state["needs_refinement"] = False
            return state
            
        logging.info(f"Quality check iteration: {state.get('iteration_count', 0)}")
        
        # Collect responses
        responses = []
        for tool_name, r in state.get("tool_responses", {}).items():
            if r["type"] == "text":
                responses.append(f"Text response: {r.get('content', '')}")
            elif r["type"] == "image":
                responses.append(f"Image generated: {r.get('content', '(image url)')}")
            elif r["type"] == "pdf":
                responses.append(f"PDF generated: {r.get('content', '(pdf url)')}")
            elif r["type"] == "diagram":
                responses.append(f"Diagram generated: {r.get('content', '(diagram url)')}")
            elif r["type"] == "powerpoint":
                responses.append(f"Powerpoint generated: {r.get('content', '(powerpoint url)')}")
        
        combined_responses = "\n\n".join(responses)
        
        # Let the LLM decide if refinement is needed
        prompt = f"""
        Evaluate if the following response sufficiently addresses the user query:
        
        USER QUERY: "{state['messages'][-1].content}"
        
        CURRENT RESPONSE:
        {combined_responses}
        
        Answer with JSON:
        {{
            "needs_refinement": <true|false>,
            "reason": "<brief explanation>",
            "tools_to_refine": ["<tool_name>", ...] // Only include if needs_refinement is true
        }}
        """
        
        resp = llm.invoke([HumanMessage(content=prompt)]).content
        
        try:
            evaluation = json.loads(resp)
            state["needs_refinement"] = evaluation.get("needs_refinement", False)
            
            # If refinement is needed, specify which tools to rerun
            if state["needs_refinement"] and "tools_to_refine" in evaluation:
                state["needed_tools"] = evaluation["tools_to_refine"]
        except json.JSONDecodeError:
            # Default to not needing refinement if parsing fails
            state["needs_refinement"] = False
            
        return state

    # ─── Format final response ───────────────────────────────────────────────
    def format_response(self, state: AgentState) -> dict:
        # Early exit path for simple queries
        if state.get("simple_response", False):
            simple_prompt = f"Provide a brief, friendly response to this simple greeting: '{state['messages'][-1].content}'"
            simple_response = llm.invoke([HumanMessage(content=simple_prompt)]).content
            
            # Create new message list with history plus new response
            updated_messages = state["messages"] + [AIMessage(content=simple_response)]
            
            return {
                "messages": updated_messages,  # Return full message history
                "supervisor_reasoning": "Simple greeting detected, generated direct response."
            }
        
        # Collect all available content
        user_query = state["messages"][-1].content
        has_uploaded_pdf = state.get("has_uploaded_pdf", False)
        tool_responses = state.get("tool_responses", {})
        
        # Build a context prompt with all available information
        context_sections = []
        
        if has_uploaded_pdf:
            context_sections.append(f"User uploaded a PDF with content: {state.get('file_context', 'N/A')[:200]}...")
        
        if state.get("rag_context"):
            context_sections.append(f"Retrieved context: {state.get('rag_context')[:200]}...")
        
        # Add tool responses
        for tool_name, r in tool_responses.items():
            if r["type"] == "text":
                context_sections.append(f"Generated text content: {r['content']}")
            elif r["type"] == "image" and r.get("content"):
                context_sections.append(f"Generated image URL: {r['content']}")
            elif r["type"] == "pdf" and r.get("content"):
                context_sections.append(f"Generated PDF URL: {r['content']}")
            elif r["type"] == "diagram" and r.get("content"):
                context_sections.append(f"Generated diagram URL: {r['content']}")
            elif r["type"] == "powerpoint" and r.get("content"):
                context_sections.append(f"Generated powerpoint URL: {r['content']}")
        
        context = "\n\n".join(context_sections)
        
        # Let the LLM construct the final response
        prompt = f"""
        Generate a comprehensive response to the user that integrates all available information.
        Use markdown formatting appropriately.
        
        USER QUERY: {user_query}
        
        AVAILABLE INFORMATION:
        {context}
        
        GUIDELINES:
        1. If a PDF was generated, explicitly mention it and include the download link.
        2. If an image was generated, reference it naturally and include the image in markdown format.
        3. Be conversational yet informative and complete.
        4. If the user uploaded a PDF that you analyzed, acknowledge this fact.
        """
        
        final_response = llm.invoke([SystemMessage(content=prompt)]).content
        
        # Ensure image is properly included if it exists but not in the response
        for _, r in tool_responses.items():
            if r["type"] == "image" and r.get("content") and "![" not in final_response and r["content"] not in final_response:
                final_response = f"{final_response}\n\n![Generated Image]({r['content']})"
        
        # Create new message list with history plus new response
        updated_messages = state["messages"] + [AIMessage(content=final_response)]
        
        return {
            "messages": updated_messages,  # Return full message history
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
