from fastapi import APIRouter, File, UploadFile, Form
from services.multi_agent_service import MultiAgent
from models.query import Query
from services.rag_service import RAG
from services.agentic_rag_workflow_service import AgenticRAGWorkflow
from pypdf import PdfReader
import io
from typing import List
from pdfminer.high_level import extract_text as pdfminer_extract_text
from typing import List, Optional


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
async def call_agentic_rag(
    query: str = Form(...),
    files: Optional[List[UploadFile]] = File(None)
):
    file_ctx = ""
    if files:
        parts = []
        for up in files:
            data = await up.read()
            try:
                reader = PdfReader(io.BytesIO(data))
                txt = "\n".join(p.extract_text() or "" for p in reader.pages)
            except:
                txt = pdfminer_extract_text(io.BytesIO(data))
            parts.append(txt)
        file_ctx = "\n\n".join(parts)

    workflow = AgenticRAGWorkflow()
    return workflow(query, file_context=file_ctx)