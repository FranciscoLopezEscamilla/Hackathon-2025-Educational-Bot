from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from models.llm_clients import LlmUtils
import json
import os


llm = LlmUtils.llm_client

class TextService():

    def generate_text(context: str, query: str) -> str:
        """Generates text based on user query and provided context"""

        prompt = """Your job is to generate summary of a text based on context and user query:
        HERE IS THE CONTEXT: {context}
        USER QUERY: {query}
        """

        template = PromptTemplate.from_template(prompt)
        chain = template | llm

        response = chain.invoke({"context": context, "query": query})

        return response
        

        
       
   
  