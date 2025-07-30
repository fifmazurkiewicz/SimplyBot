from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from simplybot.config import Config
from simplybot.models import ConversationSummary, NextAction
from typing import List, Dict, Any
import logging
import json

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Check if we're using OpenRouter or OpenAI
        if Config.OPENROUTER_API_KEY:
            # Use OpenRouter (main LLM configuration)
            self.llm = ChatOpenAI(
                api_key=Config.OPENROUTER_API_KEY,
                base_url=Config.OPENROUTER_BASE_URL,
                model=Config.OPENROUTER_MODEL,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
        elif Config.OPENAI_API_KEY:
            # Fallback to OpenAI (if no OpenRouter)
            self.llm = ChatOpenAI(
                api_key=Config.OPENAI_API_KEY,
                model=Config.OPENAI_MODEL,
                temperature=Config.TEMPERATURE,
                max_tokens=Config.MAX_TOKENS
            )
        else:
            raise ValueError("No API key - set OPENROUTER_API_KEY or OPENAI_API_KEY")
    
    async def summarize_conversation(self, conversation: List[Dict[str, str]]) -> ConversationSummary:
        """Podsumowuje rozmowę i przygotowuje zapytanie do RAG z zabezpieczeniem"""
        try:
            # Logowanie rozpoczęcia podsumowywania
            logger.info(f"🧠 Rozpoczynam podsumowywanie rozmowy ({len(conversation)} wiadomości)")
            
            # Sprawdź czy rozmowa ma wystarczającą treść do analizy
            if len(conversation) < 1:
                logger.warning("⚠️ Brak wiadomości w rozmowie")
                return ConversationSummary(
                    conversation_summary="Brak wiadomości do analizy",
                    rag_query="Proszę o pytanie lub opis sytuacji",
                    next_action=NextAction.ASK_USER,
                    confidence=0.0,
                    reasoning="Brak wiadomości w rozmowie"
                )
            
            # Konwertuj rozmowę na tekst
            conversation_text = "\n".join([
                f"{msg['role']}: {msg['content']}" 
                for msg in conversation
            ])
            
            # Logowanie ostatniej wiadomości użytkownika
            last_user_message = next((msg['content'] for msg in reversed(conversation) if msg['role'] == 'user'), '')
            last_message_preview = last_user_message[:10] + "..." if len(last_user_message) > 10 else last_user_message
            logger.info(f"💬 Ostatnia wiadomość użytkownika: '{last_message_preview}'")
            
            # Check if last user message is not too short
            if len(last_user_message.strip()) < 3:
                logger.warning("⚠️ Last user message too short")
                return ConversationSummary(
                    conversation_summary="User sent very short message",
                    rag_query="Please provide more detailed question or problem description",
                    next_action=NextAction.ASK_USER,
                    confidence=0.1,
                    reasoning="Last user message has less than 3 characters - more details needed"
                )
            
            system_prompt = """
            You are an expert in analyzing conversations and user intentions. Your task is to:
            1. Analyze the content of user's message
            2. Identify whether the user:
               - Asked a specific question
               - Made a statement or fact
               - Described a situation or problem
               - Sent unclear or too short message
            3. Decide whether to prepare a query to knowledge base or ask user for more information
            4. Estimate analysis confidence (0.0-1.0)
            
            Respond in JSON format:
            {
                "conversation_summary": "brief conversation summary",
                "rag_query": "specific query to knowledge base or question to user",
                "next_action": "rag_query" or "ask_user",
                "confidence": 0.0-1.0,
                "reasoning": "reasoning for chosen action"
            }
            
            Analysis rules:
            - If user asked specific question (e.g. "How does X work?", "Where can I find Y?") -> next_action: "rag_query"
            - If user made statement or fact (e.g. "I have a problem with X", "I need Y") -> next_action: "rag_query"
            - If user described situation (e.g. "Yesterday I had a problem with...", "I'm looking for a solution for...") -> next_action: "rag_query"
            - If message is too short (e.g. "ok", "hi", "test") -> next_action: "ask_user"
            - If message is unclear or doesn't contain specific information -> next_action: "ask_user"
            - If lacks context to understand intention -> next_action: "ask_user"
            
            Examples:
            - "How does SimplyProject work?" -> rag_query (specific question)
            - "I have a login problem" -> rag_query (problem description)
            - "I need help with configuration" -> rag_query (statement)
            - "ok" -> ask_user (too short)
            - "hi" -> ask_user (no specific information)
            - "test" -> ask_user (unclear)
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Rozmowa:\n{conversation_text}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Logowanie odpowiedzi
            response_preview = response.content[:50] + "..." if len(response.content) > 50 else response.content
            logger.info(f"📝 Odpowiedź LLM: '{response_preview}'")
            
            # Parsuj JSON odpowiedź
            try:
                # Wyciągnij JSON z odpowiedzi (może być otoczony markdown)
                content = response.content.strip()
                if content.startswith("```json"):
                    content = content[7:]
                if content.endswith("```"):
                    content = content[:-3]
                
                summary_data = json.loads(content.strip())
                
                # Waliduj i utwórz obiekt ConversationSummary
                summary = ConversationSummary(
                    conversation_summary=summary_data.get("conversation_summary", ""),
                    rag_query=summary_data.get("rag_query", ""),
                    next_action=NextAction(summary_data.get("next_action", "ask_user")),
                    confidence=float(summary_data.get("confidence", 0.5)),
                    reasoning=summary_data.get("reasoning", "")
                )
                
                logger.info(f"✅ Podsumowanie utworzone: {summary.next_action} (pewność: {summary.confidence})")
                return summary
                
            except (json.JSONDecodeError, ValueError) as e:
                logger.error(f"❌ Błąd parsowania JSON: {e}")
                # Fallback - spróbuj wyciągnąć informacje z tekstu
                return ConversationSummary(
                    conversation_summary="Błąd parsowania odpowiedzi LLM",
                    rag_query="Proszę o ponowne sformułowanie pytania",
                    next_action=NextAction.ASK_USER,
                    confidence=0.1,
                    reasoning=f"Błąd parsowania JSON: {str(e)}"
                )
            
        except Exception as e:
            logger.error(f"❌ Błąd podczas podsumowywania rozmowy: {e}")
            return ConversationSummary(
                conversation_summary="Błąd podczas analizy rozmowy",
                rag_query="Proszę o ponowne sformułowanie pytania",
                next_action=NextAction.ASK_USER,
                confidence=0.0,
                reasoning=f"Błąd systemu: {str(e)}"
            )
    
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
            You are a helpful assistant. Answer user questions based on 
            provided documents. If you cannot find the answer in documents, 
            respond exactly: "I don't have information". If you don't understand the question or no question arises from the conversation, you can ask the user for more information. 
            
            Responses MUST be in format:
            
            **TLDR:** [One line with quick, concise answer]
            
            **Description:** [Detailed description with additional information, context and explanations]
            
            Responses should be:
            - Accurate and based on facts from documents
            - TLDR should be very concise (1-2 sentences)
            - Description can be longer and contain details
            - In English
            """
            
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"Kontekst:\n{context_text}\n\nPytanie: {question}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Log generated response
            answer_preview = response.content[:10] + "..." if len(response.content) > 10 else response.content
            logger.info(f"✅ Response generated: '{answer_preview}'")
            
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I don't have information" 