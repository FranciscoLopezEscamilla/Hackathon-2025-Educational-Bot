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


class TextGenerator():

    def summarize_text(context: str, query: str, temperature:float = 0.7) -> str:
        message_builder = MessageBuilder(system_message)
        user_message = summarization_prompt.format(context=context, query=query)

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
    
    def generate_text_descriptions(text: str, temperature:float = 0.7):
        message_builder = MessageBuilder(system_message)
        user_message = description_prompt.format(text = text)

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