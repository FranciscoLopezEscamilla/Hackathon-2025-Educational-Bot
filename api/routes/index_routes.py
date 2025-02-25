from services.index_service import Database
from fastapi.responses import FileResponse
from fastapi import APIRouter
import glob
import os

router = APIRouter(prefix="/index", tags=["Index"])

source_folder = os.path.join(os.getcwd(), "/index_documents")
files = glob.glob(source_folder, "/*")

@router.post("/create")
def create_index():
    documents = Database.extract_content_from_files(files)
    
    index_path =  Database.create_vector_store(documents)

    return index_path
    
    
   