from app.utils.logging import logger
from app.utils.cache import embedding_cache

_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Initializing SentenceTransformer model (all-MiniLM-L6-v2) - This may take a moment...")
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer('all-MiniLM-L6-v2')
    return _model

async def get_embedding(text: str):
    # Check cache first
    cached = embedding_cache.get(text)
    if cached:
        return cached
        
    try:
        model = get_model()
        embedding = model.encode(text).tolist()
        embedding_cache.set(text, embedding)
        return embedding
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise e
