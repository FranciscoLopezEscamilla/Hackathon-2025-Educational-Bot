from fastapi import APIRouter
from services.blob_service import BlobService
from models.document import DocumentMetadata, RampUpdDocuments
from services.index_service import Database

router = APIRouter(prefix="/storage_account")

@router.post("/blobs")
def get_blob_list() -> list:

    blob_metadata_list = BlobService.get_blobs_list()
    indexed_files_list = Database.get_indexed_files()

    full_list = RampUpdDocuments(generated_files = blob_metadata_list, indexed_files=indexed_files_list)
    return full_list
