from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from services.text_service import TextService
from services.rag_service import RAG
from services.image_service import ImageGenerator
import os

llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
)

class MultiAgent:

    rag_tool = RAG.get_context_from_index
    text_tool = TextService.generate_text
    # image_tool = ImageGenerator.generate_images

    text_agent = create_react_agent(
        model=llm, 
        tools=[text_tool],
        name="text_agent",
        prompt="You are a smart assistant that helps people to train themselfs by generating content for them."
    )

    rag_agent = create_react_agent(
        model = llm,
        tools = [rag_tool],
        name = "rag_agent",
        prompt = "You are a smart agent that searchs for content in a vector db"
    )

    # image_agent = create_react_agent(
    #     model = llm,
    #     tools = [image_tool],
    #     name = "image_agent",
    #     prompt = "You are a smart agent that can generate helpful images for training documents."
    # )

    workflow = create_supervisor(
        [rag_agent, text_agent],
        model = llm,
        prompt= (
            "You are a smart agent that works as a router, your job is to decide which agent comes to play"
            "Agents list: rag_agent, text_agent, image_agent"
            "For queries related to GenAI in music, or GenAI in art, use the rag_agent."
            "For queries related to text generation, use the text_agent"
            
            "Agents description:" 
            "The rag_agent is able to search user queries in a vector database."
            "The text_agent can create new content for the user based on the rag_agent output (context)"
     )
    )

    app = workflow.compile()