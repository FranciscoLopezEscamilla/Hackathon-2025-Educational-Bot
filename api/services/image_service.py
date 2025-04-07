from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.utilities.dalle_image_generator import DallEAPIWrapper
from models.llm_clients import LlmUtils
import requests
import json
import os
from datetime import datetime
from uuid import uuid4

client = LlmUtils.dalle_client
llm = LlmUtils.llm_client
model = os.getenv('GPT_IMAGES_DEPLOYMENT_NAME')
images_folder = os.getcwd() + "\\assets\\generated_images"

class ImageGenerator:

    
    def langchain_imgs(prompt: str):
        """Generate images based on user queries"""

        prompt_ = PromptTemplate(
            input_variables=["image_desc"],
            template="Generate a detailed prompt to generate an image based on the following query: {image_desc}",
        )

        chain = LLMChain(llm=client, prompt=prompt_)

        img_url = DallEAPIWrapper().run(chain.run(prompt))

        return img_url


    #def generate_images(prompts: list):
    #    """Generate very cool images based on queries and prompt from users."""
    #    image_urls = []
    #    sub_folder = (datetime.today().strftime('%Y-%m-%d %H:%M:%S')).replace(" ","-").replace(":","-")
    #    images_path = os.path.join(images_folder, sub_folder)
#
    #    if not os.path.exists(images_path):
    #        os.makedirs(images_path) 
#
    #    for prompt in prompts:
    #        result = client.images.generate(
    #                model = model,
    #                prompt=prompt,
    #                n=1
    #                )
#
    #        image_url = json.loads(result.model_dump_json())['data'][0]['url']
    #        image = requests.get(image_url).content
    #        image_name = f"genai_img_{uuid4()}"
    #        with open(os.path.join(images_folder, images_path, f"{image_name}.jpg"), 'wb') as handler:
    #            handler.write(image)

    #        image_urls.append(image_url)

    #    return image_urls