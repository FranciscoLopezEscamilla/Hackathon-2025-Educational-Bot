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

# ─── Initialize LLM ────────────────────────────────────────────────────────
llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
)

class AgentState(TypedDict):
    messages: List[Union[SystemMessage, HumanMessage, AIMessage]]
    context: Optional[str]               # fetched RAG context (None until pulled)
    needed_tools: List[str]
    tool_responses: dict
    iteration_count: int
    needs_refinement: Optional[bool]
    required_components: List[str]
    reasoning: Optional[str]

class AgenticRAGWorkflow:
    def __init__(self):
        # Build workflow graph
        self.workflow = StateGraph(AgentState)
        self._build_workflow()
        self.chain = self.workflow.compile()

    # ─── Internal implementations ────────────────────────────────────────────
    def _generate_text(self, context: str, query: str) -> dict:
        instruction = (
            "Answer the user using the provided context. "
            "If context is empty or not needed, reply based only on general knowledge.\n\n"
            f"Context:\n{context}\n\nUser Query:\n{query}"
        )
        msgs = [SystemMessage(content=instruction), HumanMessage(content=query)]
        resp = llm.invoke(msgs).content
        return {"type": "text", "content": resp}

    def _generate_image(self, context: str, query: str) -> dict:
        prompt = (
            "Generate a detailed image prompt based on the context and user request.\n\n"
            f"Context:\n{context}\n\nRequest:\n{query}"
        )
        imgs = ImageGenerator.generate_images(prompt)
        return {"type": "image", "content": imgs}

    def _generate_pdf(self, context: str, query: str) -> dict:
        prompt = (
            "Generate detailed and structured content for a PDF document based on the following context and user request.\n\n"
            f"Context:\n{context}\n\nUser Request:\n{query}\n\n"
            "The content should be well-organized, informative, and suitable for inclusion in a PDF document."
        )
        pdf_content = llm.invoke([HumanMessage(content=prompt)]).content
        if not pdf_content.strip():
            pdf_content = "No meaningful content could be generated for the PDF."
        title = llm.invoke([HumanMessage(content=f"Create a concise title for the following content:\n{pdf_content}\n(Title should be brief and without quotes).")]).content
        logging.info(f"Generated PDF Title: {title}")
        logging.info(f"Generated PDF Content: {pdf_content}")
        pdf_file = DocumentGenerator.create(title=title, content=pdf_content)
        return {"type": "pdf", "content": pdf_file}

    # ─── Supervisor: LLM-driven tool decision + conditional RAG retrieval ────
    def supervisor(self, state: AgentState) -> AgentState:
        print("Supervisor invoked")
        user_q = state["messages"][-1].content
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

                **Important:** Always assume the tools exist. If the user requests a PDF or mentions "export as PDF", set needs_pdf to true. Do not say you cannot generate a PDF—delegate to the pdf_service tool.

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
        if "pdf" in user_q.lower() or "export as pdf" in user_q.lower():
            decision["needs_pdf"] = True
            decision["reasoning"] += " User explicitly requested a PDF."
        # Conditionally retrieve context
        if decision.get("pull_context"):
            state["context"] = RAG.get_context_from_index(user_q)
        else:
            state["context"] = state.get("context") or ""
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
        results = {}
        for t in state.get("needed_tools", []):
            if t == "text_service":
                results[t] = self._generate_text(state.get("context", ""), state["messages"][-1].content)
            elif t == "image_service":
                results[t] = self._generate_image(state.get("context", ""), state["messages"][-1].content)
            elif t == "pdf_service":
                results[t] = self._generate_pdf(state.get("context", ""), state["messages"][-1].content)
        state["tool_responses"] = results
        return state

    # ─── Quality check: simple yes/no ────────────────────────────────────────
    def quality_check(self, state: AgentState) -> AgentState:
        # Skip quality check if only a PDF was generated
        if "pdf_service" in state.get("needed_tools", []) and len(state.get("needed_tools", [])) == 1:
            pdf_response = state["tool_responses"].get("pdf_service", {})
            if not pdf_response.get("content") or "No meaningful content" in pdf_response.get("content", ""):
                logging.warning("PDF content is not meaningful. Marking for refinement.")
                state["needs_refinement"] = True
            else:
                logging.info("Skipping quality check for meaningful PDF generation.")
                state["needs_refinement"] = False
            return state

        combined = "\n\n".join(
            r["content"] if isinstance(r.get("content"), str) else str(r.get("content"))
            for r in state.get("tool_responses", {}).values()
            if r["type"] != "pdf"  # Exclude PDFs from the combined content
        )
        prompt = (
            f"Evaluate if the following response satisfies the user query '{state['messages'][-1].content}'.\n"
            f"Response:\n{combined}\n"
            "Answer 'yes' or 'no'."
        )
        resp = llm.invoke([HumanMessage(content=prompt)]).content.strip().lower()
        state["needs_refinement"] = not resp.startswith("yes")
        return state

    # ─── Format final response ───────────────────────────────────────────────
    def format_response(self, state: AgentState) -> dict:
        parts = []
        for r in state.get("tool_responses", {}).values():
            if r["type"] == "text": parts.append(r["content"])
            elif r["type"] == "image": parts.append(f"![image]({r['content']})")
            else: parts.append(f"[Download PDF]({r['content']})")
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
        if file_context:
            init_msgs.append(SystemMessage(content="### Uploaded Document Context\n" + file_context))
        init_msgs.append(HumanMessage(content=user_input))

        state: AgentState = {
            "messages": init_msgs,
            "context": None,
            "needed_tools": [],
            "tool_responses": {},
            "iteration_count": 0,
            "needs_refinement": None,
            "required_components": [],
            "reasoning": None,
        }
        return self.chain.invoke(state)
