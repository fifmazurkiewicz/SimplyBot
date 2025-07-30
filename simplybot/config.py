import os
from dotenv import load_dotenv

load_dotenv(r'C:\Users\MSI\PycharmProjects\SimplyBot\.env')

class Config:
    # OpenRouter (główna konfiguracja dla LLM)
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o")
    
    # OpenAI (główna konfiguracja dla embeddings)
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    
    # Qdrant
    QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "simplybot_docs")
    
    # ElevenLabs
    ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")
    ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")  
    
    # App settings
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "1000"))
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    
    # Embedding settings
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "openai")
    BGE_MODEL_NAME = os.getenv("BGE_MODEL_NAME", "BAAI/bge-m3")
    OPENAI_EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
    
    # File upload settings
    UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
    MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10"))  # MB 


if __name__ == "__main__":
    print(Config.OPENAI_API_KEY)
    print(Config.OPENAI_MODEL)
    print(Config.OPENROUTER_API_KEY)
    print(Config.OPENROUTER_MODEL)
    print(Config.QDRANT_URL)
    print(Config.QDRANT_API_KEY)
    print(Config.QDRANT_COLLECTION_NAME)
    print(Config.ELEVENLABS_API_KEY)
    print(Config.ELEVENLABS_VOICE_ID)
    print(Config.MAX_TOKENS)
    print(Config.TEMPERATURE)   