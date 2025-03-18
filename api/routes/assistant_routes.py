from fastapi import APIRouter
from services.assistant_service import AssistantService

router = APIRouter()
assistant_service = AssistantService()

@router.post("/assistant")
def chat_with_assistant(user_message: str):
    """Handles user queries to the assistant."""
    thread = assistant_service.create_thread()
    assistant_service.send_message(thread.id, user_message)
    
    run = assistant_service.run_thread(thread.id)
    
    if run.status == "completed":
        messages = assistant_service.get_thread_messages(thread.id)
        return {"response": messages.data[0].content[0].text.value}
    else:
        return {"error": f"Run failed with status: {run.status}"}
