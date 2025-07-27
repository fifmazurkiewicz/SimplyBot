from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from simplybot.config import Config
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Sprawdź czy używamy OpenRouter czy OpenAI
        if Config.OPENROUTER_API_KEY:
            # Użyj OpenRouter (główna konfiguracja dla LLM)
            self.llm = ChatOpenAI(
                api_key=Config.OPENROUTER_API_KEY,
                base_url=Config.OPENROUTER_BASE_URL,
                model=Config.OPENROUTER_MODEL,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
        elif Config.OPENAI_API_KEY:
            # Fallback do OpenAI (jeśli brak OpenRouter)
            self.llm = ChatOpenAI(
                api_key=Config.OPENAI_API_KEY,
                model=Config.OPENAI_MODEL,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
        else:
            raise ValueError("Brak klucza API - ustaw OPENROUTER_API_KEY lub OPENAI_API_KEY")
    
    async def summarize_conversation(self, conversation: List[Dict[str, str]]) -> str:
        """Podsumowuje rozmowę i przygotowuje zapytanie do RAG"""
        try:
            # Logowanie rozpoczęcia podsumowywania
            logger.info(f"🧠 Rozpoczynam podsumowywanie rozmowy ({len(conversation)} wiadomości)")
            
            # Konwertuj rozmowę na tekst
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation
            ])
            
            # Logowanie ostatniej wiadomości użytkownika
            last_user_message = next((msg['content'] for msg in reversed(conversation) if msg['role'] == 'user'), '')
            last_message_preview = last_user_message[:10] + "..." if len(last_user_message) > 10 else last_user_message
            logger.info(f"💬 Ostatnia wiadomość użytkownika: '{last_message_preview}'")
            
            system_prompt = """
            Jesteś ekspertem w analizie rozmów. Twoim zadaniem jest:
            1. Podsumować główne punkty rozmowy
            2. Zidentyfikować kluczowe pytania lub problemy użytkownika
            3. Przygotować konkretne zapytanie do bazy wiedzy
            
            Odpowiedz w formacie:
            PODSUMOWANIE: [krótkie podsumowanie]
            PYTANIE: [konkretne zapytanie do bazy wiedzy]
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Rozmowa:\n{conversation_text}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Logowanie podsumowania
            summary_preview = response.content[:10] + "..." if len(response.content) > 10 else response.content
            logger.info(f"📝 Podsumowanie wygenerowane: '{summary_preview}'")
            
            return response.content
            
        except Exception as e:
            logger.error(f"Błąd podczas podsumowywania rozmowy: {e}")
            return "Nie udało się podsumować rozmowy"
    
    async def answer_with_context(self, question: str, context_docs: List[Dict[str, Any]]) -> str:
        """Odpowiada na pytanie używając kontekstu z dokumentów"""
        try:
            # Logowanie rozpoczęcia generowania odpowiedzi
            question_preview = question[:10] + "..." if len(question) > 10 else question
            logger.info(f"🤖 Generowanie odpowiedzi dla pytania: '{question_preview}' (kontekst: {len(context_docs)} dokumentów)")
            
            if not context_docs:
                logger.warning("⚠️ Brak dokumentów kontekstowych - zwracam domyślną odpowiedź")
                return "Nie posiadam informacji"
            
            # Przygotuj kontekst z dokumentów
            context_text = "\n\n".join([
                f"Dokument {i+1}:\n{doc.get('content', '')}"
                for i, doc in enumerate(context_docs)
            ])
            
            # Logowanie informacji o kontekście
            context_preview = context_text[:50] + "..." if len(context_text) > 50 else context_text
            logger.info(f"📚 Kontekst przygotowany: '{context_preview}'")
            
            system_prompt = """
            Jesteś pomocnym asystentem. Odpowiadaj na pytania użytkownika na podstawie 
            dostarczonych dokumentów. Jeśli nie możesz znaleźć odpowiedzi w dokumentach, 
            odpowiedz dokładnie: "Nie posiadam informacji". Jeżeli nie zrozumiałeś pytania lub z rozmowy nie wynika żadne pytanie, możesz dopytać użytkownika o dalsze informacje. 
            
            Odpowiedzi MUSZĄ być w formacie:
            
            **TLDR:** [Jedna linia z szybką, zwięzłą odpowiedzią]
            
            **Opis:** [Szczegółowy opis z dodatkowymi informacjami, kontekstem i wyjaśnieniami]
            
            Odpowiedzi powinny być:
            - Dokładne i oparte na faktach z dokumentów
            - TLDR powinien być bardzo zwięzły (1-2 zdania)
            - Opis może być dłuższy i zawierać szczegóły
            - W języku polskim
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Kontekst:\n{context_text}\n\nPytanie: {question}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Logowanie wygenerowanej odpowiedzi
            answer_preview = response.content[:10] + "..." if len(response.content) > 10 else response.content
            logger.info(f"✅ Odpowiedź wygenerowana: '{answer_preview}'")
            
            return response.content
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania odpowiedzi: {e}")
            return "Nie posiadam informacji" 