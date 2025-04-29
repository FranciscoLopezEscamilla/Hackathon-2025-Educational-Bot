from models.document import DocumentContent, DocumentRequest, TextItem, PptRequest
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from models.llm_clients import LlmUtils
llm = LlmUtils.llm

parser = JsonOutputParser(pydantic_object=PptRequest)

def create_sample_request(text):
    """Create sample request for generate ppt files"""

    prompt = """Your job is to read and analyze the following text: {text}
    
    You need to understand the previos text and generate the following values:

    Title
    Header
    Content of header
    Sub header
    Content of sub header

    return a valid json file with the values like this:

    "title": "value",
    "header": "value",
    "headerContent": "value",
    "subheader": "value",
    "subheaderContent": "value"

    """

    prompt_template = PromptTemplate(template=prompt,
                                     input_variables=["text"],
                                     partial_variables={"format_instructions": parser.get_format_instructions()})
    chain  = prompt_template | llm | parser
    response = chain.invoke({"text": text})
    
    
    title = response["title"]
    header = response["header"]
    content_header = response["headerContent"]
    sub_header = response["subheader"]
    sub_header_content = response["subheaderContent"]

    sample_request = DocumentRequest(
            title=title,
            pages=[
                DocumentContent(
                    text_items=[
                        TextItem(type="header", content=header),
                        TextItem(type="paragraph", content=content_header),
                    ],
                    images=[
                        #ImageItem(path="sample_image.png")
                    ]
                ),

                DocumentContent(
                    text_items=[
                        TextItem(type="subheader", content=sub_header),
                        TextItem(type="paragraph", content=sub_header_content),
                    ],
                    images=[]
                )

            ]
        )
    
    return sample_request