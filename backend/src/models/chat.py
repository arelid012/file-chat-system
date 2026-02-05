# backend/src/models/chat.py
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum

class Language(str, Enum):
    EN = "en"
    MS = "ms"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: MessageRole
    content: str
    timestamp: datetime = Field(default_factory=datetime.now)

class QuestionRequest(BaseModel):
    text: str
    session_id: Optional[str] = None
    language: Language = Language.EN

class ChatResponse(BaseModel):
    answer: str
    sources: List[dict] = Field(default_factory=list)  
    language: Language
    session_id: Optional[str] = None