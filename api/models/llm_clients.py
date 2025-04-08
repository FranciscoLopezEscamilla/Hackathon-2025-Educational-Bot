from langchain_openai import AzureOpenAIEmbeddings
from openai import AzureOpenAI
from langchain_openai.chat_models.azure import AzureChatOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

openai_api_key = os.getenv('AZURE_OPENAI_API_KEY')
openai_api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
openai_api_version = os.getenv('AZURE_OPENAI_API_VERSION')
embeddings_model = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME')
gpt_model = os.getenv("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME")
dalle_model = os.getenv("GPT_IMAGES_DEPLOYMENT_NAME")

class LlmUtils:
    
    client = AzureOpenAI(azure_endpoint=openai_api_base, api_key=openai_api_key, api_version=openai_api_version)

    def llm_client():
            llm = AzureChatOpenAI(
                openai_api_version=openai_api_version,
                azure_deployment=gpt_model,
            )
            return llm
        
    def embeddings_client():
            embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=openai_api_base,
                api_key=openai_api_key,
                azure_deployment=embeddings_model
            )
            return embeddings