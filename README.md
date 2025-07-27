# 🤖 SimplyBot - Bot Dialogowy z RAG

Bot dialogowy wykorzystujący Retrieval-Augmented Generation (RAG) z LangChain, Qdrant i ElevenLabs.

## 🚀 Funkcjonalności

- **Rozmowa z botem** - inteligentne odpowiedzi na podstawie kontekstu
- **RAG (Retrieval-Augmented Generation)** - wyszukiwanie w bazie wiedzy
- **Wrzucanie dokumentów** - obsługa PDF, TXT, DOCX
- **Generowanie audio** - ElevenLabs TTS
- **Interfejs webowy** - Streamlit GUI
- **REST API** - FastAPI backend
- **Wielu dostawców LLM** - OpenRouter (GPT-4, Claude, Gemini, Llama)

## 🌟 Dlaczego OpenRouter?

- **Jeden API** - dostęp do wielu modeli (OpenAI, Anthropic, Google, Meta)
- **Lepsze ceny** - często tańsze niż bezpośrednie API
- **Większa dostępność** - alternatywa gdy OpenAI ma problemy
- **Łatwe przełączanie** - zmień model bez zmiany kodu
- **Darmowe kredyty** - dla nowych użytkowników

## 📋 Wymagania

- Python 3.9+
- Poetry
- Qdrant (lokalnie lub w chmurze)
- Klucze API:
  - OpenRouter (zalecane) lub OpenAI
  - ElevenLabs (opcjonalnie)

## 🛠️ Instalacja

### Konfiguracja OpenRouter

