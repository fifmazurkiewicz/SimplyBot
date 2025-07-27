import requests
import json
from sentence_transformers import SentenceTransformer

def generate_bge_embedding(text, model_name="BAAI/bge-m3"):
    """Generuje embedding używając modelu BGE"""
    try:
        # Załaduj model
        model = SentenceTransformer(model_name)
        
        # BGE wymaga specjalnego formatowania dla wyszukiwania
        if not text.startswith("Represent this sentence for searching relevant passages: "):
            formatted_text = f"Represent this sentence for searching relevant passages: {text}"
        else:
            formatted_text = text
        
        # Generuj embedding
        embedding = model.encode(formatted_text)
        return embedding.tolist()
        
    except Exception as e:
        print(f"Błąd podczas generowania embedding: {e}")
        return None

def insert_point(collection_name, point_id, vector, payload):
    url = f"http://localhost:6333/collections/{collection_name}/points?wait=true"
    headers = {"Content-Type": "application/json"}
    data = {
        "points": [
            {
                "id": point_id,
                "vector": vector,
                "payload": payload
            }
        ]
    }
    response = requests.put(url, headers=headers, data=json.dumps(data))
    if response.status_code == 200:
        print("Punkt dodany pomyślnie!")
    else:
        print(f"Błąd dodawania punktu: {response.status_code} {response.text}")

def search_similar(collection_name, query_text, limit=5):
    """Wyszukuje podobne dokumenty używając BGE embeddings"""
    try:
        # Generuj embedding dla zapytania
        query_vector = generate_bge_embedding(query_text)
        
        if not query_vector:
            print("Nie udało się wygenerować embedding dla zapytania!")
            return
        
        url = f"http://localhost:6333/collections/{collection_name}/points/search"
        headers = {"Content-Type": "application/json"}
        data = {
            "vector": query_vector,
            "limit": limit,
            "with_payload": True
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(data))
        
        if response.status_code == 200:
            results = response.json()
            print(f"\nZnaleziono {len(results['result'])} podobnych dokumentów:")
            
            for i, result in enumerate(results['result'], 1):
                score = result['score']
                content = result['payload'].get('content', 'Brak treści')
                source = result['payload'].get('metadata', {}).get('source', 'Nieznane')
                
                print(f"{i}. Score: {score:.4f}")
                print(f"   Źródło: {source}")
                print(f"   Treść: {content[:100]}...")
                print()
        else:
            print(f"Błąd wyszukiwania: {response.status_code} {response.text}")
            
    except Exception as e:
        print(f"Błąd podczas wyszukiwania: {e}")

def get_collection_info(collection_name):
    """Pobiera informacje o kolekcji"""
    try:
        url = f"http://localhost:6333/collections/{collection_name}"
        response = requests.get(url)
        
        if response.status_code == 200:
            info = response.json()
            print(f"\nInformacje o kolekcji '{collection_name}':")
            print(f"  Status: {info['result']['status']}")
            print(f"  Liczba punktów: {info['result']['vectors_count']}")
            print(f"  Wymiary: {info['result']['config']['params']['vectors']['size']}")
        else:
            print(f"Błąd pobierania informacji o kolekcji: {response.status_code}")
            
    except Exception as e:
        print(f"Błąd podczas pobierania informacji o kolekcji: {e}")

if __name__ == "__main__":
    collection = "simplybot_docs"
    
    print("="*50)
    print("TEST BGE EMBEDDINGS Z QDRANT")
    print("="*50)
    
    # Sprawdź informacje o kolekcji
    get_collection_info(collection)
    
    # Przykładowy tekst do przetestowania
    test_text = "To jest przykładowy dokument testowy z embeddingiem BGE. Zawiera informacje o produktach i usługach."
    
    print(f"Generowanie embedding dla tekstu: '{test_text}'")
    
    # Generuj embedding używając BGE
    vector = generate_bge_embedding(test_text)
    
    if vector:
        print(f"Wygenerowano embedding o wymiarach: {len(vector)}")
        
        payload = {
            "content": test_text,
            "metadata": {
                "source": "test_bge",
                "title": "Test dokument BGE",
                "content_type": "test",
                "added_at": "2024-01-01T00:00:00"
            }
        }
        
        insert_point(collection, 1, vector, payload)
        
        # Test wyszukiwania
        print("\n" + "="*50)
        print("TEST WYSZUKIWANIA")
        print("="*50)
        
        search_queries = [
            "produkty i usługi",
            "dokument testowy",
            "informacje o firmie",
            "embedding BGE"
        ]
        
        for query in search_queries:
            print(f"\nWyszukiwanie: '{query}'")
            search_similar(collection, query, limit=3)
            
    else:
        print("Nie udało się wygenerować embedding!")
