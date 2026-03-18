import PyPDF2
from fastapi import UploadFile
from typing import List
from app.core.config import settings
from app.utils.logging import logger

class IngestionService:
    def __init__(self):
        self.chunk_size = settings.CHUNK_SIZE
        self.chunk_overlap = settings.CHUNK_OVERLAP

    async def parse_file(self, file: UploadFile) -> str:
        content = await file.read()
        return await self.parse_bytes(content, file.filename)

    async def parse_bytes(self, content: bytes, filename: str) -> str:
        if filename.lower().endswith(".pdf"):
            import io
            try:
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
                text = ""
                for page in pdf_reader.pages:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted + "\n"
                return text
            except Exception as e:
                logger.error(f"PDF extraction error: {e}")
                raise Exception(f"Failed to extract text from PDF: {e}")
        
        try:
            return content.decode("utf-8")
        except UnicodeDecodeError:
            # Fallback for other encodings
            return content.decode("latin-1")

    def chunk_text(self, text: str) -> List[str]:
        from app.ingestion.chunker import advanced_chunker
        return advanced_chunker.split_text(text)

ingestion_service = IngestionService()
