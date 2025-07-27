import requests
import json
from openai import OpenAI
from simplybot.config import Config
import os
from dotenv import load_dotenv

def test_openai_embedding_to_qdrant():
    """Test generowania embedding OpenAI large i wgrania do Qdrant"""
    try:
        # Sprawdź klucz OpenAI
        if not Config.OPENAI_API_KEY:
            print("❌ Brak klucza OpenAI API - ustaw OPENAI_API_KEY w zmiennych środowiskowych")
            return False
        # Inicjalizuj klienta OpenAI
        client = OpenAI(api_key=Config.OPENAI_API_KEY)
        
        # Przykładowy tekst
        test_text = "SimplyProject to zaawansowany system zarządzania projektami, który umożliwia planowanie zadań, śledzenie postępów i efektywne zarządzanie zespołem."
        
        print(f"Generowanie embedding dla tekstu: '{test_text}'")
        
        # Generuj embedding używając modelu large
        response = client.embeddings.create(
            model=Config.OPENAI_EMBEDDING_MODEL,
            input=test_text
        )
        
        embedding = response.data[0].embedding
        
        print("✅ Embedding OpenAI wygenerowany pomyślnie!")
        print(f"   Model: {Config.OPENAI_EMBEDDING_MODEL}")
        print(f"   Wymiary: {len(embedding)}")
        
        # Przygotuj payload dla Qdrant
        payload = {
            "content": test_text,
            "metadata": {
                "source": "openai_test",
                "title": "Test SimplyProject",
                "content_type": "product_description",
                "model": Config.OPENAI_EMBEDDING_MODEL,
                "added_at": "2024-01-01T00:00:00"
            }
        }
        
        # Wgraj do Qdrant
        collection_name = Config.QDRANT_COLLECTION_NAME
        url = f"http://localhost:6333/collections/{collection_name}/points?wait=true"
        headers = {"Content-Type": "application/json"}
        data = {
            "points": [
                {
                    "id": 999,  # Unikalny ID dla testu
                    "vector": embedding,
                    "payload": payload
                }
            ]
        }
        
        print(f"Wgrywanie do Qdrant (kolekcja: {collection_name})...")
        
        response = requests.put(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            print("✅ Punkt pomyślnie wgrany do Qdrant!")
            print(f"   ID: 999")
            print(f"   Kolekcja: {collection_name}")
            return True
        else:
            print(f"❌ Błąd wgrywania do Qdrant: {response.status_code} {response.text}")
            return False
        
    except Exception as e:
        print(f"❌ Błąd: {e}")
        return False

if __name__ == "__main__":
    print("="*60)
    print("TEST OPENAI EMBEDDING + QDRANT")
    print("="*60)
    
    success = test_openai_embedding_to_qdrant()
    
    print("\n" + "="*60)
    if success:
        print("✅ TEST ZAKOŃCZONY POMYŚLNIE")
    else:
        print("❌ TEST ZAKOŃCZONY BŁĘDEM")
    print("="*60) 