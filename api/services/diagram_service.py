from langchain_core.prompts import PromptTemplate
from models.llm_clients import LlmUtils
from mermaid import Mermaid

llm = LlmUtils.llm

class DiagramGenerator:

    def generate_diagram(text):
        "you are a diagram creator expert that generates diagrams with mermaid package"

        prompt = """Your job is to write the code to generate a colorful mermaid diagram describing the text below:

        {text} 

        Please understand the text before generating the code. use the text information only , don't use any other information.
        only generate the code as output nothing extra.
        each line in the code must be terminated by ; 
        Code:"""

        template = PromptTemplate.from_template(prompt)
        chain = template | llm
        response = chain.invoke({"text": text})
        return response.content

    def execute_mermaid(graph):

        if "mermaid" in graph:
            graph = graph.replace("mermaid","").replace("`", "")
        return Mermaid(graph)