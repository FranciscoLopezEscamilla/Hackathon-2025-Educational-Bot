from fastapi import APIRouter
from services.multi_agent_service import MultiAgent
from models.query import Query
from services.rag_service import RAG
from services.agentic_rag_workflow_service import AgenticRAGWorkflow

router = APIRouter(prefix="/agents", tags=["Agents"])

@router.post("/multiagent")
def call_multiagent(request: Query):

    #context = RAG.get_context_from_index(request.query)

    app = MultiAgent.app

    response = app.invoke({"messages": [
        request.query
        ]})

    return response['messages'][-1].content

@router.post("/agentic_rag_v3")
def call_agentic_rag(request: Query):
    print(request)
    workflow = AgenticRAGWorkflow()
    response = workflow(request.query)
    return response

