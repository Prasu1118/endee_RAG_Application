from typing import List, Dict
import numpy as np
from app.utils.logging import logger

def simple_rerank(query: str, retrieved_docs: List[Dict], top_n: int = 3) -> List[Dict]:
    """
    Primitive semantic re-ranking using simple keyword matching density or 
    basic similarity scoring (cross-encoder simulation).
    """
    if not retrieved_docs:
        return []
    
    query_terms = set(query.lower().split())
    scored_docs = []
    
    for doc in retrieved_docs:
        text = doc.get("text", "").lower()
        # Calculate term overlap density
        overlap = sum(1 for term in query_terms if term in text)
        score = overlap / len(query_terms) if query_terms else 0
        scored_docs.append((score, doc))
    
    # Sort by score descending
    scored_docs.sort(key=lambda x: x[0], reverse=True)
    return [doc for score, doc in scored_docs[:top_n]]
