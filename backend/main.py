import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any

from init_db import init_db
from agent import run_agent_loop

from fastapi.middleware.cors import CORSMiddleware

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup hook
    print("Running database initialization hook...")
    init_db()
    yield
    # Shutdown hook
    print("Shutting down...")

app = FastAPI(lifespan=lifespan, title="AI Refund Agent API")

# Configure CORS
origins = [
    "http://localhost:8501", # Streamlit
    "http://localhost:3000", # Next.js
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]

class ChatResponse(BaseModel):
    final_message: str
    reasoning_logs: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]

@app.post("/api/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    """
    Accepts a list of OpenAI-format messages, runs the agent loop,
    and returns the final assistant message along with any internal reasoning/tool logs.
    """
    # Create a copy of messages to pass to the agent
    # so we don't mutate the request object directly if we don't want to
    messages_copy = list(request.messages)
    
    result = run_agent_loop(messages_copy)
    
    return ChatResponse(
        final_message=result["final_message"],
        reasoning_logs=result["reasoning_logs"],
        messages=result["messages"]
    )
