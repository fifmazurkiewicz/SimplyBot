# API Reference

## Endpoints

### GET /

Sprawdza status wszystkich usług systemu.

**Response:**
```json
{
  "status": "ok",
  "timestamp": "2024-01-01T12:00:00",
  "services": {
    "openai": "ok",
    "qdrant": "ok",
    "elevenlabs": "ok",
    "embeddings": "bge"
  }
}
```

### POST /get_more_information

Główny endpoint do komunikacji z chatbotem.

**Request Body:**
```json
{
  "conversation": {
    "session_id": "string",
    "messages": [
      {
        "role": "user|assistant",
        "content": "string"
      }
    ]
  }
}
```

**Response:**
```json
{
  "answer": "string",
  "audio_url": "string|null",
  "confidence": "float",
  "sources": [
    {
      "content": "string",
      "metadata": "object",
      "score": "float"
    }
  ],
  "needs_clarification": "boolean"
}
```

### POST /summarize-conversation

Testuje podsumowanie konwersacji.

**Request Body:**
```json
{
  "conversation": {
    "messages": [
      {
        "role": "user|assistant",
        "content": "string"
      }
    ]
  }
}
```

**Response:**
```json
{
  "summary": {
    "conversation_summary": "string",
    "rag_query": "string",
    "next_action": "string",
    "confidence": "float",
    "reasoning": "string"
  },
  "success": "boolean",
  "message": "string"
}
```

### POST /upload_documents

Upload dokumentów do systemu.

**Request:** Multipart form data z plikami (PDF, DOCX, TXT)

**Response:**
```json
{
  "success": "boolean",
  "message": "string",
  "document_count": "integer"
}
```

### GET /documents/info

Informacje o przetworzonych dokumentach.

**Response:**
```json
{
  "status": "ok",
  "collection_name": "string",
  "vector_count": "integer",
  "documents": [
    {
      "filename": "string",
      "chunks": "integer",
      "upload_date": "datetime"
    }
  ]
}
```

### POST /generate-audio

Generowanie audio z tekstu.

**Request Body:**
```json
{
  "text": "string"
}
```

**Response:**
```json
{
  "audio_url": "string"
}
```

### GET /audio/{filename}

Pobiera plik audio.

**Response:** Audio file (MP3)

### POST /chat-with-json

Chat z LLM na podstawie danych JSON.

**Request Body:**
```json
{
  "any": "json data"
}
```

**Response:**
```json
{
  "answer": "string",
  "audio_url": "string|null"
}
```

### POST /files/upload

Upload pojedynczego pliku.

**Request:** Multipart form data z plikiem

**Response:**
```json
{
  "success": "boolean",
  "filename": "string",
  "message": "string"
}
```

### GET /files

Lista wszystkich plików.

**Response:**
```json
{
  "files": [
    {
      "filename": "string",
      "size": "integer",
      "upload_date": "datetime"
    }
  ]
}
```

### DELETE /files/{filename}

Usuwa plik.

**Response:**
```json
{
  "success": "boolean",
  "message": "string"
}
```

## Error Codes

- `400` - Bad Request
- `401` - Unauthorized
- `404` - Not Found
- `500` - Internal Server Error

## Authentication

API nie wymaga autoryzacji, ale wymaga skonfigurowanych kluczy API w zmiennych środowiskowych:

- `OPENAI_API_KEY` lub `OPENROUTER_API_KEY` - dla modeli językowych
- `ELEVENLABS_API_KEY` - dla syntezy mowy (opcjonalne)
- `QDRANT_URL` - dla bazy danych wektorowej