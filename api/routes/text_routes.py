from fastapi import APIRouter, HTTPException
from services.text_service import TextGenerator
from services.index_service import Database
from models.query import Query, Summary
import logging
import json

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/text", tags=["Text"])

@router.post("/summarize")
def summarize_content(request: Query):
    
    context_from_index = Database.query_index(request.query)

    sum_text : str = TextGenerator.summarize_text(context=context_from_index, query = request.query)

    clean_text: str = TextGenerator.parse_text(sum_text)

    return clean_text

@router.post("/descriptions")
def read_text(request: Summary):

    output: str = TextGenerator.generate_text_descriptions(text = request)

    clean_text: str = TextGenerator.parse_text(output)

    return clean_text