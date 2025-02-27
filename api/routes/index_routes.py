from services.index_service import Database
from fastapi.responses import FileResponse
from fastapi import APIRouter
from models.query import Query
import glob
import os

router = APIRouter(prefix="/index", tags=["Index"])

source_folder = os.getcwd()+"\\index_documents"
files = glob.glob(source_folder + "/*")

@router.post("/create")
def create_index():
    documents = Database.extract_content_from_files(files)
    
    vector_store =  Database.create_vector_store(documents)
    
    return {f"Vector store has been created with {vector_store.index.ntotal} documents" }

@router.get("/query")
def query_index(request: Query):
    search_results = Database.query_index(request.query)
    return search_results 
    
   