import json
import time
from typing import Any, Optional
from app.utils.logging import logger

class SimpleCache:
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl

    def get(self, key: str) -> Optional[Any]:
        if key in self.cache:
            entry = self.cache[key]
            if time.time() - entry['timestamp'] < self.ttl:
                logger.debug(f"Cache hit for key: {key[:50]}...")
                return entry['data']
            else:
                del self.cache[key]
        return None

    def set(self, key: str, data: Any):
        self.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }

embedding_cache = SimpleCache()
response_cache = SimpleCache()
