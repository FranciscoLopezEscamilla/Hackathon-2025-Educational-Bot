from fastapi import APIRouter, HTTPException
from services.image_service import ImageGenerator
from models.query import ImagePrompt

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/generate")
def generate_image(request: ImagePrompt):

    img_url = ImageGenerator.generate_images(request.prompt)

    return img_url