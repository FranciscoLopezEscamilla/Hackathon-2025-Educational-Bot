from langchain_core.prompts import PromptTemplate
from models.llm_clients import LlmUtils
from datetime import datetime
import requests
import json
import os
from uuid import uuid4

client = LlmUtils.client
llm = LlmUtils.llm_client
model = os.getenv('GPT_IMAGES_DEPLOYMENT_NAME')
images_folder = os.getcwd() + "\\assets\\generated_images"

class ImageGenerator:


    def generate_images(prompt: str):
        """Generate images based on queries and prompt from users."""

        sub_folder = (datetime.today().strftime('%Y-%m-%d %H:%M:%S')).replace(" ","-").replace(":","-")
        images_path = os.path.join(images_folder, sub_folder)

        if not os.path.exists(images_path):
            os.makedirs(images_path) 

        
        result = client.images.generate(
                    model = model,
                    prompt=prompt,
                    n=1
                    )
        
        image_url = json.loads(result.model_dump_json())['data'][0]['url']
        print(image_url)
        image = requests.get(image_url).content
        image_name = f"genai_img_{uuid4()}"

        with open(os.path.join(images_folder, images_path, f"{image_name}.jpg"), 'wb') as handler:
            handler.write(image)
        
        return image_url