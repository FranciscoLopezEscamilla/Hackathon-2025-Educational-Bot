from langchain_openai.chat_models.azure import AzureChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
import os

llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
)

class MultiAgent:

    def generate_text(query: str) -> str:
        """Generate text based on user query"""
        return f"This is the text agent, input text: {query}"


    def generate_images(query: str) -> str:
        """Generate images based on user query"""
        return f"This is the image agent, input text: {query}"

    def generate_flow_charts(query: str) -> str:
        """Generate flow charts based on user query"""
        return f"This is the diagrams agent, input text: {query}"
    
    text_agent = create_react_agent(
        model=llm, 
        tools=[generate_text],
        name="text_creator",
        prompt="You're a smart assistant that generate funny text"
    )

    images_agent = create_react_agent(
        model=llm,
        tools=[generate_images],
        name="image_creator",
        prompt="You are a world class drawer that generates images and sketches like a pro"
    )

    diagrams_agent = create_react_agent(
        model=llm,
        tools=[generate_flow_charts],
        name="diagram_creator",
        prompt="You are a very smart assistant that can generate flow charts based on provided context."
    )

    workflow = create_supervisor(
        [text_agent, images_agent],
        model = llm,
        prompt= (
            "You are a team supervisor managing a images generator and a text expert generator. "
            "For text and documents queryes, use text_agent. "
            "For images related queries, use images_agent."
            "For diagram requests, use diagram_creator agent."
     )
    )

    app = workflow.compile()