from fastapi import APIRouter
from services.multi_agent_service import MultiAgent
from models.query import Query
from services.rag_service import RAG

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/multiagent")
def call_multiagent(request: Query):

    app = MultiAgent.app

    response = app.invoke({"messages": [
        request.query
        
        ]})

    return response['messages'][-1].content



