from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from models.llm_clients import LlmUtils
import os

dimension = 1536

llm_utils = LlmUtils()
embeddings = llm_utils.embeddings_client()
full_path = "C:\\Users\\p.a.rodriguez.canedo\\Documents\\Hackaton_2025\\api\\index"

def extract_content_from_file(file_path):
    loader = PyPDFLoader(file_path)
    pages = loader.load()
    return pages

def create_vector_store(documents):
    vector_store = FAISS.from_documents(documents, embeddings)
    vector_store.save_local(os.path.join(full_path, "faiss_index"))
    index_path = os.path.join(full_path, "faiss_index")
    return index_path