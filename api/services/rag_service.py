from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from models.llm_clients import LlmUtils
from langchain_core.output_parsers import StrOutputParser

import os

index_path =  os.path.normpath(os.getcwd()) + "/index/faiss_index"

llm = LlmUtils.llm_client

embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                azure_deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME')
            )

class RAG:

    def get_context_from_index(query:str, k:int = 3):
        """Use this to execute RAG. If the question is related to gen ai in art or music, using this tool retrieve the results."""
        print("Calling RAG...")
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()
        template = """Answer questions based only on the following context: 
        
        ### CONTEXT ###
        {context}
        
        Question: {question}
        
        If the context doesn't provide enough information to answer the question, say that you don't know.
        Do not respond with information outside the previous context."""

        prompt = PromptTemplate.from_template(template)

        chain = (
            {"context": retriever, "question": RunnablePassthrough()}
            | prompt
            | llm
            | StrOutputParser()
        )

        result = chain.invoke(query)
        return result