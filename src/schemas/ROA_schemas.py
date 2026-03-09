from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    question: str
    conversation_id: Optional[str] = None

class ChatResponse(BaseModel):
    answer: str
    formatted_answer: Optional[str] = None
    code_snippet: Optional[str] = None
    conversation_id: str
    history_count: int = 0