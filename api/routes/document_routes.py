from models.document import Document
from api.services.document_service import DocumentGenerator
from fastapi.responses import FileResponse
from fastapi import APIRouter
import os

router = APIRouter(prefix="/document", tags=["Document"])

@router.post("/generate-pdf", response_class=FileResponse)
def generate_pdf(request: Document):
    file_path: str = DocumentGenerator.generate_pdf(request.title, request.content)
    
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

@router.post("/generate-ppt", response_class=FileResponse)
def generate_ppt(request: Document):
    file_path: str = DocumentGenerator.generate_ppt(request.title, request.content)
    
    if not os.path.exists(file_path):
        return {"error": "File not found"}
    
    return FileResponse(
        file_path,
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        filename=os.path.basename(file_path),
        headers={
            "Content-Disposition": f"attachment; filename={os.path.basename(file_path)}"
        }
    )