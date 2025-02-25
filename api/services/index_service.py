from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from models.llm_clients import LlmUtils
import faiss
import os

dimension = 1536
embeddings = LlmUtils().embeddings_client()
parend_dir = os.path.join(os.getcwd(), "index")
index_path = os.path.join(parend_dir, "faiss_index")

class Database():

    def extract_content_from_files(files):
        documents = []
        for file in files:
            loader = PyPDFLoader(file)
            pages = loader.load()
            documents.append(pages)
        return documents

    def create_vector_store(documents):

        index = faiss.IndexFlatL2(dimension)

        vector_store = FAISS(
            embedding_function=embeddings,
            index=index,
            docstore= InMemoryDocstore(),
            index_to_docstore_id={}
        )

        for document in documents:
            vector_store.add_documents(document)

        vector_store.save_local(os.path.join(parend_dir, "faiss_index"))
        index_path = os.path.join(parend_dir, "faiss_index")
        return index_path

    def query_index(query: str):
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()
        documents = retriever.invoke(query)
        result_string = "\n\n".join(doc.page_content for doc in documents)
        return result_string