from fastapi import APIRouter, HTTPException
from services.text_service import hello_world

router = APIRouter()

@router.get("/text-generator", response_model=str)
async def simple_text():
    name = "pedro"
    return hello_world(name)
