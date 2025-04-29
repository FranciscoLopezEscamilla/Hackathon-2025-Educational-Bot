from langchain_core.prompts import PromptTemplate
from models.llm_clients import LlmUtils
from mermaid import Mermaid
from langchain_core.runnables.graph_mermaid import draw_mermaid_png
import uuid
import os

llm = LlmUtils.llm
parent_dir = os.getcwd()

class DiagramGenerator:

    def generate_diagram(text):
        "you are a diagram creator expert that generates diagrams with mermaid package"

        prompt  = """Your job is to write the code to generate a colorful mermaid diagram describing the text below:

        {text} 
    
        Please understand the text before generating the code. use the text information only , don't use any other information.
        only generate the code as output nothing extra. Do not add code that is not part of mermaid.
        each line in the code must be terminated by ; 
        Code:"""

        template = PromptTemplate.from_template(prompt)
        chain = template | llm
        response = chain.invoke({"text": text})
        return response.content

    def execute_mermaid(graph):
        output_path = parent_dir + "/assets/diagrams"
        print(output_path)
        file_id = uuid.uuid4()

        if "mermaid" in graph:
            graph = graph.replace("mermaid","").replace("`", "")

        draw_mermaid_png(mermaid_syntax=graph, 
                         output_file_path=os.path.join(output_path, f"{file_id}.png"))
        
        return os.path.join(output_path, f"{file_id}.png"), f"{file_id}.png"
