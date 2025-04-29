from langchain_community.docstore.in_memory import InMemoryDocstore
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from models.llm_clients import LlmUtils
from models.document import DocumentMetadata
import faiss
import os

dimension = 1536
embeddings = LlmUtils.embeddings_client()
parent_dir = os.getcwd() + "\\index"
index_path = parent_dir + "\\faiss_index"

azure_search_endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
azure_search_key = os.getenv('AZURE_SEARCH_KEY')
search_client = SearchClient(azure_search_endpoint, "hackaton-2025", AzureKeyCredential(azure_search_key))

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

        vector_store.save_local(os.path.join(parent_dir, "faiss_index"))
        return vector_store

    def query_index(query: str):
        print(index_path)
        vector_store = FAISS.load_local(index_path, embeddings, allow_dangerous_deserialization=True)
        retriever = vector_store.as_retriever()
        documents = retriever.invoke(query)
        result_string = "\n\n".join(doc.page_content for doc in documents)
        return result_string
    
    def get_indexed_files():
        
        
        document_count = search_client.get_document_count()

        files = []
        indexed_files = []

        for i in range(document_count):
            doc = search_client.get_document(i+1)
            doc_name = str(doc['source'].split("\\")[-1])
            if doc_name not in files:
                files.append(doc_name)
            
        for item in files:
            metadata_item=(DocumentMetadata(name=item, url=""))
            indexed_files.append(metadata_item)  
        
        return indexed_files
