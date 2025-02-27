from services.message_builder import MessageBuilder
from models.text_prompts import TextPromptTemplates
from models.llm_clients import LlmUtils
from models.custom_functions import CustomFunctions
import json
import os

model = os.getenv('GPT_DEPLOYMENT_NAME')
client = LlmUtils.llm_client()
prompt_instance = TextPromptTemplates
functions_instance = CustomFunctions
functions = CustomFunctions.functions
system_message = prompt_instance.system_prompt
summarization_prompt = prompt_instance.summarization_text_prompt
description_prompt = prompt_instance.description_prompt
USER = "user"
message_builder = MessageBuilder(system_message)

class TextGenerator():

    def get_completion(context: str, task: str, query: str, temperature:float = 0.7) -> str:
        
        if task == "summarization":
            user_message = summarization_prompt.format(context=context, query=query)

        elif task == "description":
            user_message = description_prompt

        message_builder.append_messages(USER, user_message)
        messages = message_builder.messages
        completion = client.chat.completions.create(
            model = model, 
            messages=messages,
            temperature=temperature,
            #tools=functions,
            #tool_choice={"type": "function", "function": {"name": "summarize_text"}}
        )

        return completion.choices[0].message.content
    
    def parse_text(summary: str):
        clean_summary = json.loads(summary)
        return clean_summary