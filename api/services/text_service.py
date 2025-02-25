from services.index_service import load_local_index, format_content
from services.message_builder import MessageBuilder
from models.text_prompts import TextPromptTemplates
from models.llm_clients import LlmUtils
import os

model = os.getenv('GPT_DEPLOYMENT_NAME')
client = LlmUtils.llm_client()
prompt_instance = TextPromptTemplates()
system_message = prompt_instance.system_prompt
user_prompt = prompt_instance.user_message
USER = "user"
message_builder = MessageBuilder(system_message)

class TextGenerator():

    def get_completion(context: str, temperature:float = 0.7) -> str:
        
        generate_description_message = user_prompt.format(context=context)
        
        message_builder.append_messages(USER, generate_description_message)

        messages = message_builder.messages

        completion = client.chat.completions.create(
            model = model, 
            messages=messages,
            temperature=temperature
        )

        return completion.choices[0].message.content