import pytest
from app.ingestion.chunker import AdvancedChunker

def test_chunking_logic():
    chunker = AdvancedChunker(chunk_size=10, chunk_overlap=2)
    text = "This is a simple text with several words to test the chunking algorithm."
    chunks = chunker.split_text(text)
    
    assert len(chunks) > 1
    assert all(len(c.split()) <= 10 for c in chunks)
    # Check overlap (very basic check)
    assert chunks[1].startswith(chunks[0].split()[-2])

def test_chunking_paragraph_preservation():
    chunker = AdvancedChunker(chunk_size=50)
    text = "Paragraph one.\n\nParagraph two with more content."
    chunks = chunker.split_text(text)
    assert len(chunks) == 2
    assert "Paragraph one" in chunks[0]
    assert "Paragraph two" in chunks[1]
