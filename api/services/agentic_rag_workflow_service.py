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

logging.basicConfig(level=logging.INFO)

# Add this constant at the top of your file, after imports
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
    def _generate_text(self, rag_context: str, file_context: str, query: str) -> dict:
        instruction = (
            "Answer the user using the provided contexts. "
            "If a file was uploaded by the user, prioritize that information. "
            "If contexts are empty or not needed, reply based only on general knowledge.\n\n"
        )
        
        if file_context:
            instruction += f"Uploaded File Context:\n{file_context}\n\n"
        
        if rag_context:
            instruction += f"Retrieved Context:\n{rag_context}\n\n"
        
        instruction += f"User Query:\n{query}"
        
        msgs = [SystemMessage(content=instruction), HumanMessage(content=query)]
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
            
        logging.info(f"Generated PDF Title: {title}")
        pdf_file = DocumentGenerator.create(title=title, content=content)
        return {"type": "pdf", "content": pdf_file}

    # ─── Supervisor: LLM-driven tool decision + conditional RAG retrieval ────
    def supervisor(self, state: AgentState) -> AgentState:
        print("Supervisor invoked")
        user_q = state["messages"][-1].content
        
        # Check if user uploaded a PDF
        has_uploaded_pdf = bool(state.get("file_context"))
        
        # Prompt LLM to decide which tools to run
        prompt = f"""
                Analyze the user request and decide:
                1. Whether to pull external context from RAG (pull_context: true/false).
                2. Which tools to invoke: needs_text, needs_images, needs_pdf.
                3. Any required components for final quality check.
                4. A brief reasoning.

                Available tools:
                - text_service (for text replies)
                - image_service (for image generation)
                - pdf_service (for PDF export)

                {'User has uploaded a PDF file. ' if has_uploaded_pdf else ''}
                {'If the user is asking questions about their uploaded PDF, you should NOT generate a new PDF but answer with text_service.' if has_uploaded_pdf else ''}
                
                **Important:** Always assume the tools exist. Only set needs_pdf to true if the user explicitly requests to create/generate/export a NEW PDF.
                If the user is asking ABOUT PDF content or has questions about their uploaded PDF, use text_service instead.

                Return strictly valid JSON:
                {{
                "pull_context": <true|false>,
                "needs_text": <true|false>,
                "needs_images": <true|false>,
                "needs_pdf": <true|false>,
                "required_components": [ ... ],
                "reasoning": "..."
                }}

                User Query: {user_q}
                """
        raw = llm.invoke([HumanMessage(content=prompt)]).content
        try:
            decision = json.loads(raw)
        except json.JSONDecodeError:
            # Fallback defaults
            decision = {
                "pull_context": False,
                "needs_text": True,
                "needs_images": False,
                "needs_pdf": False,
                "required_components": [],
                "reasoning": "default to text"
            }
        
        # More careful checking for PDF generation intent
        pdf_keywords = ["generate pdf", "create pdf", "make pdf", "export as pdf", "export to pdf", "produce pdf", "compile pdf"]
        explicitly_wants_pdf = any(keyword in user_q.lower() for keyword in pdf_keywords)
        
        if explicitly_wants_pdf:
            decision["needs_pdf"] = True
            decision["reasoning"] += " User explicitly requested a PDF generation."
        elif has_uploaded_pdf and "pdf" in user_q.lower():
            # If user uploaded a PDF and mentions PDF but not explicitly requesting generation
            decision["needs_pdf"] = False
            decision["needs_text"] = True
            decision["reasoning"] += " User is asking about their uploaded PDF, responding with text."
            
        # Conditionally retrieve context
        if decision.get("pull_context"):
            state["rag_context"] = RAG.get_context_from_index(user_q)
        else:
            state["rag_context"] = state.get("rag_context") or ""
            
        # Store whether user uploaded a PDF
        state["has_uploaded_pdf"] = has_uploaded_pdf
        
        # Determine needed tools
        tools = []
        if decision.get("needs_text"): tools.append("text_service")
        if decision.get("needs_images"): tools.append("image_service")
        if decision.get("needs_pdf"): tools.append("pdf_service")
        state["needed_tools"] = tools
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
                    state.get("rag_context", ""), 
                    state.get("file_context", ""), 
                    state["messages"][-1].content
                )
            elif t == "image_service":
                results[t] = self._generate_image(
                    state.get("rag_context", ""), 
                    state.get("file_context", ""), 
                    state["messages"][-1].content
                )
            elif t == "pdf_service" and not pdf_generated:
                results[t] = self._generate_pdf(
                    state.get("rag_context", ""), 
                    state.get("file_context", ""), 
                    state["messages"][-1].content
                )
                pdf_generated = True
                
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
        
        # Skip quality check if PDF was generated (assume it's good enough)
        if state.get("pdf_generated", False):
            pdf_response = state["tool_responses"].get("pdf_service", {})
            if not pdf_response.get("content"):
                logging.warning("PDF generation failed. Marking as not needing refinement to avoid loops.")
            state["needs_refinement"] = False
            return state

        # Only perform quality check on non-PDF responses
        combined = "\n\n".join(
            r["content"] if isinstance(r.get("content"), str) else str(r.get("content"))
            for r in state.get("tool_responses", {}).values()
            if r["type"] != "pdf"  # Exclude PDFs from the combined content
        )
        
        if not combined.strip():
            # If there's no content to check, don't refine
            state["needs_refinement"] = False
            return state
            
        prompt = (
            f"Evaluate if the following response satisfies the user query '{state['messages'][-1].content}'.\n"
            f"Response:\n{combined}\n"
            "Answer with only 'yes' or 'no'."
        )
        resp = llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
        state["needs_refinement"] = not resp.startswith("yes")
        return state

    # ─── Format final response ───────────────────────────────────────────────
    def format_response(self, state: AgentState) -> dict:
        parts = []
        for r in state.get("tool_responses", {}).values():
            if r["type"] == "text":
                parts.append(r["content"])
            elif r["type"] == "image":
                parts.append(f"![image]({r['content']})")
            elif r["type"] == "pdf":
                parts.append(f"[Download PDF]({r['content']})")

        # Contextually aware responses
        if state.get("pdf_generated", False):
            parts.append("I've generated a new PDF document based on your request. You can download it using the link above.")
        elif state.get("has_uploaded_pdf", False) and "pdf_service" not in state.get("needed_tools", []):
            # The user uploaded a PDF but we didn't generate a new one
            if not any(parts):  # If no parts exist yet
                parts.append("I've analyzed the PDF you uploaded. How else can I help with this document?")

        content = "\n\n".join(parts)
        # Return messages and keep reasoning separate
        return {
            "messages": [AIMessage(content=content)],
            "supervisor_reasoning": state.get("reasoning")
        }

    # ─── Workflow graph ─────────────────────────────────────────────────────
    def _build_workflow(self):
        self.workflow.add_node("supervisor", self.supervisor)
        self.workflow.add_node("execute_tools", self.execute_tools)
        self.workflow.add_node("quality_check", self.quality_check)
        self.workflow.add_node("format_response", self.format_response)

        self.workflow.set_entry_point("supervisor")
        self.workflow.add_conditional_edges("supervisor",
            lambda s: bool(s.get("needed_tools")),
            {True: "execute_tools", False: "format_response"}
        )
        self.workflow.add_edge("execute_tools", "quality_check")
        self.workflow.add_conditional_edges("quality_check",
            lambda s: s.get("needs_refinement", False),
            {True: "execute_tools", False: "format_response"}
        )
        self.workflow.add_edge("format_response", END)

    def __call__(self, user_input: str, file_context: Optional[str] = None):
        init_msgs: List[Union[SystemMessage, HumanMessage]] = []
        init_msgs.append(HumanMessage(content=user_input))

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
