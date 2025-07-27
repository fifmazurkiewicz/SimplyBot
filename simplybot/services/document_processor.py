import os
import logging
from typing import List, Dict, Any
from datetime import datetime
import PyPDF2
from docx import Document
import re

logger = logging.getLogger(__name__)

class DocumentProcessor:
    def __init__(self):
        self.supported_extensions = ['.pdf', '.txt', '.docx']
    
    async def process_file(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Przetwarza plik i zwraca listę dokumentów"""
        try:
            file_extension = os.path.splitext(filename)[1].lower()
            
            if file_extension not in self.supported_extensions:
                raise ValueError(f"Nieobsługiwany format pliku: {file_extension}")
            
            if file_extension == '.pdf':
                return await self._process_pdf(file_path, filename)
            elif file_extension == '.txt':
                return await self._process_txt(file_path, filename)
            elif file_extension == '.docx':
                return await self._process_docx(file_path, filename)
                
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania pliku {filename}: {e}")
            return []
    
    async def _process_pdf(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Przetwarza plik PDF"""
        documents = []
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    text = page.extract_text()
                    if text.strip():
                        # Podziel tekst na mniejsze fragmenty
                        chunks = self._split_text(text, max_length=1000)
                        
                        for chunk_num, chunk in enumerate(chunks):
                            doc = {
                                "content": chunk,
                                "source": filename,
                                "title": f"{filename} - Strona {page_num + 1}",
                                "content_type": "pdf",
                                "page": page_num + 1,
                                "chunk": chunk_num + 1,
                                "added_at": datetime.now().isoformat()
                            }
                            documents.append(doc)
                            
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania PDF {filename}: {e}")
        
        return documents
    
    async def _process_txt(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Przetwarza plik TXT"""
        documents = []
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                text = file.read()
                
                if text.strip():
                    # Podziel tekst na mniejsze fragmenty
                    chunks = self._split_text(text, max_length=1000)
                    
                    for chunk_num, chunk in enumerate(chunks):
                        doc = {
                            "content": chunk,
                            "source": filename,
                            "title": filename,
                            "content_type": "txt",
                            "chunk": chunk_num + 1,
                            "added_at": datetime.now().isoformat()
                        }
                        documents.append(doc)
                        
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania TXT {filename}: {e}")
        
        return documents
    
    async def _process_docx(self, file_path: str, filename: str) -> List[Dict[str, Any]]:
        """Przetwarza plik DOCX"""
        documents = []
        try:
            doc = Document(file_path)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            if text.strip():
                # Podziel tekst na mniejsze fragmenty
                chunks = self._split_text(text, max_length=1000)
                
                for chunk_num, chunk in enumerate(chunks):
                    doc_item = {
                        "content": chunk,
                        "source": filename,
                        "title": filename,
                        "content_type": "docx",
                        "chunk": chunk_num + 1,
                        "added_at": datetime.now().isoformat()
                    }
                    documents.append(doc_item)
                    
        except Exception as e:
            logger.error(f"Błąd podczas przetwarzania DOCX {filename}: {e}")
        
        return documents
    
    def _split_text(self, text: str, max_length: int = 1000) -> List[str]:
        """Dzieli tekst na mniejsze fragmenty"""
        # Usuń nadmiarowe białe znaki
        text = re.sub(r'\s+', ' ', text).strip()
        
        if len(text) <= max_length:
            return [text]
        
        chunks = []
        current_chunk = ""
        
        # Podziel na zdania
        sentences = re.split(r'[.!?]+', text)
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            if len(current_chunk) + len(sentence) + 1 <= max_length:
                current_chunk += sentence + ". "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = sentence + ". "
        
        if current_chunk:
            chunks.append(current_chunk.strip())
        
        return chunks 