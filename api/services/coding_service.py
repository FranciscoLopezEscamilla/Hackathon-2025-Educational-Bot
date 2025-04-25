from langchain_core.prompts import PromptTemplate
from langchain_core.tools import tool
from models.llm_clients import LlmUtils
import json
import os


llm = LlmUtils.llm

class CodingService():

    def generate_code(context: str, query: str) -> str:
        """Generates a response for the user query based on context."""

        prompt = """You are a smart assistant that can generate, write and review code based on user query.
        Your job is to respond to the following user query:

        ### USER QUERY ### 
        {query}

        Make sure you understand what the user needs and generate an appropiate response.
        
        When necessary use the provided context to generate your response, DO NOT add any information outside the context.
        ### CONTEXT ### 
        {context}
        
        """

        template = PromptTemplate.from_template(prompt)
        chain = template | llm

        response = chain.invoke({"context": context, "query": query})

        return response.content