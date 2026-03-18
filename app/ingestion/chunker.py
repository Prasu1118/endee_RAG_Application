from typing import List
import re
from app.core.config import settings

class AdvancedChunker:
    def __init__(self, chunk_size: int = None, chunk_overlap: int = None):
        self.chunk_size = chunk_size or settings.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or settings.CHUNK_OVERLAP

    def split_text(self, text: str) -> List[str]:
        # Recursive-like splitting by paragraphs first, then sentences, then words
        # This keeps semantic units together better than simple word splitting
        
        # 1. Clean text (remove excessive newlines)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 2. Split by paragraphs
        paragraphs = text.split('\n\n')
        
        chunks = []
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_len = len(para.split())
            
            # If paragraph itself is too large, split it further
            if para_len > self.chunk_size:
                # Process what we have so far
                if current_chunk:
                    chunks.append(" ".join(current_chunk))
                    current_chunk = []
                    current_length = 0
                
                # Split large paragraph by sentences
                sentences = re.split(r'(?<=[.!?]) +', para)
                for sentence in sentences:
                    sent_len = len(sentence.split())
                    if current_length + sent_len > self.chunk_size:
                        if current_chunk:
                            chunks.append(" ".join(current_chunk))
                            # Carry over overlap
                            overlap_str = " ".join(current_chunk[-self.chunk_overlap:]) if len(current_chunk) > self.chunk_overlap else " ".join(current_chunk)
                            current_chunk = [overlap_str, sentence]
                            current_length = len(overlap_str.split()) + sent_len
                        else:
                            # Single sentence is too long, just force split
                            chunks.append(sentence)
                    else:
                        current_chunk.append(sentence)
                        current_length += sent_len
            else:
                if current_length + para_len > self.chunk_size:
                    if current_chunk:
                        chunks.append(" ".join(current_chunk))
                        # Carry over overlap
                        overlap_str = " ".join(current_chunk[-self.chunk_overlap:]) if len(current_chunk) > self.chunk_overlap else " ".join(current_chunk)
                        current_chunk = [overlap_str, para]
                        current_length = len(overlap_str.split()) + para_len
                    else:
                        current_chunk.append(para)
                        current_length += para_len
                else:
                    current_chunk.append(para)
                    current_length += para_len
                    
        if current_chunk:
            chunks.append(" ".join(current_chunk))
            
        return chunks

advanced_chunker = AdvancedChunker()
