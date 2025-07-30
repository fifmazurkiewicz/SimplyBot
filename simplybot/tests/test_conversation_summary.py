import requests
import json
from simplybot.config import Config

def test_conversation_summary():
    """Test podsumowania rozmowy z zabezpieczeniem"""
    print("="*60)
    print("TEST PODSUMOWANIA ROZMOWY Z ZABEZPIECZENIEM")
    print("="*60)
    
    API_BASE_URL = "http://localhost:8000"
    
    # Test 1: Single message with question
print("\n🧪 TEST 1: Single message with question")
    question_conversation = {
        "conversation": {
            "messages": [
                {"role": "user", "content": "How does SimplyProject work?"}
            ]
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/summarize-conversation", json=question_conversation)
        if response.status_code == 200:
            result = response.json()
            summary = result["summary"]
            print(f"✅ Status: {summary['next_action']}")
            print(f"📊 Pewność: {summary['confidence']}")
            print(f"💭 Uzasadnienie: {summary['reasoning']}")
            print(f"📝 Podsumowanie: {summary['conversation_summary']}")
            print(f"❓ Zapytanie: {summary['rag_query']}")
        else:
            print(f"❌ Błąd: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")
    
    # Test 2: Normalna rozmowa
    print("\n🧪 TEST 2: Normalna rozmowa")
    normal_conversation = {
        "conversation": {
            "messages": [
                {"role": "user", "content": "Cześć, mam pytanie o SimplyProject"},
                {"role": "assistant", "content": "Witaj! Chętnie pomogę Ci z SimplyProject. O co konkretnie chcesz się dowiedzieć?"},
                {"role": "user", "content": "Jakie są główne funkcje tego systemu?"}
            ]
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/summarize-conversation", json=normal_conversation)
        if response.status_code == 200:
            result = response.json()
            summary = result["summary"]
            print(f"✅ Status: {summary['next_action']}")
            print(f"📊 Pewność: {summary['confidence']}")
            print(f"💭 Uzasadnienie: {summary['reasoning']}")
            print(f"📝 Podsumowanie: {summary['conversation_summary']}")
            print(f"❓ Zapytanie: {summary['rag_query']}")
        else:
            print(f"❌ Błąd: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")
    
    # Test 3: Rozmowa z bardzo krótką ostatnią wiadomością
    print("\n🧪 TEST 3: Krótka ostatnia wiadomość")
    short_last_message = {
        "conversation": {
            "messages": [
                {"role": "user", "content": "Cześć, mam pytanie o SimplyProject"},
                {"role": "assistant", "content": "Witaj! Chętnie pomogę Ci z SimplyProject. O co konkretnie chcesz się dowiedzieć?"},
                {"role": "user", "content": "ok"}
            ]
        }
    }
    
    # Test 4: Stwierdzenie/problem
    print("\n🧪 TEST 4: Stwierdzenie/problem")
    statement_conversation = {
        "conversation": {
            "messages": [
                {"role": "user", "content": "Mam problem z logowaniem do systemu"}
            ]
        }
    }
    
    # Test 5: Opis sytuacji
    print("\n🧪 TEST 5: Opis sytuacji")
    situation_conversation = {
        "conversation": {
            "messages": [
                {"role": "user", "content": "Wczoraj próbowałem skonfigurować SimplyProject ale nie udało mi się"}
            ]
        }
    }
    
    # Test 6: Zbyt krótka wiadomość
    print("\n🧪 TEST 6: Zbyt krótka wiadomość")
    very_short_conversation = {
        "conversation": {
            "messages": [
                {"role": "user", "content": "hi"}
            ]
        }
    }
    
    try:
        response = requests.post(f"{API_BASE_URL}/summarize-conversation", json=short_last_message)
        if response.status_code == 200:
            result = response.json()
            summary = result["summary"]
            print(f"✅ Status: {summary['next_action']}")
            print(f"📊 Pewność: {summary['confidence']}")
            print(f"💭 Uzasadnienie: {summary['reasoning']}")
            print(f"📝 Podsumowanie: {summary['conversation_summary']}")
            print(f"❓ Zapytanie: {summary['rag_query']}")
        else:
            print(f"❌ Błąd: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")
    
    # Test 4: Stwierdzenie/problem
    try:
        response = requests.post(f"{API_BASE_URL}/summarize-conversation", json=statement_conversation)
        if response.status_code == 200:
            result = response.json()
            summary = result["summary"]
            print(f"✅ Status: {summary['next_action']}")
            print(f"📊 Pewność: {summary['confidence']}")
            print(f"💭 Uzasadnienie: {summary['reasoning']}")
            print(f"📝 Podsumowanie: {summary['conversation_summary']}")
            print(f"❓ Zapytanie: {summary['rag_query']}")
        else:
            print(f"❌ Błąd: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")
    
    # Test 5: Opis sytuacji
    try:
        response = requests.post(f"{API_BASE_URL}/summarize-conversation", json=situation_conversation)
        if response.status_code == 200:
            result = response.json()
            summary = result["summary"]
            print(f"✅ Status: {summary['next_action']}")
            print(f"📊 Pewność: {summary['confidence']}")
            print(f"💭 Uzasadnienie: {summary['reasoning']}")
            print(f"📝 Podsumowanie: {summary['conversation_summary']}")
            print(f"❓ Zapytanie: {summary['rag_query']}")
        else:
            print(f"❌ Błąd: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")
    
    # Test 6: Zbyt krótka wiadomość
    try:
        response = requests.post(f"{API_BASE_URL}/summarize-conversation", json=very_short_conversation)
        if response.status_code == 200:
            result = response.json()
            summary = result["summary"]
            print(f"✅ Status: {summary['next_action']}")
            print(f"📊 Pewność: {summary['confidence']}")
            print(f"💭 Uzasadnienie: {summary['reasoning']}")
            print(f"📝 Podsumowanie: {summary['conversation_summary']}")
            print(f"❓ Zapytanie: {summary['rag_query']}")
        else:
            print(f"❌ Błąd: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")

def test_full_conversation_flow():
    """Test pełnego przepływu rozmowy"""
    print("\n" + "="*60)
    print("TEST PEŁNEGO PRZEPŁYWU ROZMOWY")
    print("="*60)
    
    API_BASE_URL = "http://localhost:8000"
    
    # Test 1: Konkretne pytanie (powinno przejść do RAG)
    print("\n🧪 TEST 1: Konkretne pytanie w pełnym przepływie")
    question_conversation = {
        "conversation": {
            "messages": [
                {"role": "user", "content": "Jakie są główne funkcje SimplyProject?"}
            ],
            "session_id": "test_session"
        }
    }
    
    # Test 2: Zbyt krótka wiadomość (powinno dopytac)
    print("\n🧪 TEST 2: Zbyt krótka wiadomość w pełnym przepływie")
    short_conversation = {
        "conversation": {
            "messages": [
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "Witaj! Jak mogę Ci pomóc?"},
                {"role": "user", "content": "ok"}
            ],
            "session_id": "test_session"
        }
    }
    
    # Test 1: Konkretne pytanie
    try:
        response = requests.post(f"{API_BASE_URL}/get_more_information", json=question_conversation)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Odpowiedź: {result.get('answer', 'Brak odpowiedzi')[:100]}...")
            print(f"🤔 Wymaga dopytania: {result.get('needs_clarification', False)}")
            print(f"📊 Pewność: {result.get('confidence', 0)}")
        else:
            print(f"❌ Błąd: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")
    
    # Test 2: Zbyt krótka wiadomość
    try:
        response = requests.post(f"{API_BASE_URL}/get_more_information", json=short_conversation)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Odpowiedź: {result.get('answer', 'Brak odpowiedzi')[:100]}...")
            print(f"🤔 Wymaga dopytania: {result.get('needs_clarification', False)}")
            print(f"📊 Pewność: {result.get('confidence', 0)}")
        else:
            print(f"❌ Błąd: {response.status_code}")
    except Exception as e:
        print(f"❌ Błąd połączenia: {e}")

if __name__ == "__main__":
    test_conversation_summary()
    test_full_conversation_flow()
    
    print("\n" + "="*60)
    print("✅ TESTY ZAKOŃCZONE")
    print("="*60) 