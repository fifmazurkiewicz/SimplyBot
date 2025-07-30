from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ConversationMessage(BaseModel):
    role: str  # "user" lub "assistant"
    content: str
    timestamp: Optional[datetime] = None

class Conversation(BaseModel):
    messages: List[ConversationMessage]
    session_id: Optional[str] = None

class GetMoreInformationRequest(BaseModel):
    conversation: Conversation

class GetMoreInformationResponse(BaseModel):
    answer: str
    audio_url: Optional[str] = None
    confidence: float = 0.0
    sources: List[Dict[str, Any]] = []
    needs_clarification: bool = False

class DocumentUploadResponse(BaseModel):
    success: bool
    message: str
    document_count: int = 0

class HealthCheckResponse(BaseModel):
    status: str
    timestamp: datetime
    services: Dict[str, str]

# Nowe modele dla zarządzania plikami
class FileInfo(BaseModel):
    filename: str
    size: int  # w bajtach
    created_at: datetime
    content_type: str
    path: str

class FileListResponse(BaseModel):
    files: List[FileInfo]
    total_count: int
    total_size: int  # w bajtach

class FileUploadResponse(BaseModel):
    success: bool
    message: str
    file: Optional[FileInfo] = None

class NextAction(str, Enum):
    """Enum dla następnej akcji po podsumowaniu rozmowy"""
    RAG_QUERY = "rag_query"
    ASK_USER = "ask_user"

class ConversationSummary(BaseModel):
    """Model podsumowania rozmowy z zabezpieczeniem"""
    conversation_summary: str = Field(
        description="Krótkie podsumowanie głównych punktów rozmowy"
    )
    rag_query: str = Field(
        description="Konkretne zapytanie do bazy wiedzy (RAG) lub pytanie do użytkownika"
    )
    next_action: NextAction = Field(
        description="Następna akcja: rag_query (zapytanie do RAG) lub ask_user (dopytaj użytkownika)"
    )
    confidence: float = Field(
        ge=0.0,
        le=1.0,
        description="Pewność podsumowania (0.0-1.0)"
    )
    reasoning: str = Field(
        description="Uzasadnienie wybranej akcji"
    )

class ConversationSummaryRequest(BaseModel):
    """Request dla podsumowania rozmowy"""
    conversation: Dict[str, Any] = Field(
        description="Rozmowa do podsumowania"
    )

class ConversationSummaryResponse(BaseModel):
    """Response z podsumowaniem rozmowy"""
    summary: ConversationSummary
    success: bool = True
    message: Optional[str] = None 