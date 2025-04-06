from langchain_openai.chat_models.azure import AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
from services.text_service import TextService
import os

llm = AzureChatOpenAI(
    openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_deployment=os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME"),
)

class MultiAgent:

    def generate_text(context: str, query: str) -> str:
        """Generates text based on user query and provided context"""

        prompt = """Your job is to respond user query based only in the provided context:
        HERE IS THE CONTEXT: {context}
        USER QUERY: {query}
        """

        template = PromptTemplate.from_template(prompt)
        chain = template | llm

        response = chain.invoke({"context": context, "query": query})

        return response

    def generate_images(query: str) -> str:
        """Generate images based on user query"""
        return f"This is the image agent, input text: {query}"

    text_agent = create_react_agent(
        model=llm, 
        tools=[generate_text],
        name="text_creator",
        prompt="You're a smart assistant that generate smart text"
    )

    images_agent = create_react_agent(
        model=llm,
        tools=[generate_images],
        name="image_creator",
        prompt="You are a world class drawer that generates images and sketches like a pro"
    )


    workflow = create_supervisor(
        [text_agent, images_agent],
        model = llm,
        prompt= (
            "You are a team supervisor managing a images generator and a text expert generator. "
            "For answering questions based on context, use text_agent. "
            "For images related queries, use images_agent."
     )
    )

    app = workflow.compile()