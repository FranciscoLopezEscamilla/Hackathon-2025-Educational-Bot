from fastapi import APIRouter
from services.multi_agent_service import MultiAgent
from models.query import Query

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/multiagent")
def call_multiagent(request: Query):

    print("You are in agent edpoint")
    app = MultiAgent.app

    response = app.invoke({"messages": [request.query]})

    return response



