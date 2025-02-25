from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from models.llm_clients import LlmUtils
import os

dimension = 1536
embeddings = LlmUtils().embeddings_client()
full_path = "C:\\Users\\p.a.rodriguez.canedo\\Documents\\Hackaton_2025\\api\\index"
index_path = os.path.join(full_path, "faiss_index")

class DataBase():
    def extract_content_from_file(file_path):
        loader = PyPDFLoader(file_path)
        pages = loader.load()
        return pages

    def create_vector_store(documents):
        vector_store = FAISS.from_documents(documents, embeddings)
        vector_store.save_local(os.path.join(full_path, "faiss_index"))
        index_path = os.path.join(full_path, "faiss_index")
        return index_path

    def load_local_index(path):
        vector_store = FAISS.load_local(path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()
        return retriever

    def format_content(documents):
        result_string = "\n\n".join(doc.page_content for doc in documents)
        return result_string

    def query_index(query: str):
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()
        documents = retriever.invoke(query)
        results = format_content(documents)
        return results