from fastapi import APIRouter, File, UploadFile, Form
from services.multi_agent_service import MultiAgent
from models.query import Query
from services.rag_service import RAG
from services.agentic_rag_workflow_service import AgenticRAGWorkflow
from pypdf import PdfReader
import io
from typing import List, Optional
from pydantic import BaseModel
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from typing import List, Optional, Dict, Any, Literal
from pdfminer.high_level import extract_text as pdfminer_extract_text

router = APIRouter(prefix="/agents", tags=["Agents"])

class MessageContent(BaseModel):
    type: Literal["user", "ai"]
    content: str

@router.post("/multiagent")
def call_multiagent(request: Query):
    app = MultiAgent.app
    response = app.invoke({"messages": [
        request.query
        ]})
    return response['messages'][-1].content

@router.post("/agentic_rag_v3")
async def call_agentic_rag(
    query: str = Form(...),
    message_history: str = Form(None),  # JSON serialized message history
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

    # Parse message history if provided
    history = []
    if message_history:
        try:
            import json
            parsed_history = json.loads(message_history)
            for msg in parsed_history:
                if msg["type"] == "user":
                    history.append(HumanMessage(content=msg["content"]))
                else:
                    history.append(AIMessage(content=msg["content"]))
        except Exception as e:
            print(f"Error parsing message history: {e}")
            # Continue with empty history if parsing fails
            history = []
    
    # Add the current query
    history.append(HumanMessage(content=query))
    
    workflow = AgenticRAGWorkflow()
    result = workflow(query, file_context=file_ctx, message_history=history)
    
    # Return the complete interaction including history
    return result