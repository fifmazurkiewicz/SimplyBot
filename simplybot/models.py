from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

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