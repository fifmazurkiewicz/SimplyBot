import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from typing import List, Dict, Any
import tempfile

# Konfiguracja strony
st.set_page_config(
    page_title="SimplyBot - Bot Dialogowy z RAG",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Konfiguracja API
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Sprawdza stan API"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.json()
    except:
        return None

def upload_documents(files):
    """Wrzuca dokumenty do API"""
    try:
        files_data = []
        for file in files:
            files_data.append(("files", (file.name, file.getvalue(), file.type)))
        
        response = requests.post(f"{API_BASE_URL}/upload_documents", files=files_data)
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_more_information(conversation):
    """Wysyła rozmowę do API i otrzymuje odpowiedź"""
    try:
        payload = {
            "conversation": {
                "messages": conversation,
                "session_id": st.session_state.get("session_id", "default")
            }
        }
        
        response = requests.post(f"{API_BASE_URL}/get_more_information", json=payload)
        return response.json()
    except Exception as e:
        return {"answer": f"Błąd: {str(e)}", "audio_url": None}

def get_documents_info():
    """Pobiera informacje o dokumentach"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/info")
        return response.json()
    except:
        return None

def generate_audio_from_text(text):
    """Generuje audio z tekstu"""
    try:
        response = requests.post(f"{API_BASE_URL}/generate-audio", json={"text": text})
        result = response.json()
        
        if result.get("audio_url"):
            # Wyciągnij nazwę pliku z URL
            filename = result["audio_url"].split("/")[-1]
            # Pobierz plik audio jako bytes
            audio_response = requests.get(f"{API_BASE_URL}/audio/{filename}")
            if audio_response.status_code == 200:
                return {"audio_bytes": audio_response.content, "audio_url": result["audio_url"]}
        
        return result
    except Exception as e:
        return {"audio_url": None, "error": str(e)}

def chat_with_json(json_data):
    """Chat z LLM na podstawie danych JSON"""
    try:
        response = requests.post(f"{API_BASE_URL}/chat-with-json", json=json_data)
        return response.json()
    except Exception as e:
        return {"answer": f"Błąd: {str(e)}"}

# Inicjalizacja sesji
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "example_json" not in st.session_state:
    st.session_state.example_json = ""

# Nagłówek
st.title("🤖 SimplyBot - Bot Dialogowy z RAG")
st.markdown("Bot wykorzystujący LangChain, Qdrant i ElevenLabs do inteligentnych odpowiedzi")

# Sidebar
with st.sidebar:
    st.header("🔧 Panel Sterowania")
    
    # Status API
    st.subheader("Status API")
    health = check_api_health()
    if health:
        st.success("✅ API dostępne")
        if "services" in health:
            for service, status in health["services"].items():
                if service == "qdrant_collection":
                    if status == "ok":
                        st.success("✅ QDRANT KOLEKCJA")
                    elif status == "not_found":
                        st.warning("⚠️ QDRANT KOLEKCJA - brak (utworzy się automatycznie)")
                    else:
                        st.error("❌ QDRANT KOLEKCJA")
                else:
                    if status == "ok":
                        st.success(f"✅ {service.upper()}")
                    elif status == "no_api_key":
                        st.warning(f"⚠️ {service.upper()} - brak klucza API")
                    else:
                        st.error(f"❌ {service.upper()}")
    else:
        st.error("❌ API niedostępne")
    
    # Informacje o dokumentach
    st.subheader("📚 Dokumenty")
    docs_info = get_documents_info()
    if docs_info and "vectors_count" in docs_info:
        st.info(f"Liczba fragmentów: {docs_info['vectors_count']}")
    else:
        st.warning("Brak informacji o dokumentach")
    
    # Wrzucanie dokumentów
    st.subheader("📁 Wrzuć Dokumenty")
    uploaded_files = st.file_uploader(
        "Wybierz pliki (PDF, TXT, DOCX)",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("Wrzuć dokumenty"):
        with st.spinner("Przetwarzanie dokumentów..."):
            result = upload_documents(uploaded_files)
            if result.get("success"):
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])
    
    # Czyszczenie audio
    if st.button("🧹 Wyczyść stare pliki audio"):
        try:
            response = requests.post(f"{API_BASE_URL}/cleanup-audio")
            if response.status_code == 200:
                st.success("Wyczyszczono stare pliki audio")
            else:
                st.error("Błąd podczas czyszczenia")
        except:
            st.error("Nie udało się połączyć z API")

# Tabs dla różnych funkcji
tab1, tab2 = st.tabs(["💬 Chat z Botem", "📊 Analiza JSON"])

with tab1:
    st.header("💬 Rozmowa z Botem")
    
    # Wyświetl historię wiadomości
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Sprawdź czy odpowiedź ma format TLDR + Opis
            content = message["content"]
            if message["role"] == "assistant" and "**TLDR:**" in content and "**Opis:**" in content:
                # Podziel odpowiedź na TLDR i Opis
                parts = content.split("**Opis:**")
                if len(parts) == 2:
                    tldr_part = parts[0].replace("**TLDR:**", "").strip()
                    opis_part = parts[1].strip()
                    
                    # Wyświetl TLDR w kolorze
                    st.markdown(f"**📋 TLDR:** {tldr_part}")
                    st.markdown("---")
                    st.markdown(f"**📖 Opis:** {opis_part}")
                else:
                    st.write(content)
            else:
                st.write(content)
            
            # Wyświetl audio jeśli dostępne
            if message.get("audio_url"):
                try:
                    # Wyciągnij nazwę pliku z URL
                    filename = message["audio_url"].split("/")[-1]
                    # Spróbuj pobrać plik audio
                    audio_response = requests.get(f"{API_BASE_URL}/audio/{filename}")
                    if audio_response.status_code == 200:
                        # Automatyczne odtwarzanie audio dla historii
                        audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
                        st.markdown(
                            f"""
                            <audio controls style="width: 100%; margin: 10px 0;">
                                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                Twoja przeglądarka nie obsługuje odtwarzania audio.
                            </audio>
                            """,
                            unsafe_allow_html=True
                        )
                        # Przycisk do ponownego odtwarzania
                        if st.button("🔊 Odtwórz ponownie", key=f"replay_{message.get('id', 'unknown')}"):
                            st.markdown(
                                f"""
                                <audio controls autoplay style="width: 100%; margin: 10px 0;">
                                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                    Twoja przeglądarka nie obsługuje odtwarzania audio.
                                </audio>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.warning("⚠️ Plik audio niedostępny")
                except:
                    st.warning("⚠️ Plik audio niedostępny")

with tab2:
    st.header("📊 Analiza JSON z LLM")
    st.markdown("Wklej dane JSON i otrzymaj analizę od AI")
    
    # Input JSON
    json_input = st.text_area(
        "Wklej dane JSON:",
        height=200,
        placeholder='{"name": "example", "value": 123}',
        value=st.session_state.example_json
    )
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button("🤖 Analizuj JSON", type="primary"):
            if json_input.strip():
                try:
                    # Parsuj JSON
                    json_data = json.loads(json_input)
                    
                    with st.spinner("AI analizuje dane..."):
                        response = chat_with_json(json_data)
                    
                    if "answer" in response:
                        st.success("✅ Analiza gotowa!")
                        st.write("**Odpowiedź AI:**")
                        
                        # Sprawdź czy odpowiedź ma format TLDR + Opis
                        answer_text = response["answer"]
                        if "**TLDR:**" in answer_text and "**Opis:**" in answer_text:
                            # Podziel odpowiedź na TLDR i Opis
                            parts = answer_text.split("**Opis:**")
                            if len(parts) == 2:
                                tldr_part = parts[0].replace("**TLDR:**", "").strip()
                                opis_part = parts[1].strip()
                                
                                # Wyświetl TLDR w kolorze
                                st.markdown(f"**📋 TLDR:** {tldr_part}")
                                                        st.markdown("---")
                        st.markdown(f"**📖 Opis:** {opis_part}")
                        st.info("💡 Audio jest generowane tylko dla części TLDR")
                    else:
                        st.write(answer_text)
                else:
                    st.write(answer_text)
                        
                        # Przycisk do generowania audio
                        if st.button("🔊 Użyj głosu (TLDR)", key="voice_btn"):
                            with st.spinner("Generowanie audio dla TLDR..."):
                                # Wyciągnij TLDR z odpowiedzi
                                answer_text = response["answer"]
                                if "**TLDR:**" in answer_text and "**Opis:**" in answer_text:
                                    tldr_part = answer_text.split("**Opis:**")[0]
                                    tldr_text = tldr_part.replace("**TLDR:**", "").strip()
                                    audio_response = generate_audio_from_text(tldr_text)
                                else:
                                    audio_response = generate_audio_from_text(answer_text)
                                if audio_response.get("audio_bytes"):
                                    st.success("✅ Audio wygenerowane dla TLDR!")
                                    # Automatyczne odtwarzanie audio
                                    st.audio(
                                        audio_response["audio_bytes"], 
                                        format="audio/mp3",
                                        start_time=0
                                    )
                                    # Automatyczne odtwarzanie przez HTML
                                    audio_base64 = base64.b64encode(audio_response['audio_bytes']).decode('utf-8')
                                    st.markdown(
                                        f"""
                                        <audio controls autoplay style="width: 100%; margin: 10px 0;">
                                            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                            Twoja przeglądarka nie obsługuje odtwarzania audio.
                                        </audio>
                                        """,
                                        unsafe_allow_html=True
                                    )
                                elif audio_response.get("audio_url"):
                                    st.success("✅ Audio wygenerowane!")
                                    st.audio(
                                        audio_response["audio_url"], 
                                        format="audio/mp3",
                                        start_time=0
                                    )
                                else:
                                    st.error("❌ Błąd generowania audio")
                    else:
                        st.error("❌ Błąd podczas analizy")
                        
                except json.JSONDecodeError as e:
                    st.error(f"❌ Nieprawidłowy format JSON: {e}")
            else:
                st.warning("⚠️ Wklej dane JSON przed analizą")
    
    with col2:
        if st.button("🗑️ Wyczyść"):
            st.rerun()
    
    # Przykładowy JSON
    with st.expander("📝 Przykładowy JSON"):
        example_json = {
            "user": {
                "name": "Jan Kowalski",
                "age": 30,
                "email": "jan@example.com"
            },
            "orders": [
                {
                    "id": 1,
                    "product": "Laptop",
                    "price": 2500,
                    "status": "delivered"
                },
                {
                    "id": 2,
                    "product": "Mouse",
                    "price": 50,
                    "status": "pending"
                }
            ],
            "total_spent": 2550
        }
        st.json(example_json)
        if st.button("📋 Użyj przykładu"):
            st.session_state.example_json = json.dumps(example_json, indent=2)
            st.rerun()

# Input użytkownika
if prompt := st.chat_input("Napisz wiadomość..."):
    # Dodaj wiadomość użytkownika
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generuj odpowiedź
    with st.chat_message("assistant"):
        with st.spinner("Bot myśli..."):
            response = get_more_information(st.session_state.messages)
            
            if "answer" in response:
                # Sprawdź czy odpowiedź ma format TLDR + Opis
                answer_text = response["answer"]
                if "**TLDR:**" in answer_text and "**Opis:**" in answer_text:
                    # Podziel odpowiedź na TLDR i Opis
                    parts = answer_text.split("**Opis:**")
                    if len(parts) == 2:
                        tldr_part = parts[0].replace("**TLDR:**", "").strip()
                        opis_part = parts[1].strip()
                        
                        # Wyświetl TLDR w kolorze
                        st.markdown(f"**📋 TLDR:** {tldr_part}")
                        st.markdown("---")
                        st.markdown(f"**📖 Opis:** {opis_part}")
                        st.info("💡 Audio jest generowane tylko dla części TLDR")
                    else:
                        st.write(answer_text)
                else:
                    st.write(answer_text)
                
                # Dodaj odpowiedź do historii
                bot_message = {
                    "role": "assistant", 
                    "content": response["answer"],
                    "audio_url": response.get("audio_url")
                }
                st.session_state.messages.append(bot_message)
                
                # Wyświetl audio jeśli dostępne
                if response.get("audio_url"):
                    try:
                        # Wyciągnij nazwę pliku z URL
                        filename = response["audio_url"].split("/")[-1]
                        # Spróbuj pobrać plik audio
                        audio_response = requests.get(f"{API_BASE_URL}/audio/{filename}")
                        if audio_response.status_code == 200:
                            # Automatyczne odtwarzanie audio
                            audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
                            st.markdown(
                                f"""
                                <audio controls autoplay style="width: 100%; margin: 10px 0;">
                                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                    Twoja przeglądarka nie obsługuje odtwarzania audio.
                                </audio>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning("⚠️ Plik audio niedostępny")
                    except:
                        st.warning("⚠️ Plik audio niedostępny")
                
                # Wyświetl źródła jeśli dostępne
                if response.get("sources"):
                    with st.expander("📚 Źródła"):
                        for i, source in enumerate(response["sources"]):
                            st.markdown(f"**Źródło {i+1}:**")
                            st.write(f"Fragment: {source['content']}")
                            if source.get("metadata"):
                                st.write(f"Plik: {source['metadata'].get('source', 'Nieznany')}")
                            st.write(f"Powiązanie: {source.get('score', 0):.2f}")
                            st.divider()
            else:
                st.error("Błąd podczas generowania odpowiedzi")

# Przycisk do czyszczenia historii
if st.button("🗑️ Wyczyść historię"):
    st.session_state.messages = []
    st.rerun()

# Informacje o sesji
st.sidebar.markdown("---")
st.sidebar.markdown(f"**ID Sesji:** {st.session_state.session_id}")
st.sidebar.markdown(f"**Liczba wiadomości:** {len(st.session_state.messages)}")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        SimplyBot v1.0 - Powered by LangChain, Qdrant & ElevenLabs
    </div>
    """,
    unsafe_allow_html=True
) 