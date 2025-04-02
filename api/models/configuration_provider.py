import os

class ConfigurationProvider():
    def __init__(self):
        self.api_base = os.getenv('AZURE_OPENAI_ENDPOINT')
        self.api_key = os.getenv('AZURE_OPENAI_KEY')
        self.openai_api_version = os.getenv('AZURE_OPENAI_VERSION')
        self.chat_deployment_name = os.getenv('GPT_DEPLOYMENT_NAME')
        self.image_deployment_name = os.getenv('GPT_IMAGES_DEPLOYMENT_NAME')
        self.embeddings_deployment_name = os.getenv('EMBEDDINGS_DEPLOYMENT_NAME')
        self.llama_api_key = os.getenv('LLAMA_API_KEY')