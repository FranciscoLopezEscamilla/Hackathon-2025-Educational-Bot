from fastapi import APIRouter
from services.blob_service import BlobService
from models.document import DocumentMetadata

router = APIRouter(prefix="/storage_account")

@router.post("/blobs")
def get_blob_list() -> list:

    blob_metadata_list = BlobService.get_blobs_list()
    return blob_metadata_list
