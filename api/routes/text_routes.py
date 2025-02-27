from fastapi import APIRouter, HTTPException
from services.text_service import TextGenerator
from services.index_service import Database
from models.query import Query

router = APIRouter(prefix="/text", tags=["Text"])

@router.post("/summarize")
def summarize_content(request: Query):
    
    task = "summarization"
    context_from_index = Database.query_index(request.query)

    sum_text : str = TextGenerator.get_completion(context=context_from_index, task=task, query = request.query)

    clean_text: str = TextGenerator.parse_text(sum_text)
    return clean_text
