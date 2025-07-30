# Instalacja SimplyBot

## Wymagania wstępne

- Python 3.10 lub nowszy
- Git
- Dostęp do internetu

## Krok 1: Klonowanie repozytorium

```bash
git clone https://github.com/your-username/SimplyBot.git
cd SimplyBot
```

## Krok 2: Instalacja zależności

```bash
pip install -r requirements.txt
```

## Krok 3: Konfiguracja zmiennych środowiskowych

Skopiuj plik przykładu:
```bash
cp env.example .env
```

Edytuj plik `.env` i dodaj swoje klucze API:

```env
# OpenAI API Key (wymagane)
OPENAI_API_KEY=your_openai_api_key_here

# Alternatywnie, OpenRouter API Key
OPENROUTER_API_KEY=your_openrouter_api_key_here

# Qdrant URL (domyślnie lokalny)
QDRANT_URL=http://localhost:6333

# ElevenLabs API Key (opcjonalne)
ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
```

## Krok 4: Uruchomienie Qdrant

### Opcja A: Docker (zalecane)
```bash
docker run -p 6333:6333 qdrant/qdrant
```

### Opcja B: Instalacja lokalna
Pobierz Qdrant z [oficjalnej strony](https://qdrant.tech/documentation/guides/installation/) i uruchom lokalnie.

## Krok 5: Uruchomienie aplikacji

### Terminal 1: API Backend
```bash
uvicorn simplybot.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Interfejs webowy
```bash
streamlit run simplybot/gui/streamlit_app.py
```

## Weryfikacja instalacji

1. Otwórz przeglądarkę i przejdź do `http://localhost:8501`
2. Sprawdź status usług w panelu bocznym
3. Wszystkie usługi powinny pokazywać status "ok"

## Rozwiązywanie problemów

### Problem: Błąd połączenia z Qdrant
- Upewnij się, że Qdrant jest uruchomiony na porcie 6333
- Sprawdź URL w pliku `.env`

### Problem: Błąd API Key
- Sprawdź czy klucze API są poprawnie ustawione w `.env`
- Upewnij się, że masz środki na koncie OpenAI/OpenRouter

### Problem: Błąd importu modułów
- Upewnij się, że wszystkie zależności są zainstalowane: `pip install -r requirements.txt`
- Sprawdź czy używasz Python 3.10+ 