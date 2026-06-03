from pydantic import BaseModel
from typing import List, Dict, Any

class ChatRequest(BaseModel):
    messages: List[Dict[str, Any]]

class ChatResponse(BaseModel):
    final_message: str
    reasoning_logs: List[Dict[str, Any]]
    messages: List[Dict[str, Any]]
