from pydantic import BaseModel

class Query(BaseModel):
    query: str

class QueryPost(BaseModel):
    query: str