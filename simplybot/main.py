from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from qdrant_client import QdrantClient
from simplybot.models import (
    GetMoreInformationRequest, 
    GetMoreInformationResponse,
    DocumentUploadResponse,
    HealthCheckResponse,
    FileInfo,
    FileListResponse,
    FileUploadResponse,
    ConversationSummaryResponse,
    ConversationSummaryRequest
)
from simplybot.services.llm_service import LLMService
from simplybot.services.vector_store import VectorStoreService
from simplybot.services.audio_service import AudioService
from simplybot.services.document_processor import DocumentProcessor
from simplybot.config import Config
import logging
import os
from datetime import datetime
from typing import List, Dict
import tempfile
from pathlib import Path
import json

# Konfiguracja logowania
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="SimplyBot API",
    description="RAG chatbot using LangChain, Qdrant and ElevenLabs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Statyczne pliki
os.makedirs("static", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Inicjalizacja serwisów
llm_service = LLMService()
vector_store = VectorStoreService()
audio_service = AudioService()
document_processor = DocumentProcessor()

@app.get("/", response_model=HealthCheckResponse)
async def health_check():
    """Checks service status"""
    services = {}
    
    # Check OpenRouter/OpenAI
    try:
        if Config.OPENROUTER_API_KEY:
            services["openrouter"] = "ok"
        elif Config.OPENAI_API_KEY:
            services["openai"] = "ok"
        else:
            services["llm"] = "no_api_key"
    except:
        services["llm"] = "error"
    
    # Check Qdrant
    try:
        # First check if server is running
        client = QdrantClient(url=Config.QDRANT_URL)
        collections = client.get_collections()
        services["qdrant"] = "ok"
        
        # Additionally check collection (optional)
        try:
            qdrant_info = await vector_store.get_collection_info()
            if qdrant_info.get("status") == "ok":
                services["qdrant_collection"] = "ok"
            else:
                services["qdrant_collection"] = "not_found"
        except:
            services["qdrant_collection"] = "not_found"
            
    except Exception as e:
        logger.error(f"Qdrant connection error: {e}")
        services["qdrant"] = "error"
    
    # Check ElevenLabs
    try:
        if Config.ELEVENLABS_API_KEY:
            services["elevenlabs"] = "ok"
        else:
            services["elevenlabs"] = "no_api_key"
    except:
        services["elevenlabs"] = "error"
    
    # Check Embeddings
    try:
        services["embeddings"] = Config.EMBEDDING_MODEL
        if Config.EMBEDDING_MODEL == "bge":
            services["bge_model"] = Config.BGE_MODEL_NAME
    except:
        services["embeddings"] = "error"
    
    return HealthCheckResponse(
        status="ok",
        timestamp=datetime.now(),
        services=services
    )

@app.post("/get_more_information", response_model=GetMoreInformationResponse)
async def get_more_information(request: GetMoreInformationRequest):
    """Main endpoint for bot conversation handling"""
    try:
        logger.info(f"🚀 Starting request processing (session: {request.conversation.session_id})")
        
        # 1. Convert conversation to LLM format
        conversation_messages = []
        for msg in request.conversation.messages:
            conversation_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        logger.info(f"💬 Conversation contains {len(conversation_messages)} messages")
        
        # 2. Summarize conversation and prepare RAG query
        logger.info("🧠 STEP 1: Summarizing conversation...")
        conversation_summary = await llm_service.summarize_conversation(conversation_messages)
        
        logger.info(f"📊 Summary: {conversation_summary.next_action} (confidence: {conversation_summary.confidence})")
        logger.info(f"💭 Reasoning: {conversation_summary.reasoning}")
        
        # Check if user needs to be asked for more
        if conversation_summary.next_action.value == "ask_user":
            logger.info("🤔 Conversation requires user follow-up")
            return GetMoreInformationResponse(
                answer=f"**TLDR:** {conversation_summary.rag_query}\n\n**Opis:** {conversation_summary.conversation_summary}",
                audio_url=None,
                confidence=conversation_summary.confidence,
                sources=[],
                needs_clarification=True
            )
        
        # 3. Search documents in Qdrant
        logger.info("🔍 STEP 2: Searching documents in Qdrant...")
        question = conversation_summary.rag_query
        question_preview = question[:10] + "..." if len(question) > 10 else question
        logger.info(f"❓ RAG question: '{question_preview}'")
        
        context_docs = await vector_store.search_documents(question, limit=5)
        
        # 4. Generate response with context
        logger.info("🤖 STEP 3: Generating response with context...")
        answer = await llm_service.answer_with_context(question, context_docs)
        
        # 5. Generate audio only for TLDR (optional)
        audio_url = None
        if Config.ELEVENLABS_API_KEY:
            logger.info("🎵 STEP 4: Generating audio for TLDR...")
            
            # Extract TLDR from response
            tldr_text = ""
            if "**TLDR:**" in answer:
                tldr_part = answer.split("**Opis:**")[0]
                tldr_text = tldr_part.replace("**TLDR:**", "").strip()
                logger.info(f"📋 TLDR for audio: '{tldr_text[:50]}...'")
            else:
                # If no TLDR format, use entire response
                tldr_text = answer
                logger.info(f"📋 Using entire response for audio: '{tldr_text[:50]}...'")
            
            audio_url = await audio_service.generate_speech(tldr_text)
            if audio_url:
                logger.info(f"✅ Audio generated for TLDR: {audio_url}")
            else:
                logger.warning("⚠️ Failed to generate audio")
        else:
            logger.info("⚠️ Skipping audio generation - no ElevenLabs key")
        
        # 6. Prepare sources
        sources = []
        for doc in context_docs:
            sources.append({
                "content": doc.get("content", "")[:200] + "...",
                "metadata": doc.get("metadata", {}),
                "score": doc.get("score", 0)
            })
        
        logger.info(f"🎉 Processing completed - response ready (audio: {'yes' if audio_url else 'no'})")
        
        return GetMoreInformationResponse(
            answer=answer,
            audio_url=audio_url,
            confidence=conversation_summary.confidence,
            sources=sources,
            needs_clarification=False
        )
        
    except Exception as e:
        logger.error(f"Error in get_more_information: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/summarize-conversation", response_model=ConversationSummaryResponse)
async def summarize_conversation(request: ConversationSummaryRequest):
    """Endpoint for testing conversation summary"""
    try:
        logger.info("🧠 Testing conversation summary...")
        
        # Convert conversation to LLM format
        conversation_messages = []
        for msg in request.conversation.get("messages", []):
            conversation_messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Summarize conversation
        summary = await llm_service.summarize_conversation(conversation_messages)
        
        return ConversationSummaryResponse(
            summary=summary,
            success=True,
            message="Conversation summary generated successfully"
        )
        
    except Exception as e:
        logger.error(f"Error during conversation summarization: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_documents", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Endpoint for uploading documents"""
    try:
        total_documents = 0
        
        for file in files:
            # Check file size
            if file.size > Config.MAX_FILE_SIZE * 1024 * 1024:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} is too large. Maximum size: {Config.MAX_FILE_SIZE}MB"
                )
            
            # Save file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Process document
                documents = await document_processor.process_file(temp_file_path, file.filename)
                
                if documents:
                    # Add to vector store
                    added_count = await vector_store.add_documents(documents)
                    total_documents += added_count
                    logger.info(f"Added {added_count} fragments from file {file.filename}")
                
            finally:
                # Delete temporary file
                os.unlink(temp_file_path)
        
        return DocumentUploadResponse(
            success=True,
            message=f"Successfully added {total_documents} document fragments",
            document_count=total_documents
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/info")
async def get_documents_info():
    """Returns information about documents in database"""
    try:
        logger.info("📊 Retrieving document information...")
        info = await vector_store.get_collection_info()
        logger.info(f"📊 Document information: {info}")
        return info
    except Exception as e:
        logger.error(f"Error retrieving document information: {e}")
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/generate-audio")
async def generate_audio(request: Dict):
    """Generates audio from text"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="No text to convert")
        
        audio_url = await audio_service.generate_speech(text)
        return {"audio_url": audio_url}
    except Exception as e:
        logger.error(f"Error generating audio: {e}")
        raise HTTPException(status_code=500, detail="Error generating audio")

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Retrieves audio file"""
    try:
        import os
        from fastapi.responses import FileResponse
        
        audio_path = os.path.join("static/audio", filename)
        if os.path.exists(audio_path):
            return FileResponse(audio_path, media_type="audio/mpeg")
        else:
            raise HTTPException(status_code=404, detail="Audio file not found")
    except Exception as e:
        logger.error(f"Error retrieving audio file: {e}")
        raise HTTPException(status_code=500, detail="Error retrieving audio file")

@app.post("/chat-with-json")
async def chat_with_json(json_data: Dict):
    """Chat with LLM based on JSON data"""
    try:
        # Convert JSON to text
        json_text = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        # Prepare message for LLM
        system_prompt = """
        You are a helpful assistant. Analyze the provided JSON data and answer user questions.
        
        Responses MUST be in format:
        
        **TLDR:** [One line with quick, concise answer]
        
        **Description:** [Detailed description with additional information, context and explanations]
        
        Responses should be:
        - Accurate and based on JSON data
        - TLDR should be very concise (1-2 sentences)
        - Description can be longer and contain details
        - In English
        """
        
        # Call LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this JSON data and answer questions:\n\n{json_text}"}
        ]
        
        # Use LLMService to generate response
        response = await llm_service.answer_with_context("", [{"content": json_text}])
        
        # Generate audio only for TLDR (optional)
        audio_url = None
        if Config.ELEVENLABS_API_KEY:
            logger.info("🎵 Generating audio for TLDR from JSON...")
            
            # Extract TLDR from response
            tldr_text = ""
            if "**TLDR:**" in response:
                tldr_part = response.split("**Description:**")[0]
                tldr_text = tldr_part.replace("**TLDR:**", "").strip()
                logger.info(f"📋 TLDR for audio: '{tldr_text[:50]}...'")
            else:
                # If no TLDR format, use entire response
                tldr_text = response
                logger.info(f"📋 Using entire response for audio: '{tldr_text[:50]}...'")
            
            audio_url = await audio_service.generate_speech(tldr_text)
            if audio_url:
                logger.info(f"✅ Audio generated for TLDR: {audio_url}")
            else:
                logger.warning("⚠️ Failed to generate audio")
        
        return {"answer": response, "audio_url": audio_url}
        
    except Exception as e:
        logger.error(f"Error processing JSON: {e}")
        raise HTTPException(status_code=500, detail="Error processing JSON")

# File management endpoints
@app.post("/files/upload", response_model=FileUploadResponse, tags=["Files"])
async def upload_file(file: UploadFile = File(...)):
    """
    Uploads a single file to the system.
    
    - **file**: File to upload (PDF, TXT, DOCX)
    
    Returns information about the uploaded file.
    """
    try:
        logger.info(f"📤 Rozpoczynam wrzucanie pliku: {file.filename}")
        
        # Sprawdź rozmiar pliku
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
        logger.info(f"📏 Rozmiar pliku: {file_size} bajtów")
        
        if file_size > Config.MAX_FILE_SIZE * 1024 * 1024:
            raise HTTPException(
                status_code=400,
                detail=f"Plik jest za duży. Maksymalny rozmiar: {Config.MAX_FILE_SIZE}MB"
            )
        
        # Sprawdź rozszerzenie
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in ['.pdf', '.txt', '.docx']:
            raise HTTPException(
                status_code=400,
                detail=f"Nieobsługiwany format pliku: {file_extension}. Dozwolone: PDF, TXT, DOCX"
            )
        
        # Utwórz katalog uploads jeśli nie istnieje
        upload_dir = Path(Config.UPLOAD_DIR)
        upload_dir.mkdir(exist_ok=True)
        
        # Zapisz plik
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            f.write(content)
        
        logger.info(f"💾 Plik zapisany: {file_path}")
        
        # Przygotuj informacje o pliku
        file_info = FileInfo(
            filename=file.filename,
            size=file_size,
            created_at=datetime.now(),
            content_type=file.content_type,
            path=str(file_path)
        )
        
        logger.info(f"✅ Plik wrzucony pomyślnie: {file.filename}")
        
        return FileUploadResponse(
            success=True,
            message="Plik został pomyślnie wrzucony",
            file=file_info
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas wrzucania pliku: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/files", response_model=FileListResponse, tags=["Files"])
async def list_files():
    """
    Zwraca listę wszystkich plików w systemie.
    
    Zwraca:
    - Listę plików z informacjami
    - Całkowitą liczbę plików
    - Całkowity rozmiar plików
    """
    try:
        files = []
        total_size = 0
        upload_dir = Path(Config.UPLOAD_DIR)
        
        # Utwórz katalog jeśli nie istnieje
        upload_dir.mkdir(exist_ok=True)
        
        logger.info(f"📁 Skanowanie katalogu: {upload_dir}")
        
        # Zbierz informacje o plikach
        for file_path in upload_dir.glob("*.*"):
            if file_path.suffix.lower() in ['.pdf', '.txt', '.docx']:
                try:
                    size = file_path.stat().st_size
                    created_at = datetime.fromtimestamp(file_path.stat().st_ctime)
                    
                    # Określ typ zawartości
                    content_type = {
                        '.pdf': 'application/pdf',
                        '.txt': 'text/plain',
                        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                    }.get(file_path.suffix.lower(), 'application/octet-stream')
                    
                    file_info = FileInfo(
                        filename=file_path.name,
                        size=size,
                        created_at=created_at,
                        content_type=content_type,
                        path=str(file_path)
                    )
                    files.append(file_info)
                    total_size += size
                    
                    logger.info(f"📄 Znaleziono plik: {file_path.name} ({size} bajtów)")
                    
                except Exception as file_error:
                    logger.warning(f"⚠️ Błąd podczas przetwarzania pliku {file_path.name}: {file_error}")
                    continue
        
        logger.info(f"📊 Znaleziono {len(files)} plików, łącznie {total_size} bajtów")
        
        return FileListResponse(
            files=sorted(files, key=lambda x: x.created_at, reverse=True),
            total_count=len(files),
            total_size=total_size
        )
        
    except Exception as e:
        logger.error(f"Błąd podczas listowania plików: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/files/{filename}", tags=["Files"])
async def delete_file(filename: str):
    """
    Usuwa pojedynczy plik z systemu.
    
    - **filename**: Nazwa pliku do usunięcia
    """
    try:
        file_path = Path(Config.UPLOAD_DIR) / filename
        
        if not file_path.exists():
            raise HTTPException(
                status_code=404,
                detail=f"Plik {filename} nie istnieje"
            )
        
        file_path.unlink()
        return {"success": True, "message": f"Plik {filename} został usunięty"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas usuwania pliku: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 