1. **Zarejestruj się na [OpenRouter](https://openrouter.ai)**
2. **Wygeneruj API key**
3. **Wybierz model** - dostępne modele:
   - `openai/gpt-4o` - GPT-4 Omni
   - `openai/gpt-4-turbo` - GPT-4 Turbo
   - `anthropic/claude-3-opus` - Claude 3 Opus
   - `anthropic/claude-3-sonnet` - Claude 3 Sonnet
   - `google/gemini-pro` - Gemini Pro
   - `meta-llama/llama-3.1-70b-instruct` - Llama 3.1 70B

📖 **Pełna lista modeli**: [openrouter_models.md](openrouter_models.md)

### Instalacja aplikacji

1. **Sklonuj repozytorium**
```bash
git clone <repository-url>
cd SimplyBot
```

2. **Zainstaluj Poetry (jeśli nie masz)**
```bash
pip install poetry
```

3. **Zainstaluj zależności**
```bash
poetry install
```

4. **Skonfiguruj zmienne środowiskowe**
```bash
cp env.example .env
# Edytuj .env i dodaj swoje klucze API
```

5. **Uruchom Qdrant**

**Lokalnie (zalecane dla rozwoju):**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

**W chmurze (Qdrant Cloud):**
- Utwórz konto na [cloud.qdrant.io](https://cloud.qdrant.io)
- Skopiuj URL i API key do `.env`

## 🚀 Uruchomienie

### Opcja 1: Użyj skryptów Poetry

**Uruchom API:**
```bash
poetry run start-api
```

**Uruchom GUI:**
```bash
poetry run start-gui
```

### Opcja 2: Ręczne uruchomienie

**API (port 8000):**
```bash
poetry run uvicorn simplybot.main:app --reload --host 0.0.0.0 --port 8000
```

**GUI (port 8501):**
```bash
poetry run streamlit run simplybot/gui/streamlit_app.py
```

## 📖 Użycie

### 1. Wrzuć dokumenty
- Otwórz GUI w przeglądarce: `http://localhost:8501`
- W sidebarze wybierz pliki (PDF, TXT, DOCX)
- Kliknij "Wrzuć dokumenty"

### 2. Rozmawiaj z botem
- Wpisz pytanie w polu czatu
- Bot przeanalizuje rozmowę i znajdzie odpowiednie dokumenty
- Otrzymasz odpowiedź z kontekstem i opcjonalnie audio

### 3. API Endpoints

**Sprawdź stan usług:**
```bash
GET http://localhost:8000/
```

**Wyślij rozmowę:**
```bash
POST http://localhost:8000/get_more_information
Content-Type: application/json

{
  "conversation": {
    "messages": [
      {"role": "user", "content": "Jakie są zasady zwrotu?"},
      {"role": "assistant", "content": "Zgodnie z dokumentami..."}
    ]
  }
}
```

**Wrzuć dokumenty:**
```bash
POST http://localhost:8000/upload_documents
Content-Type: multipart/form-data

files: [plik1.pdf, plik2.txt]
```

## 🔧 Konfiguracja

### Zmienne środowiskowe (.env)

```env
# OpenRouter (zalecane)
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
OPENROUTER_MODEL=openai/gpt-4o

# OpenAI (opcjonalnie)
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_MODEL=gpt-3.5-turbo

# Qdrant
QDRANT_URL=http://localhost:6333
# QDRANT_API_KEY=  # Nie potrzebne dla lokalnej instalacji
QDRANT_COLLECTION_NAME=simplybot_docs

# Dla Qdrant Cloud użyj:
# QDRANT_URL=https://your-cluster.qdrant.io
# QDRANT_API_KEY=your_cloud_api_key

# ElevenLabs (opcjonalnie)
ELEVENLABS_API_KEY=your_key_here
ELEVENLABS_VOICE_ID=21m00Tcm4TlvDq8ikWAM

# Aplikacja
MAX_TOKENS=1000
TEMPERATURE=0.7
MAX_FILE_SIZE=10
```

## 🧪 Testowanie z Insomnia

1. **Importuj kolekcję Insomnia**
2. **Ustaw zmienne środowiskowe**
3. **Testuj endpointy**

Przykładowe zapytanie do `get_more_information`:
```json
{
  "conversation": {
    "messages": [
      {
        "role": "user",
        "content": "Jakie są warunki gwarancji?"
      }
    ]
  }
}
```

## 📁 Struktura projektu

```
SimplyBot/
├── simplybot/
│   ├── __init__.py
│   ├── main.py              # FastAPI aplikacja
│   ├── config.py            # Konfiguracja
│   ├── models.py            # Modele Pydantic
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py   # Serwis LLM
│   │   ├── vector_store.py  # Serwis Qdrant
│   │   ├── audio_service.py # Serwis ElevenLabs
│   │   └── document_processor.py
│   └── gui/
│       ├── __init__.py
│       └── streamlit_app.py # Interfejs Streamlit
├── static/                  # Pliki statyczne (audio)
├── pyproject.toml          # Konfiguracja Poetry
├── env.example             # Przykład zmiennych środowiskowych
└── README.md
```

## 🔍 Debugowanie

### Logi
```bash
# Włącz debug logging
export LOG_LEVEL=DEBUG
poetry run start-api
```

### Sprawdź stan usług
```bash
curl http://localhost:8000/
```

### Sprawdź dokumenty w Qdrant
```bash
curl http://localhost:8000/documents/info
```

## 🚨 Rozwiązywanie problemów

### API nie odpowiada
- Sprawdź czy Qdrant działa: `docker ps`
- Sprawdź klucze API w `.env`
- Sprawdź logi aplikacji

### Błąd podczas wrzucania dokumentów
- Sprawdź format pliku (PDF, TXT, DOCX)
- Sprawdź rozmiar pliku (max 10MB)
- Sprawdź połączenie z Qdrant

### Brak audio
- Sprawdź klucz ElevenLabs API
- Sprawdź czy katalog `static/audio` istnieje
- Sprawdź uprawnienia do zapisu

## 🤝 Wkład

1. Fork projektu
2. Utwórz branch (`git checkout -b feature/amazing-feature`)
3. Commit zmiany (`git commit -m 'Add amazing feature'`)
4. Push do branch (`git push origin feature/amazing-feature`)
5. Otwórz Pull Request

## 📄 Licencja

Ten projekt jest licencjonowany pod MIT License.

## 🙏 Podziękowania

- [LangChain](https://langchain.com/) - Framework dla aplikacji LLM
- [Qdrant](https://qdrant.tech/) - Vector database
- [ElevenLabs](https://elevenlabs.io/) - Text-to-Speech
- [FastAPI](https://fastapi.tiangolo.com/) - Web framework
- [Streamlit](https://streamlit.io/) - Web app framework