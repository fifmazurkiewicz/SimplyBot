from elevenlabs import generate, save, set_api_key
from simplybot.config import Config
import logging
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class AudioService:
    def __init__(self):
        if Config.ELEVENLABS_API_KEY:
            set_api_key(Config.ELEVENLABS_API_KEY)
        self.voice_id = Config.ELEVENLABS_VOICE_ID
        self.audio_dir = "static/audio"
        self._ensure_audio_dir()
    
    def _ensure_audio_dir(self):
        """Upewnia się, że katalog audio istnieje"""
        os.makedirs(self.audio_dir, exist_ok=True)
    
    async def generate_speech(self, text: str) -> str:
        """Generuje audio z tekstu używając ElevenLabs"""
        try:
            if not Config.ELEVENLABS_API_KEY:
                logger.warning("Brak klucza API ElevenLabs - pomijam generowanie audio")
                return None
            
            # Logowanie rozpoczęcia generowania audio
            text_preview = text[:10] + "..." if len(text) > 10 else text
            logger.info(f"🎵 Rozpoczynam generowanie audio dla tekstu: '{text_preview}' (długość: {len(text)} znaków)")
            
            # Generuj unikalną nazwę pliku
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"speech_{timestamp}.mp3"
            filepath = os.path.join(self.audio_dir, filename)
            
            logger.info(f"📁 Zapisuję audio do: {filepath}")
            
            # Generuj audio
            audio = generate(
                text=text,
                voice=self.voice_id,
                model="eleven_multilingual_v2"
            )
            
            # Zapisz plik
            save(audio, filepath)
            
            # Zwróć URL do pliku
            audio_url = f"/static/audio/{filename}"
            logger.info(f"✅ Audio wygenerowane pomyślnie: {audio_url}")
            
            return audio_url
            
        except Exception as e:
            logger.error(f"Błąd podczas generowania audio: {e}")
            return None
    
    async def cleanup_old_audio_files(self, max_age_hours: int = 24):
        """Usuwa stare pliki audio"""
        try:
            import time
            current_time = time.time()
            max_age_seconds = max_age_hours * 3600
            
            for filename in os.listdir(self.audio_dir):
                if filename.endswith('.mp3'):
                    filepath = os.path.join(self.audio_dir, filename)
                    file_age = current_time - os.path.getmtime(filepath)
                    
                    if file_age > max_age_seconds:
                        os.remove(filepath)
                        logger.info(f"Usunięto stary plik audio: {filename}")
                        
        except Exception as e:
            logger.error(f"Błąd podczas czyszczenia plików audio: {e}") 