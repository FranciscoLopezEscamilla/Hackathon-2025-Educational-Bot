from pydantic import BaseModel

class Query(BaseModel):
    query: str

class QueryPost(BaseModel):
    query: str

class Summary(BaseModel):
    overview: str
    important_concepts: str
    features: str
    relevance: str
    conclusion: str

class ImagePrompt(BaseModel):
    prompts: list