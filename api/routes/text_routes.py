from fastapi import APIRouter, HTTPException
from services.text_service import TextGenerator
from services.index_service import Database
from models.query import Query

router = APIRouter(prefix="/text", tags=["Text"])

@router.post("/generate")
def generate_text(request: Query):
    
    context_from_index = Database.query_index(request.query)

    gen_text : str = TextGenerator.get_completion(context=context_from_index)

    return gen_text
