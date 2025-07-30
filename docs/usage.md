# Użycie SimplyBot

## Uruchomienie aplikacji

1. **Uruchom API Backend**:
   ```bash
   uvicorn simplybot.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Uruchom interfejs webowy**:
   ```bash
   streamlit run simplybot/gui/streamlit_app.py
   ```

3. **Otwórz przeglądarkę** i przejdź do `http://localhost:8501`

## Podstawowe funkcjonalności

### 1. Upload dokumentów

1. W panelu bocznym kliknij "Upload Documents"
2. Wybierz pliki (PDF, DOCX, TXT)
3. Kliknij "Upload"
4. Poczekaj na przetworzenie dokumentów

### 2. Chat z botem

1. W głównym oknie wpisz swoje pytanie
2. Naciśnij Enter lub kliknij "Send"
3. Bot znajdzie odpowiednie fragmenty z dokumentów
4. Wygeneruje odpowiedź na podstawie znalezionych informacji

### 3. Generowanie audio

1. Po otrzymaniu odpowiedzi tekstowej
2. Kliknij ikonę głośnika obok odpowiedzi
3. Poczekaj na wygenerowanie audio
4. Odtwórz dźwięk

### 4. Podgląd dokumentów

1. W panelu bocznym sprawdź sekcję "Documents Info"
2. Zobacz listę przetworzonych dokumentów
3. Sprawdź liczbę fragmentów w każdym dokumencie

## API Endpoints

### Główny endpoint chatu
```bash
POST /get_more_information
```

### Upload dokumentów
```bash
POST /upload_documents
```

### Generowanie audio
```bash
POST /generate-audio
```

### Informacje o dokumentach
```bash
GET /documents/info
```

## Przykłady użycia

### Przykład 1: Pytanie o konkretny temat
```
Użytkownik: "Co to jest RAG?"
Bot: [Znajdzie fragmenty o RAG w dokumentach i wygeneruje odpowiedź]
```

### Przykład 2: Analiza dokumentu
```
Użytkownik: "Podsumuj główne punkty z dokumentu"
Bot: [Przeanalizuje cały dokument i stworzy podsumowanie]
```

### Przykład 3: Porównanie informacji
```
Użytkownik: "Porównaj różnice między X a Y"
Bot: [Znajdzie fragmenty o X i Y, porówna je]
```

## Wskazówki

- **Jakość pytań**: Im bardziej szczegółowe pytanie, tym lepsza odpowiedź
- **Kontekst**: Bot pamięta kontekst rozmowy, możesz odwoływać się do wcześniejszych pytań
- **Dokumenty**: Im więcej dokumentów przetworzysz, tym bogatsza baza wiedzy
- **Audio**: Funkcja audio wymaga klucza ElevenLabs API 