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
    FileUploadResponse
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
    description="Bot dialogowy z RAG wykorzystujący LangChain, Qdrant i ElevenLabs",
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
    """Sprawdza stan usług"""
    services = {}
    
    # Sprawdź OpenRouter/OpenAI
    try:
        if Config.OPENROUTER_API_KEY:
            services["openrouter"] = "ok"
        elif Config.OPENAI_API_KEY:
            services["openai"] = "ok"
        else:
            services["llm"] = "no_api_key"
    except:
        services["llm"] = "error"
    
    # Sprawdź Qdrant
    try:
        # Najpierw sprawdź czy serwer działa
        client = QdrantClient(url=Config.QDRANT_URL)
        collections = client.get_collections()
        services["qdrant"] = "ok"
        
        # Dodatkowo sprawdź kolekcję (opcjonalnie)
        try:
            qdrant_info = await vector_store.get_collection_info()
            if qdrant_info.get("status") == "ok":
                services["qdrant_collection"] = "ok"
            else:
                services["qdrant_collection"] = "not_found"
        except:
            services["qdrant_collection"] = "not_found"
            
    except Exception as e:
        logger.error(f"Błąd połączenia z Qdrant: {e}")
        services["qdrant"] = "error"
    
    # Sprawdź ElevenLabs
    try:
        if Config.ELEVENLABS_API_KEY:
            services["elevenlabs"] = "ok"
        else:
            services["elevenlabs"] = "no_api_key"
    except:
        services["elevenlabs"] = "error"
    
    # Sprawdź Embeddings
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
    """Główny endpoint do obsługi rozmowy z botem"""
    try:
        logger.info(f"🚀 Rozpoczynam przetwarzanie zapytania (sesja: {request.conversation.session_id})")
        
        # 1. Konwertuj rozmowę na format dla LLM
        conversation_messages = []
        for msg in request.conversation.messages:
            conversation_messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        logger.info(f"💬 Rozmowa zawiera {len(conversation_messages)} wiadomości")
        
        # 2. Podsumuj rozmowę i przygotuj zapytanie do RAG
        logger.info("🧠 KROK 1: Podsumowywanie rozmowy...")
        summary = await llm_service.summarize_conversation(conversation_messages)
        
        # Wyciągnij pytanie z podsumowania
        question = summary
        if "PYTANIE:" in summary:
            question = summary.split("PYTANIE:")[-1].strip()
        
        question_preview = question[:10] + "..." if len(question) > 10 else question
        logger.info(f"❓ Pytanie do RAG: '{question_preview}'")
        
        # 3. Wyszukaj dokumenty w Qdrant
        logger.info("🔍 KROK 2: Wyszukiwanie dokumentów w Qdrant...")
        context_docs = await vector_store.search_documents(question, limit=5)
        
        # 4. Wygeneruj odpowiedź z kontekstem
        logger.info("🤖 KROK 3: Generowanie odpowiedzi z kontekstem...")
        answer = await llm_service.answer_with_context(question, context_docs)
        
        # 5. Generuj audio tylko dla TLDR (opcjonalnie)
        audio_url = None
        if Config.ELEVENLABS_API_KEY:
            logger.info("🎵 KROK 4: Generowanie audio dla TLDR...")
            
            # Wyciągnij TLDR z odpowiedzi
            tldr_text = ""
            if "**TLDR:**" in answer:
                tldr_part = answer.split("**Opis:**")[0]
                tldr_text = tldr_part.replace("**TLDR:**", "").strip()
                logger.info(f"📋 TLDR do audio: '{tldr_text[:50]}...'")
            else:
                # Jeśli nie ma formatu TLDR, użyj całej odpowiedzi
                tldr_text = answer
                logger.info(f"📋 Używam całej odpowiedzi do audio: '{tldr_text[:50]}...'")
            
            audio_url = await audio_service.generate_speech(tldr_text)
            if audio_url:
                logger.info(f"✅ Audio wygenerowane dla TLDR: {audio_url}")
            else:
                logger.warning("⚠️ Nie udało się wygenerować audio")
        else:
            logger.info("⚠️ Pomijam generowanie audio - brak klucza ElevenLabs")
        
        # 6. Przygotuj źródła
        sources = []
        for doc in context_docs:
            sources.append({
                "content": doc.get("content", "")[:200] + "...",
                "metadata": doc.get("metadata", {}),
                "score": doc.get("score", 0)
            })
        
        logger.info(f"🎉 Przetwarzanie zakończone - odpowiedź gotowa (audio: {'tak' if audio_url else 'nie'})")
        
        return GetMoreInformationResponse(
            answer=answer,
            audio_url=audio_url,
            confidence=0.8 if context_docs else 0.0,
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Błąd w get_more_information: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/upload_documents", response_model=DocumentUploadResponse)
async def upload_documents(files: List[UploadFile] = File(...)):
    """Endpoint do wrzucania dokumentów"""
    try:
        total_documents = 0
        
        for file in files:
            # Sprawdź rozmiar pliku
            if file.size > Config.MAX_FILE_SIZE * 1024 * 1024:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Plik {file.filename} jest za duży. Maksymalny rozmiar: {Config.MAX_FILE_SIZE}MB"
                )
            
            # Zapisz plik tymczasowo
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as temp_file:
                content = await file.read()
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Przetwórz dokument
                documents = await document_processor.process_file(temp_file_path, file.filename)
                
                if documents:
                    # Dodaj do vector store
                    added_count = await vector_store.add_documents(documents)
                    total_documents += added_count
                    logger.info(f"Dodano {added_count} fragmentów z pliku {file.filename}")
                
            finally:
                # Usuń plik tymczasowy
                os.unlink(temp_file_path)
        
        return DocumentUploadResponse(
            success=True,
            message=f"Pomyślnie dodano {total_documents} fragmentów dokumentów",
            document_count=total_documents
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Błąd podczas wrzucania dokumentów: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/info")
async def get_documents_info():
    """Zwraca informacje o dokumentach w bazie"""
    try:
        info = await vector_store.get_collection_info()
        return info
    except Exception as e:
        logger.error(f"Błąd podczas pobierania informacji o dokumentach: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/cleanup-audio")
async def cleanup_audio():
    """Czyści stare pliki audio"""
    try:
        await audio_service.cleanup_old_audio_files()
        return {"message": "Pomyślnie wyczyszczono stare pliki audio"}
    except Exception as e:
        logger.error(f"Błąd podczas czyszczenia audio: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate-audio")
async def generate_audio(request: Dict):
    """Generuje audio z tekstu"""
    try:
        text = request.get("text", "")
        if not text:
            raise HTTPException(status_code=400, detail="Brak tekstu do konwersji")
        
        audio_url = await audio_service.generate_speech(text)
        return {"audio_url": audio_url}
    except Exception as e:
        logger.error(f"Błąd podczas generowania audio: {e}")
        raise HTTPException(status_code=500, detail="Błąd podczas generowania audio")

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """Pobiera plik audio"""
    try:
        import os
        from fastapi.responses import FileResponse
        
        audio_path = os.path.join("static/audio", filename)
        if os.path.exists(audio_path):
            return FileResponse(audio_path, media_type="audio/mpeg")
        else:
            raise HTTPException(status_code=404, detail="Plik audio nie znaleziony")
    except Exception as e:
        logger.error(f"Błąd podczas pobierania pliku audio: {e}")
        raise HTTPException(status_code=500, detail="Błąd podczas pobierania pliku audio")

@app.post("/chat-with-json")
async def chat_with_json(json_data: Dict):
    """Chat z LLM na podstawie danych JSON"""
    try:
        # Konwertuj JSON na tekst
        json_text = json.dumps(json_data, indent=2, ensure_ascii=False)
        
        # Przygotuj wiadomość dla LLM
        system_prompt = """
        Jesteś pomocnym asystentem. Przeanalizuj podane dane JSON i odpowiedz na pytania użytkownika.
        
        Odpowiedzi MUSZĄ być w formacie:
        
        **TLDR:** [Jedna linia z szybką, zwięzłą odpowiedzią]
        
        **Opis:** [Szczegółowy opis z dodatkowymi informacjami, kontekstem i wyjaśnieniami]
        
        Odpowiedzi powinny być:
        - Dokładne i oparte na danych z JSON
        - TLDR powinien być bardzo zwięzły (1-2 zdania)
        - Opis może być dłuższy i zawierać szczegóły
        - W języku polskim
        """
        
        # Wywołaj LLM
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Przeanalizuj te dane JSON i odpowiedz na pytania:\n\n{json_text}"}
        ]
        
        # Użyj LLMService do generowania odpowiedzi
        response = await llm_service.answer_with_context("", [{"content": json_text}])
        
        # Generuj audio tylko dla TLDR (opcjonalnie)
        audio_url = None
        if Config.ELEVENLABS_API_KEY:
            logger.info("🎵 Generowanie audio dla TLDR z JSON...")
            
            # Wyciągnij TLDR z odpowiedzi
            tldr_text = ""
            if "**TLDR:**" in response:
                tldr_part = response.split("**Opis:**")[0]
                tldr_text = tldr_part.replace("**TLDR:**", "").strip()
                logger.info(f"📋 TLDR do audio: '{tldr_text[:50]}...'")
            else:
                # Jeśli nie ma formatu TLDR, użyj całej odpowiedzi
                tldr_text = response
                logger.info(f"📋 Używam całej odpowiedzi do audio: '{tldr_text[:50]}...'")
            
            audio_url = await audio_service.generate_speech(tldr_text)
            if audio_url:
                logger.info(f"✅ Audio wygenerowane dla TLDR: {audio_url}")
            else:
                logger.warning("⚠️ Nie udało się wygenerować audio")
        
        return {"answer": response, "audio_url": audio_url}
        
    except Exception as e:
        logger.error(f"Błąd podczas przetwarzania JSON: {e}")
        raise HTTPException(status_code=500, detail="Błąd podczas przetwarzania JSON")

# Endpointy do zarządzania plikami
@app.post("/files/upload", response_model=FileUploadResponse, tags=["Files"])
async def upload_file(file: UploadFile = File(...)):
    """
    Wrzuca pojedynczy plik do systemu.
    
    - **file**: Plik do wrzucenia (PDF, TXT, DOCX)
    
    Zwraca informacje o wrzuconym pliku.
    """
    try:
        # Sprawdź rozmiar pliku
        file_size = 0
        content = await file.read()
        file_size = len(content)
        
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
        
        # Przygotuj informacje o pliku
        file_info = FileInfo(
            filename=file.filename,
            size=file_size,
            created_at=datetime.now(),
            content_type=file.content_type,
            path=str(file_path)
        )
        
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
        
        # Zbierz informacje o plikach
        for file_path in upload_dir.glob("*.*"):
            if file_path.suffix.lower() in ['.pdf', '.txt', '.docx']:
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