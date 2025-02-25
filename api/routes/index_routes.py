from services.index_service import extract_content_from_file, create_vector_store
from fastapi.responses import FileResponse
from fastapi import APIRouter
import os

router = APIRouter(prefix="/index", tags=["Index"])

file_path = "C:/Users/p.a.rodriguez.canedo/Documents/Hackaton_2025/api/index_documents/UH Onboarding Manual.pdf"

@router.post("/create")
def create_index():
    documents = extract_content_from_file(file_path)
    
    index_path =  create_vector_store(documents)

    return index_path
    
    
   