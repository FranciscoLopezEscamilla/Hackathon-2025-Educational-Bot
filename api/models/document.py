from pydantic import BaseModel
from typing import List, Optional

class TextItem(BaseModel): 
    type: str # "title", "subtitle", "paragraph" 
    content: str

class DocumentContent(BaseModel):
    text_items: Optional[List[TextItem]] = []
    images: Optional[List[str]] = []

class DocumentRequest(BaseModel):
    title: str
    pages: List[DocumentContent]

class ImageItem(BaseModel):
    path: str

class DocumentMetadata(BaseModel):
    name: str
    url: str

class RampUpdDocuments(BaseModel):
    generated_files: Optional[List[DocumentMetadata]]
    indexed_files : Optional[List[DocumentMetadata]]

class PptRequest(BaseModel):
    title:str
    header: str
    headerContent: str
    subheader: str
    subheaderContent: str