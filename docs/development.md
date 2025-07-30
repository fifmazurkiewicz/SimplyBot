# Rozwój SimplyBot

## Struktura projektu

```text
simplybot/
├── main.py              # Główny plik FastAPI
├── config.py            # Konfiguracja aplikacji
├── models.py            # Modele Pydantic
├── services/            # Serwisy biznesowe
│   ├── llm_service.py
│   ├── vector_store.py
│   ├── document_processor.py
│   └── audio_service.py
├── gui/                 # Interfejs użytkownika (Streamlit)
│   └── streamlit_app.py
└── tests/               # Testy jednostkowe
    ├── test_api.py
    └── test_services.py
```

## Konfiguracja środowiska deweloperskiego

1. Zainstaluj główne zależności projektu:

   ```bash
   pip install -r requirements.txt
   ```

2. Zainstaluj zależności dokumentacji (opcjonalnie, ale zalecane):

   ```bash
   pip install -r requirements-docs.txt
   ```

3. Skonfiguruj zmienne środowiskowe kopiując plik przykładowy i uzupełniając wymagane klucze API:

   ```bash
   cp env.example .env
   # edytuj .env
   ```

## Uruchamianie aplikacji w trybie deweloperskim

```bash
# Terminal 1: Backend API
uvicorn simplybot.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Interfejs Streamlit
streamlit run simplybot/gui/streamlit_app.py
```

Po uruchomieniu aplikacji interfejs będzie dostępny pod adresem `http://localhost:8501`, a dokumentacja FastAPI pod `http://localhost:8000/docs`.

## Testowanie

Aby uruchomić wszystkie testy jednostkowe oraz sprawdzić pokrycie kodu, wykonaj:

```bash
pytest --cov=simplybot
```

Przykładowe uruchomienie pojedynczego pliku testowego:

```bash
pytest simplybot/tests/test_api.py
```

## Formatowanie i linting

Projekt wykorzystuje Black oraz Flake8. Aby sformatować kod i sprawdzić błędy lintera:

```bash
black simplybot/
flake8 simplybot/
```

## Dodawanie nowych funkcjonalności

1. Utwórz nową gałąź:

   ```bash
git checkout -b feature/nazwa-funkcjonalnosci
   ```

2. Zaimplementuj zmiany w odpowiednich modułach w folderze `simplybot/`.
3. Dodaj lub uaktualnij testy jednostkowe w `simplybot/tests/`.
4. Zaktualizuj dokumentację w folderze `docs/`.
5. Uruchom testy i upewnij się, że wszystkie przechodzą.
6. Wypchnij zmiany i utwórz Pull Request.

## Generowanie i podgląd dokumentacji

```bash
# Generowanie statycznej strony (do folderu site/)
mkdocs build

# Podgląd na żywo podczas edycji
mkdocs serve
```

---

Masz pytania lub napotkałeś problem? Otwórz issue na GitHubie lub dołącz do naszego Discorda! :rocket:
