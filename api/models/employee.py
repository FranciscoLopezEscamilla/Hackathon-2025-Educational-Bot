from pydantic import BaseModel

class EmployeeBase(BaseModel):
    id: int
    name: str

# this type would be returned as the response of the HTTP POST endpoint
class EmployeeCreate(BaseModel):
    pass

# this type is returned as the response of the HTTP GET endpoint
class EmployeeGetResponse(BaseModel):
    id: int
    name: str