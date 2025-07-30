import os
import asyncio
import json
from openai import OpenAI
from simplybot.config import Config
from simplybot.services.llm_service import LLMService

def test_openai_connection():
    """Tests connection to OpenAI API"""
    try:
        if not Config.OPENAI_API_KEY:
            print("❌ No OpenAI API key - set OPENAI_API_KEY in environment variables")
            return False
        
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        # Test prostego zapytania
        response = client.chat.completions.create(
            model=Config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": "Jesteś pomocnym asystentem."},
                {"role": "user", "content": "Odpowiedz po polsku: Jak się masz?"}
            ],
            max_tokens=50,
            temperature=0.7
        )
        
        print("✅ OpenAI connection works correctly!")
        print(f"   Model: {Config.OPENAI_MODEL}")
        print(f"   Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ OpenAI connection error: {e}")
        return False

async def test_llm_service():
    """Testuje LLMService z konfiguracją OpenAI"""
    try:
        print("\n" + "="*50)
        print("TEST LLM SERVICE Z OPENAI")
        print("="*50)
        
        # Sprawdź konfigurację
        if not Config.OPENAI_API_KEY:
            print("❌ Brak klucza OpenAI API")
            return False
        
        # Utwórz instancję LLMService
        llm_service = LLMService()
        print("✅ LLMService zainicjalizowany pomyślnie")
        
        # Test podsumowywania rozmowy
        print("\n--- Test podsumowywania rozmowy ---")
        conversation = [
            {"role": "user", "content": "Cześć, mam pytanie o produkty firmy"},
            {"role": "assistant", "content": "Dzień dobry! Chętnie pomogę. Jakie produkty Cię interesują?"},
            {"role": "user", "content": "Szukam informacji o oprogramowaniu do zarządzania projektami"}
        ]
        
        summary = await llm_service.summarize_conversation(conversation)
        print(f"Podsumowanie: {summary}")
        
        # Test odpowiedzi z kontekstem
        print("\n--- Test odpowiedzi z kontekstem ---")
        context_docs = [
            {
                "content": "Nasza firma oferuje system zarządzania projektami SimplyProject. System umożliwia planowanie zadań, śledzenie postępów i zarządzanie zespołem.",
                "metadata": {"source": "produkty.txt"}
            },
            {
                "content": "SimplyProject jest dostępny w trzech wersjach: Basic, Professional i Enterprise. Każda wersja ma różne funkcjonalności i limity użytkowników.",
                "metadata": {"source": "cennik.txt"}
            }
        ]
        
        question = "Jakie funkcje ma SimplyProject?"
        answer = await llm_service.answer_with_context(question, context_docs)
        print(f"Pytanie: {question}")
        print(f"Odpowiedź: {answer}")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd podczas testowania LLMService: {e}")
        return False

def test_openai_embeddings():
    """Testuje generowanie embeddings przez OpenAI"""
    try:
        if not Config.OPENAI_API_KEY:
            print("❌ Brak klucza OpenAI API")
            return False
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Test generowania embedding
        test_text = "To jest przykładowy tekst do testowania embeddings OpenAI."
        
        response = client.embeddings.create(
            model="text-embedding-3-small",
            input=test_text
        )
        
        embedding = response.data[0].embedding
        print("✅ Embedding OpenAI wygenerowany pomyślnie!")
        print(f"   Wymiary: {len(embedding)}")
        print(f"   Model: text-embedding-3-small")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd podczas generowania embedding: {e}")
        return False

def test_openai_models():
    """Testuje dostępne modele OpenAI"""
    try:
        if not Config.OPENAI_API_KEY:
            print("❌ Brak klucza OpenAI API")
            return False
        
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Pobierz listę dostępnych modeli
        models = client.models.list()
        
        print("✅ Dostępne modele OpenAI:")
        for model in models.data:
            if "gpt" in model.id or "embedding" in model.id:
                print(f"   - {model.id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Błąd podczas pobierania modeli: {e}")
        return False

async def run_all_tests():
    """Uruchamia wszystkie testy OpenAI"""
    print("="*60)
    print("TESTY OPENAI DLA SIMPLYBOT")
    print("="*60)
    
    # Test połączenia
    connection_ok = test_openai_connection()
    
    if connection_ok:
        # Test LLM Service
        await test_llm_service()
        
        # Test embeddings
        test_openai_embeddings()
        
        # Test modeli
        test_openai_models()
    
    print("\n" + "="*60)
    print("TESTY ZAKOŃCZONE")
    print("="*60)

if __name__ == "__main__":
    # Uruchom testy asynchronicznie
    asyncio.run(run_all_tests()) 