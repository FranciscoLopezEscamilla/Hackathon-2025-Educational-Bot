from models.document import Document
from services.document_generator_service import DocumentGenerator
from fastapi.responses import FileResponse
from fastapi import APIRouter
import os

router = APIRouter(prefix="/document", tags=["Document"])

@router.post("/generate", response_class=FileResponse)
def create_document(request: Document):
    file_path: str = DocumentGenerator.create(request.title, request.content)
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(
        file_path,
        media_type="application/pdf",
        filename=os.path.basename(file_path),
        headers={
            "Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"
        }
    )