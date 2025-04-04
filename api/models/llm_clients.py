from pydantic import BaseModel
from langchain_openai import AzureOpenAIEmbeddings
from openai import AzureOpenAI
from dotenv import load_dotenv
import os
load_dotenv()

api_key = os.getenv('AZURE_OPENAI_API_KEY')
api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
version = os.getenv('AZURE_OPENAI_API_VERSION')
embeddings_model = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME')

class LlmUtils:
    def __init__():
        pass

    def llm_client():
            client = AzureOpenAI(
                azure_endpoint=api_base,
                api_key=api_key,
                api_version=version
            )
            return client
        
    def embeddings_client():
            embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=api_base,
                api_key=api_key,
                azure_deployment=embeddings_model
            )
            return embeddings