from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from models.llm_clients import LlmUtils
import json
import os


llm = LlmUtils.llm_client

class TextService():

    def generate_text(context: str, query: str) -> str:
        """Generates a response for the user query based on context."""

        prompt = """You are a smart assistant that can generate text based on user query.
        Your job is to analyze the following user query:

        ### USER QUERY ### 
        {query}

        Make sure you understand what the user needs based on the query and generate an appropiate response.
        
        Use only the following context to generate your response, DO NOT add any information outside the context.
        ### CONTEXT ### 
        {context}
        
        """

        template = PromptTemplate.from_template(prompt)
        chain = template | llm

        response = chain.invoke({"context": context, "query": query})

        return response.content
        

        
       
   
  