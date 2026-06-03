from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.agent import run_agent_loop

router = APIRouter()

@router.post("/", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Accepts a list of OpenAI-format messages, runs the agent loop,
    and returns the final assistant message along with any internal reasoning/tool logs.
    """
    # Create a copy of messages to pass to the agent
    messages_copy = list(request.messages)
    
    result = run_agent_loop(messages_copy)
    
    return ChatResponse(
        final_message=result["final_message"],
        reasoning_logs=result["reasoning_logs"],
        messages=result["messages"]
    )
