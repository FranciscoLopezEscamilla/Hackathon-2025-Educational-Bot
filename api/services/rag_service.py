from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import FAISS

import os

index_path =  os.path.normpath(os.getcwd()) + "/index/faiss_index"


embeddings = AzureOpenAIEmbeddings(
                azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT'),
                api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                azure_deployment=os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMENT_NAME')
            )

class RAG:

    def get_context_from_index(query:str, k:int = 3):
        """This tool retrieves context from knowledge db based on user query"""
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)

        query_embeddings = embeddings.embed_query(query)
    
        results = vector_store.similarity_search_with_score_by_vector(embedding=query_embeddings, k=k)
        
        result_string = "\n\n".join(doc[0].page_content for doc in results)

        return result_string