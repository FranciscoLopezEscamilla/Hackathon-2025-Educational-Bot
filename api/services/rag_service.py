from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from models.llm_clients import LlmUtils
from langchain_core.output_parsers import StrOutputParser
from azure.search.documents.models import VectorizedQuery
from openai import AzureOpenAI
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

import os

index_path =  os.path.normpath(os.getcwd()) + "/index/faiss_index"
model = os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME')
azure_search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
azure_search_key = os.getenv('AZURE_SEARCH_KEY')

search_client = SearchClient(azure_search_endpoint, "hackaton-2025", AzureKeyCredential(azure_search_key))

client = AzureOpenAI(
  api_key = os.getenv("AZURE_OPENAI_API_KEY"),  
  api_version = "2024-02-01",
  azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
)

llm = LlmUtils.llm

embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                azure_deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME')
            )

class RAG:

    def get_context_from_index(query:str):
        """Use this to execute RAG. If the question is related to gen ai in art or music, using this tool retrieve the results."""
        print("Calling RAG...")
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()
        template = """return the most relevant information from the context below to answer the question.
        
        ### CONTEXT ###
        {context}
        
        Question: {question}
        """

        prompt = PromptTemplate.from_template(template)

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        result = chain.invoke(query)
        print("rag_context", result)
        return result
    
    def get_context_from_aisearch(query:str):
        print("Calling AI Search RAG")
        embedded_query = client.embeddings.create(input = [query], model=model).data[0].embedding
        vector_query = VectorizedQuery(vector=embedded_query, k_nearest_neighbors=5, fields="content_vector")
        response = search_client.search(search_text = None, vector_queries=[vector_query])

        full_response = ""
        for r in response:
            full_response += str(r['content']) + '\n\n'
        
        return full_response
