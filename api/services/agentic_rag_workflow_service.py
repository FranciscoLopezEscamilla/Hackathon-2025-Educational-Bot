from langchain_openai.chat_models.azure import AzureChatOpenAI
from typing import TypedDict, List, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from services.rag_service import RAG
from services.image_service import ImageGenerator
from services.document_generator_service import DocumentGenerator
import os

# Initialize LLM client
llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
)

class AgentState(TypedDict):
    messages: List[HumanMessage | AIMessage]
    context: Optional[str]
    used_tools: List[str]
    needed_tools: List[str]
    supervisor_feedback: Optional[str]
    tool_responses: dict
    direct_response: Optional[str]
    iteration_count: int

class AgenticRAGWorkflow:
    def __init__(self):
        # Map tool names to their decorators for external invocation
        self.tools = {
            "context_service": self.context_service_tool,
            "text_service": self.text_service_tool,
            "image_service": self.image_service_tool,
            "pdf_service": self.pdf_service_tool,
        }
        # Build workflow graph
        self.workflow = StateGraph(AgentState)
        self._build_workflow()
        self.chain = self.workflow.compile()

    # External tool wrappers
    @tool
    def context_service_tool(self, query: str) -> str:
        """Retrieve relevant textual context for a user query from the RAG index."""
        return self._get_context(query)

    @tool
    def text_service_tool(self, context: str, query: str) -> dict:
        """Generate a plain-text answer based on context and user query."""
        return self._generate_text(context, query)

    @tool
    def image_service_tool(self, context: str, query: str) -> dict:
        """Produce image-generation prompts and fetch images based on context and query."""
        return self._generate_image(context, query)

    @tool
    def pdf_service_tool(self, context: str, query: str) -> dict:
        """Create a PDF document with content generated from the query and context."""
        return self._generate_pdf(context, query)

    # Internal implementations
    def _get_context(self, query: str) -> str:
        return RAG.get_context_from_index(query)

    def _generate_text(self, context: str, query: str) -> dict:
        response = llm.invoke([HumanMessage(content=query)]).content
        return {"type": "text", "content": response}

    def _generate_image(self, context: str, query: str) -> dict:
        prompt = f"Generate image prompt from context: {context} request: {query}"
        images = ImageGenerator.generate_images(prompt)
        return {"type": "image", "content": images}

    def _generate_pdf(self, context: str, query: str) -> dict:
        content = llm.invoke([HumanMessage(content=query)]).content
        title = llm.invoke([HumanMessage(content=f"Title for: {content}")]).content
        pdf_file = DocumentGenerator.create(title=title, content=content)
        return {"type": "pdf", "content": pdf_file}

    def _build_workflow(self):
        self.workflow.add_node("supervisor", self.supervisor)
        self.workflow.add_node("execute_tools", self.execute_tools)
        self.workflow.add_node("quality_check", self.quality_check)
        self.workflow.add_node("format_response", self.format_response)

        self.workflow.set_entry_point("supervisor")
        self.workflow.add_conditional_edges(
            "supervisor",
            self.route_tools,
            {"execute": "execute_tools", "respond": "format_response"}
        )
        self.workflow.add_edge("execute_tools", "quality_check")
        self.workflow.add_conditional_edges(
            "quality_check",
            lambda state: "execute" if state.get("needs_refinement") else "respond",
            {"execute": "execute_tools", "respond": "format_response"}
        )
        self.workflow.add_edge("format_response", END)

    def supervisor(self, state: AgentState) -> AgentState:
        user_query = state["messages"][-1].content
        # Direct answer if simple and second pass
        if len(user_query) < 100 and state["iteration_count"] >= 1:
            state["direct_response"] = llm.invoke([HumanMessage(content=user_query)]).content
            return state

        # Retrieve context directly
        state["context"] = self._get_context(user_query)

        # Heuristic tool selection
        needs = []
        if "image" in user_query.lower():
            needs.append("image_service")
        if "pdf" in user_query.lower():
            needs.append("pdf_service")
        if not needs:
            needs.append("text_service")

        state["needed_tools"] = needs
        state["supervisor_feedback"] = f"Using tools: {needs}"
        state["iteration_count"] += 1
        return state

    def execute_tools(self, state: AgentState) -> AgentState:
        results = {}
        for tool_name in state.get("needed_tools", []):
            # Call internal implementation to avoid wrapper schema
            if tool_name == "text_service":
                out = self._generate_text(state["context"], state["messages"][-1].content)
            elif tool_name == "image_service":
                out = self._generate_image(state["context"], state["messages"][-1].content)
            else:  # pdf_service
                out = self._generate_pdf(state["context"], state["messages"][-1].content)
            results[tool_name] = out
            state["used_tools"].append(tool_name)

        state["tool_responses"] = results
        return state

    def quality_check(self, state: AgentState) -> AgentState:
        state["needs_refinement"] = not bool(state.get("tool_responses"))
        return state

    def format_response(self, state: AgentState) -> dict:
        if state.get("direct_response"):
            return {"messages": [AIMessage(content=state["direct_response"]) ]}

        parts = []
        for resp in state.get("tool_responses", {}).values():
            if resp["type"] == "text":
                parts.append(resp["content"])
            elif resp["type"] == "image":
                parts.append(f"![image]({resp['content']})")
            else:
                parts.append(f"[PDF document]({resp['content']})")
        final = "\n\n".join(parts)
        return {"messages": [AIMessage(content=final)]}

    def route_tools(self, state: AgentState) -> str:
        return "respond" if state.get("direct_response") else "execute"

    def __call__(self, user_input: str):
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_input)],
            "context": None,
            "used_tools": [],
            "needed_tools": [],
            "supervisor_feedback": None,
            "tool_responses": {},
            "direct_response": None,
            "iteration_count": 0
        }
        return self.chain.invoke(initial_state)

# Example Usage
if __name__ == "__main__":
    agent = AgenticRAGWorkflow()
    resp = agent("Generate an overview of machine learning as PDF and visual examples")
    print(resp["messages"][-1].content)
