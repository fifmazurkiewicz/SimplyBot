import streamlit as st
import requests
import json
import os
import base64
from datetime import datetime
from typing import List, Dict, Any
import tempfile

# Page configuration
st.set_page_config(
    page_title="SimplyBot - RAG Chatbot",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Konfiguracja API
API_BASE_URL = "http://localhost:8000"

def check_api_health():
    """Checks API status"""
    try:
        response = requests.get(f"{API_BASE_URL}/")
        return response.json()
    except Exception:
        return None

def upload_documents(files):
    """Uploads documents to API"""
    try:
        files_data = []
        for file in files:
            files_data.append(("files", (file.name, file.getvalue(), file.type)))
        
        response = requests.post(f"{API_BASE_URL}/upload_documents", files=files_data)
        return response.json()
    except Exception as e:
        return {"success": False, "message": str(e)}

def get_more_information(conversation):
    """Sends conversation to API and receives response"""
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
    """Retrieves document information"""
    try:
        response = requests.get(f"{API_BASE_URL}/documents/info")
        if response.status_code == 200:
            return response.json()
        else:
            print(f"Błąd API: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Błąd połączenia: {e}")
        return None

def generate_audio_from_text(text):
    """Generates audio from text"""
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
    """Chat with LLM based on JSON data"""
    try:
        response = requests.post(f"{API_BASE_URL}/chat-with-json", json=json_data)
        return response.json()
    except Exception as e:
        return {"answer": f"Błąd: {str(e)}"}

# Session initialization
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
if "example_json" not in st.session_state:
    st.session_state.example_json = ""

# Header
st.title("🤖 SimplyBot - RAG Chatbot")
st.markdown("Bot using LangChain, Qdrant and ElevenLabs for intelligent responses")

# Sidebar
with st.sidebar:
    st.header("🔧 Control Panel")
    
    # API Status
    st.subheader("API Status")
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
        st.error("❌ API unavailable")
    
    # Document information
    st.subheader("📚 Documents")
    docs_info = get_documents_info()
    if docs_info and "vectors_count" in docs_info:
        vectors_count = docs_info['vectors_count']
        if vectors_count is not None:
            if vectors_count > 0:
                st.success(f"✅ Fragment count: {vectors_count}")
        else:
            st.info(f"📚 Fragment count: {vectors_count} (no documents)")
    else:
        st.warning("⚠️ No document information")
    
    # Document upload
    st.subheader("📁 Upload Documents")
    uploaded_files = st.file_uploader(
        "Select files (PDF, TXT, DOCX)",
        type=["pdf", "txt", "docx"],
        accept_multiple_files=True
    )
    
    if uploaded_files and st.button("Upload documents"):
        with st.spinner("Processing documents..."):
            result = upload_documents(uploaded_files)
            if result.get("success"):
                st.success(result["message"])
                st.rerun()
            else:
                st.error(result["message"])
    


# Tabs for different functions
tab1, tab2 = st.tabs(["💬 Chat with Bot", "📊 JSON Analysis"])

with tab1:
    st.header("💬 Chat with Bot")
    
    # Display message history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            # Check if response has TLDR + Description format
            content = message["content"]
            if message["role"] == "assistant" and "**TLDR:**" in content and "**Description:**" in content:
                # Split response into TLDR and Description
                parts = content.split("**Description:**")
                if len(parts) == 2:
                    tldr_part = parts[0].replace("**TLDR:**", "").strip()
                    description_part = parts[1].strip()
                    
                    # Display TLDR in color
                    st.markdown(f"**📋 TLDR:** {tldr_part}")
                    st.markdown("---")
                    st.markdown(f"**📖 Description:** {description_part}")
                else:
                    st.write(content)
            else:
                st.write(content)
            
            # Display audio if available
            if message.get("audio_url"):
                try:
                    # Extract filename from URL
                    filename = message["audio_url"].split("/")[-1]
                    # Try to download audio file
                    audio_response = requests.get(f"{API_BASE_URL}/audio/{filename}")
                    if audio_response.status_code == 200:
                        # Automatic audio playback for history
                        audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
                        st.markdown(
                            f"""
                            <audio controls style="width: 100%; margin: 10px 0;">
                                <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                Your browser doesn't support audio playback.
                            </audio>
                            """,
                            unsafe_allow_html=True
                        )
                        # Button for replay
                        if st.button("🔊 Play again", key=f"replay_{message.get('id', 'unknown')}"):
                            st.markdown(
                                f"""
                                <audio controls autoplay style="width: 100%; margin: 10px 0;">
                                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                    Your browser doesn't support audio playback.
                                </audio>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.warning("⚠️ Audio file unavailable")
                except:
                    st.warning("⚠️ Audio file unavailable")

with tab2:
    st.header("📊 JSON Analysis with LLM")
    st.markdown("Paste JSON data and get AI analysis")
    
    # Input JSON
    json_input = st.text_area(
        "Paste JSON data:",
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

# User input
if prompt := st.chat_input("Write a message..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    with st.chat_message("user"):
        st.write(prompt)
    
    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Bot is thinking..."):
            response = get_more_information(st.session_state.messages)
            
            if "answer" in response:
                # Check if response requires clarification
                if response.get("needs_clarification", False):
                    st.warning("🤔 Bot needs more information:")
                    st.info(f"**Confidence:** {response.get('confidence', 0):.1%}")
                
                # Check if response has TLDR + Description format
                answer_text = response["answer"]
                if "**TLDR:**" in answer_text and "**Description:**" in answer_text:
                    # Split response into TLDR and Description
                    parts = answer_text.split("**Description:**")
                    if len(parts) == 2:
                        tldr_part = parts[0].replace("**TLDR:**", "").strip()
                        description_part = parts[1].strip()
                        
                        # Display TLDR in color
                        st.markdown(f"**📋 TLDR:** {tldr_part}")
                        st.markdown("---")
                        st.markdown(f"**📖 Description:** {description_part}")
                        st.info("💡 Audio is generated only for TLDR part")
                    else:
                        st.write(answer_text)
                else:
                    st.write(answer_text)
                
                # Add response to history
                bot_message = {
                    "role": "assistant", 
                    "content": response["answer"],
                    "audio_url": response.get("audio_url")
                }
                st.session_state.messages.append(bot_message)
                
                # Display audio if available
                if response.get("audio_url"):
                    try:
                        # Extract filename from URL
                        filename = response["audio_url"].split("/")[-1]
                        # Try to download audio file
                        audio_response = requests.get(f"{API_BASE_URL}/audio/{filename}")
                        if audio_response.status_code == 200:
                            # Automatic audio playback
                            audio_base64 = base64.b64encode(audio_response.content).decode('utf-8')
                            st.markdown(
                                f"""
                                <audio controls autoplay style="width: 100%; margin: 10px 0;">
                                    <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                                    Your browser doesn't support audio playback.
                                </audio>
                                """,
                                unsafe_allow_html=True
                            )
                        else:
                            st.warning("⚠️ Audio file unavailable")
                    except:
                        st.warning("⚠️ Audio file unavailable")
                
                # Display sources if available
                if response.get("sources"):
                    with st.expander("📚 Sources"):
                        for i, source in enumerate(response["sources"]):
                            st.markdown(f"**Source {i+1}:**")
                            st.write(f"Fragment: {source['content']}")
                            if source.get("metadata"):
                                st.write(f"File: {source['metadata'].get('source', 'Unknown')}")
                            st.write(f"Relevance: {source.get('score', 0):.2f}")
                            st.divider()
            else:
                st.error("Error generating response")

# Clear history button
if st.button("🗑️ Clear history"):
    st.session_state.messages = []
    st.rerun()

# Session information
st.sidebar.markdown("---")
st.sidebar.markdown(f"**Session ID:** {st.session_state.session_id}")
st.sidebar.markdown(f"**Message count:** {len(st.session_state.messages)}")

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