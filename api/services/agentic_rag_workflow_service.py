from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_openai.embeddings.azure import AzureOpenAIEmbeddings
from langgraph.graph import StateGraph, END
from typing import TypedDict, List, Annotated, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.vectorstores import FAISS
import os
import json
from IPython.display import Image, display


index_path = os.path.normpath(os.getcwd()) + "/index/faiss_index"
print(index_path)

llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
)

def last_message_reducer(existing, update):
    return update 

class AgentState(TypedDict):
    messages: Annotated[List[HumanMessage | AIMessage], last_message_reducer]
    context: Optional[str]
    tool_responses: dict
    needs_refinement: bool
    required_components: List[str]
    needs_text: bool
    needs_images: bool
    needs_pdf: bool
    iteration_count: int

class AgenticRAGWorkflow:
    def __init__(self):
        print("init")
        # Optional: Initialize RAG components, such as embeddings and vector store.
        # self.embeddings = AzureOpenAIEmbeddings(
        #     azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
        #     api_key=os.getenv('AZURE_OPENAI_API_KEY'),
        #     azure_deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME')
        # )
        # self.vector_store = FAISS.load_local(
        #     index_path,
        #     self.embeddings,
        #     allow_dangerous_deserialization=True
        # )
        
        # Initialize tools
        self.tools = {
            "image_service": self.image_service,
            "pdf_service": self.pdf_service,
            "text_service": self.text_service
        }
        
        # Build workflow
        self.workflow = StateGraph(AgentState)
        self._build_workflow()

        self.chain = self.workflow.compile()
        try:
            display(Image(self.chain.get_graph().draw_mermaid_png()))
        except Exception:
            pass

    # Tool definitions
    @tool
    def image_service(context: str, query: str) -> dict:
        """Generate frontend-ready image response"""
        print(" =====> image_service")
        return {
            "type": "image",
            "content": "https://cute.imageofcats.com/img.jpg",
            "format": "markdown",
            "alt_text": "Generated AI image"
        }

    @tool
    def pdf_service(context: str, query: str) -> dict:
        """Generate frontend-ready PDF response"""
        print(" =====> pdf_service")
        return {
            "type": "pdf",
            "content": "https://www.exampledocument.com/genai_doc.pdf",
            "format": "markdown",
            "description": "Generated PDF document"
        }

    @tool
    def text_service(context: str, query: str) -> dict:
        """Generate formatted text content"""
        return {
            "type": "text",
            "content": "Generated text content based on context",
            "format": "markdown"
        }
    
    def check_quality_and_complexity(self, state: AgentState) -> str:
        state["iteration_count"] = state.get("iteration_count", 0) + 1
        max_iterations = 2 
        query_length = len(state["messages"][-1].content.strip())
        is_simple = query_length < 50
        if is_simple or state["iteration_count"] >= max_iterations:
            return "approve"
        else:
            return "refine"



    def _build_workflow(self):
        self.workflow.add_node("retrieve_context", self.retrieve_context)
        self.workflow.add_node("supervisor", self.supervisor)
        self.workflow.add_node("execute_tools", self.execute_tools)
        self.workflow.add_node("quality_check", self.quality_check)
        self.workflow.add_node("format_response", self.format_response)

        self.workflow.set_entry_point("retrieve_context")
        self.workflow.add_edge("retrieve_context", "supervisor")
        
        self.workflow.add_conditional_edges(
            "supervisor",
            self.route_tools,
            {"continue": "execute_tools", "respond": "format_response"}
        )
        
        self.workflow.add_edge("execute_tools", "quality_check")
        
        self.workflow.add_conditional_edges(
            "quality_check",
            self.check_quality_and_complexity,
            {"refine": "supervisor", "approve": "format_response"}
        )
        
        self.workflow.add_edge("format_response", END)

    def retrieve_context(self, state: AgentState):
        """Retrieve RAG context"""
        context = "This is a test Context"
        state["context"] = context
        return state

    def supervisor(self, state: AgentState):
        """Decide which tools to use"""
        prompt = f"""Analyze the user request and available context to determine needed tools.
        User Input: {state["messages"][-1].content}
        Context: {state.get("context", "")}

        Available Tools: image_service, pdf_service, text_service

        Return ONLY valid JSON in the following format (with no extra text):
        {{
            "needs_text": <true or false>,
            "needs_images": <true or false>,
            "needs_pdf": <true or false>,
            "required_components": [list of required component names],
            "reasoning": "<brief explanation>"
        }}
        """
        response = llm.invoke([HumanMessage(content=prompt)]).content
        supervisor_result = self._parse_supervisor_response(response)
        state.update(supervisor_result)
        return state
    

    def execute_tools(self, state: AgentState):
        """Execute selected tools using direct invocation"""
        results = {}
        if state.get("needs_text"):
            print("Invoking text_service")
            results["text"] = self.text_service.invoke({
                "context": state["context"],
                "query": state["messages"][-1].content
            })
        if state.get("needs_images"):
            print("Invoking image_service")
            results["image"] = self.image_service.invoke({
                "context": state["context"],
                "query": state["messages"][-1].content
            })
        if state.get("needs_pdf"):
            print("Invoking pdf_service")
            results["pdf"] = self.pdf_service.invoke({
                "context": state["context"],
                "query": state["messages"][-1].content
            })
        
        state["tool_responses"] = results
        return state

    def quality_check(self, state: AgentState):
        """Self-reflection quality grader"""
        prompt = f"""Evaluate if responses fully address the user query.
        User Query: {state["messages"][-1].content}
        Context: {state.get("context", "")}
        Tool Outputs: {json.dumps(state["tool_responses"], indent=2)}
        Required Components: {state.get("required_components", [])}

        Return ONLY valid JSON in the following format:
        {{
            "approved": <true or false>,
            "missing_components": [list of missing element types],
            "feedback": "<improvement suggestions>"
        }}
        """
        response = llm.invoke([HumanMessage(content=prompt)]).content
        quality_result = self._parse_quality_response(response)
        state.update(quality_result)
        return state

    def format_response(self, state: AgentState):
        """Generate frontend-ready formatted response and trim message history"""
        prompt = f"""Compile final response with proper formatting:
        Components: {json.dumps(state.get("tool_responses", {}), indent=2)}

        Formatting Rules:
        - Images: ![alt](url)
        - PDFs: [description](url)
        - Text: Clear paragraphs with markdown formatting
        - Include all generated components

        if response used pdf or image generation, exclude details from response
        """

        # User Query: {state["messages"][-1].content}
        # Context: {state.get("context", "")}

        formatted = llm.invoke([HumanMessage(content=prompt)]).content
        # state["messages"] = state["messages"][-1:]
        return {"messages": [AIMessage(content=formatted)], "needs_refinement": False}

    def _parse_supervisor_response(self, response: str) -> dict:
        try:
            decision = json.loads(response)
            return {
                "needs_text": bool(decision.get("needs_text", False)),
                "needs_images": bool(decision.get("needs_images", False)),
                "needs_pdf": bool(decision.get("needs_pdf", False)),
                "required_components": decision.get("required_components", []),
            }
        except json.JSONDecodeError:
            print("JSON decoding error for supervisor response:", response)
            return {"needs_text": True, "needs_images": False, "needs_pdf": False, "required_components": []}

    def _parse_quality_response(self, response: str) -> dict:
        try:
            evaluation = json.loads(response)
            return {
                "needs_refinement": not evaluation.get("approved", False),
                "required_components": evaluation.get("missing_components", []),
            }
        except json.JSONDecodeError:
            return {"needs_refinement": True, "required_components": []}

    def route_tools(self, state: AgentState):
        if any([state.get("needs_text"), state.get("needs_images"), state.get("needs_pdf")]):
            return "continue"
        return "respond"

    def check_quality(self, state: AgentState):
        if state.get("needs_refinement", False):
            return "refine"
        return "approve"

    def __call__(self, user_input: str):
        initial_state: AgentState = {
            "messages": [HumanMessage(content=user_input)],
            "context": None,
            "tool_responses": {},
            "needs_refinement": False,
            "required_components": [],
            "needs_text": False,
            "needs_images": False,
            "needs_pdf": False,
            "iteration_count": 0
        }
        return self.chain.invoke(initial_state)

# Usage example
if __name__ == "__main__":
    workflow = AgenticRAGWorkflow()
    response = workflow("Explain quantum computing with visual examples")
    print(response["messages"][-1].content)
