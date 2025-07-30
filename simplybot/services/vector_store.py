from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings
from sentence_transformers import SentenceTransformer
from simplybot.config import Config
from typing import List, Dict, Any
import logging
import uuid
import numpy as np
import time

logger = logging.getLogger(__name__)

class VectorStoreService:
    def __init__(self):
        # Dla lokalnej instalacji Qdrant nie potrzebujemy API key
        client_kwargs = {"url": Config.QDRANT_URL}
        if Config.QDRANT_API_KEY:
            client_kwargs["api_key"] = Config.QDRANT_API_KEY
        
        self.client = QdrantClient(**client_kwargs)
        
        # Inicjalizacja embeddings
        self.embedding_model = Config.EMBEDDING_MODEL
        self.embeddings = self._initialize_embeddings()
        
        self.collection_name = Config.QDRANT_COLLECTION_NAME
        self._ensure_collection_exists()
    
    def _initialize_embeddings(self):
        """Inicjalizuje model embeddings"""
        if self.embedding_model == "bge":
            try:
                logger.info(f"Ładowanie modelu BGE: {Config.BGE_MODEL_NAME}")
                model = SentenceTransformer(Config.BGE_MODEL_NAME)
                return model
            except Exception as e:
                logger.error(f"Error loading BGE model: {e}")
                raise ValueError(f"Failed to load BGE model: {Config.BGE_MODEL_NAME}")
        
        elif self.embedding_model == "openai":
            # Konfiguracja embeddings - OpenAI API ma priorytet (lepsze embeddings)
            if Config.OPENAI_API_KEY:
                return OpenAIEmbeddings(
                    api_key=Config.OPENAI_API_KEY,
                    model=Config.OPENAI_EMBEDDING_MODEL
                )
            elif Config.OPENROUTER_API_KEY:
                return OpenAIEmbeddings(
                    api_key=Config.OPENROUTER_API_KEY,
                    base_url=Config.OPENROUTER_BASE_URL,
                    model=Config.OPENAI_EMBEDDING_MODEL
                )
            else:
                raise ValueError("No API key for embeddings - set OPENAI_API_KEY or OPENROUTER_API_KEY")
        
        else:
            raise ValueError(f"Nieobsługiwany model embeddings: {self.embedding_model}")
    
    def _get_embedding_dimension(self):
        """Zwraca wymiar embeddings"""
        if self.embedding_model == "bge":
            # BGE-M3 ma 1024 wymiary
            return 1024
        else:
            # OpenAI text-embedding-3-large ma 3072 wymiary
            return 3072
    
    def _encode_text(self, text: str) -> List[float]:
        """Koduje tekst na embeddings"""
        # Logowanie tekstu do embedding
        text_preview = text[:10] + "..." if len(text) > 10 else text
        logger.info(f"🔍 Generating embedding for text: '{text_preview}' (length: {len(text)} characters)")
        
        if self.embedding_model == "bge":
            # BGE wymaga specjalnego formatowania
            if not text.startswith("Represent this sentence for searching relevant passages: "):
                text = f"Represent this sentence for searching relevant passages: {text}"
            
            embedding = self.embeddings.encode(text)
            logger.info(f"✅ BGE embedding wygenerowany - wymiary: {len(embedding)}")
            return embedding.tolist()
        
        else:
            # OpenAI embeddings
            embedding = self.embeddings.embed_query(text)
            logger.info(f"✅ OpenAI embedding wygenerowany - wymiary: {len(embedding)}")
            return embedding
    
    def _ensure_collection_exists(self):
        """Upewnia się, że kolekcja istnieje"""
        try:
            collections = self.client.get_collections()
            collection_names = [col.name for col in collections.collections]
            
            if self.collection_name not in collection_names:
                embedding_dim = self._get_embedding_dimension()
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=embedding_dim,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"Utworzono kolekcję: {self.collection_name} z wymiarami: {embedding_dim}")
        except Exception as e:
            logger.error(f"Error creating collection: {e}")
    
    async def add_documents(self, documents: List[Dict[str, Any]]) -> int:
        """Adds documents to vector store"""
        try:
            added_count = 0
            logger.info(f"📚 Starting to add {len(documents)} documents to vector store")
            
            for i, doc in enumerate(documents):
                # Generate unique ID
                doc_id = str(uuid.uuid4())
                
                # Log document information
                content_preview = doc["content"][:10] + "..." if len(doc["content"]) > 10 else doc["content"]
                logger.info(f"📄 Document {i+1}/{len(documents)}: '{content_preview}' (source: {doc.get('source', 'unknown')})")
                
                # Prepare metadata
                metadata = {
                    "source": doc.get("source", "unknown"),
                    "title": doc.get("title", ""),
                    "content_type": doc.get("content_type", "text"),
                    "added_at": doc.get("added_at", "")
                }
                
                # Dodaj punkt do Qdrant
                point = PointStruct(
                    id=doc_id,
                    vector=self._encode_text(doc["content"]),
                    payload={
                        "content": doc["content"],  
                        "metadata": metadata
                    }
                )
                self.client.upsert(
                    collection_name=self.collection_name,
                    points=[point],
                    wait=True
                )
                added_count += 1
                logger.info(f"✅ Added document {i+1} to Qdrant (ID: {doc_id}...)")
            
            logger.info(f"🎉 Successfully added {added_count} documents to vector store")
            return added_count
            
        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return 0
    
    async def search_documents(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Searches for documents similar to query"""
        try:
            # Log RAG query
            query_preview = query[:10] + "..." if len(query) > 10 else query
            logger.info(f"🔍 RAG SEARCH: '{query_preview}' (limit: {limit})")
            
            # Search in Qdrant
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=self._encode_text(query),
                limit=limit,
                with_payload=True
            )
            
            # Prepare results
            documents = []
            for i, result in enumerate(search_result):
                content_preview = result.payload.get("content", "")[:10] + "..." if len(result.payload.get("content", "")) > 10 else result.payload.get("content", "")
                logger.info(f"📄 Result {i+1}: '{content_preview}' (score: {result.score:.4f})")
                
                doc = {
                    "content": result.payload.get("content", ""),
                    "metadata": result.payload.get("metadata", {}),
                    "score": result.score
                }
                documents.append(doc)
            
            logger.info(f"✅ RAG: Found {len(documents)} documents for query")
            return documents
            
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def get_collection_info(self) -> Dict[str, Any]:
        """Returns collection information"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            # Check if points_count is None and replace with 0
            points_count = collection_info.points_count if collection_info.points_count is not None else 0
            logger.info(f"📊 Collection information: {self.collection_name}, points: {points_count}")
            
            return {
                "name": self.collection_name,
                "points_count": points_count,
                "status": "ok"
            }
        except Exception as e:
            logger.error(f"Error retrieving collection information: {e}")
            return {
                "name": self.collection_name,
                "points_count": 0,
                "status": "error", 
                "message": str(e)
            } 