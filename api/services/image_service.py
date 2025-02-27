from models.llm_clients import LlmUtils
import requests
import json
import os
from datetime import datetime
from uuid import uuid4

client = LlmUtils.llm_client()
model = os.getenv('GPT_IMAGES_DEPLOYMENT_NAME')
images_folder = os.getcwd() + "\\assets\\generated_images"

class ImageGenerator:

    def generate_images(prompts: list):
        image_urls = []
        for prompt in prompts:
            result = client.images.generate(
                    model = model,
                    prompt=prompt,
                    n=1
                    )

            image_url = json.loads(result.model_dump_json())['data'][0]['url']
            image = requests.get(image_url).content

        #sub_folder = str(datetime.now())
        #images_path = os.path.join(images_folder, sub_folder)
        #if not os.path.exists(images_path):
        #    os.makedirs(images_path) 

            image_name = f"genai_img_{uuid4()}"
            with open(os.path.join(images_folder, f"{image_name}.jpg"), 'wb') as handler:
                handler.write(image)

            image_urls.append(image_url)

        return image_urls