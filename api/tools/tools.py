from langchain_core.tools import tool
from services.rag_service import RAG


@tool
def context_service_tool(self, query: str) -> str:
    """Retrieve RAG hits for the user’s query."""
    return RAG.get_context_from_index(query)

@tool
def text_service_tool(self, context: str, query: str) -> dict:
    """Answer using text, with clear instructions on which context to use."""
    return self._generate_text(context, query)

@tool
def image_service_tool(self, context: str, query: str) -> dict:
    """Produce images based on the merged context."""
    return self._generate_image(context, query)

@tool
def pdf_service_tool(self, context: str, query: str) -> dict:
    """Generate a PDF report if explicitly requested."""
    return self._generate_pdf(context, query)
