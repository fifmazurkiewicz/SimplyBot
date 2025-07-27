# 🤖 Dostępne modele OpenRouter

## 🏆 Najlepsze modele (zalecane)

| Model | Dostawca | Opis | Cena |
|-------|----------|------|------|
| `openai/gpt-4o` | OpenAI | Najnowszy GPT-4 Omni | $5/1M tokens |
| `openai/gpt-4o-mini` | OpenAI | Szybszy i tańszy GPT-4 | $0.15/1M tokens |
| `anthropic/claude-3-opus` | Anthropic | Najmocniejszy Claude | $15/1M tokens |
| `anthropic/claude-3-sonnet` | Anthropic | Zbalansowany Claude | $3/1M tokens |
| `google/gemini-pro` | Google | Gemini Pro | $0.50/1M tokens |

## 💰 Ekonomiczne modele

| Model | Dostawca | Opis | Cena |
|-------|----------|------|------|
| `openai/gpt-3.5-turbo` | OpenAI | GPT-3.5 Turbo | $0.50/1M tokens |
| `anthropic/claude-3-haiku` | Anthropic | Szybki Claude | $0.25/1M tokens |
| `meta-llama/llama-3.1-8b-instruct` | Meta | Mały Llama | $0.20/1M tokens |
| `mistralai/mistral-7b-instruct` | Mistral | Mistral 7B | $0.14/1M tokens |

## 🚀 Szybkie modele

| Model | Dostawca | Opis | Cena |
|-------|----------|------|------|
| `openai/gpt-4o-mini` | OpenAI | Szybki GPT-4 | $0.15/1M tokens |
| `anthropic/claude-3-haiku` | Anthropic | Najszybszy Claude | $0.25/1M tokens |
| `google/gemini-flash-1.5` | Google | Szybki Gemini | $0.075/1M tokens |

## 🔧 Jak zmienić model

1. **W pliku `.env`:**
```env
OPENROUTER_MODEL=anthropic/claude-3-sonnet
```

2. **W kodzie:**
```python
# Automatycznie użyje modelu z konfiguracji
llm_service = LLMService()
```

## 📊 Porównanie wydajności

### Najlepsze dla:
- **Analiza tekstu**: `openai/gpt-4o`, `anthropic/claude-3-opus`
- **Kodowanie**: `openai/gpt-4o`, `anthropic/claude-3-sonnet`
- **Kreatywność**: `anthropic/claude-3-opus`, `openai/gpt-4o`
- **Szybkość**: `openai/gpt-4o-mini`, `anthropic/claude-3-haiku`
- **Koszt**: `mistralai/mistral-7b-instruct`, `openai/gpt-3.5-turbo`

## 💡 Wskazówki

1. **Rozpocznij z GPT-4o** - najlepszy balans jakości i ceny
2. **Testuj różne modele** - każdy ma swoje mocne strony
3. **Monitoruj koszty** - używaj tańszych modeli dla prostych zadań
4. **Używaj Claude dla analizy** - świetny w rozumieniu kontekstu
5. **Gemini dla szybkości** - dobry dla prostych zapytań

## 🔗 Linki

- [OpenRouter Dashboard](https://openrouter.ai/keys)
- [Lista wszystkich modeli](https://openrouter.ai/models)
- [Cennik](https://openrouter.ai/pricing)
- [Dokumentacja API](https://openrouter.ai/docs) 