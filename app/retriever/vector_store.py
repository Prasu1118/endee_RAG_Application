import os
import json
import numpy as np
import requests
from app.core.config import settings
from app.utils.logging import logger

# Assuming the endee module is in the project root or PYTHONPATH
try:
    from endee.src.client import Client
except ImportError:
    logger.warning("Endee client not found in path, ensure 'endee' submodule is correctly positioned.")
    # We will still define the wrapper to handle the local fallback
    class Client:
        def insert(self, **kwargs): raise Exception("Endee Client Not Initialized")
        def search(self, **kwargs): raise Exception("Endee Client Not Initialized")

class EndeeWrapper:
    def __init__(self):
        self.client = Client()
        self.collection = settings.COLLECTION_NAME
        # Ensure absolute path for local fallback
        project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.local_path = os.path.join(project_root, "local_vector_store.json")
        logger.info(f"VectorStore Initialized. Local fallback path: {self.local_path}")

    def _get_local_storage(self):
        if os.path.exists(self.local_path):
            try:
                with open(self.local_path, "r") as f:
                    data = json.load(f)
                    logger.debug(f"Loaded {len(data)} items from local fallback.")
                    return data
            except Exception as e:
                logger.error(f"Failed to read local storage: {e}")
                return []
        return []

    def _save_local_storage(self, data):
        try:
            with open(self.local_path, "w") as f:
                json.dump(data, f)
                logger.debug(f"Saved {len(data)} items to local fallback.")
        except Exception as e:
            logger.error(f"Failed to save local storage: {e}")

    async def insert(self, vector, metadata):
        logger.info(f"Inserting vector into Endee (Source: {metadata.get('source')})")
        try:
            # In a real async environment, we'd use an async client or run_in_executor
            self.client.insert(
                collection=self.collection,
                vector=vector,
                metadata=metadata
            )
            logger.info(f"Successfully inserted vector into Endee collection: {self.collection}")
        except Exception as e:
            logger.warning(f"Vector DB Server unavailable, using local fallback. Error: {e}")
            data = self._get_local_storage()
            data.append({"vector": vector, "metadata": metadata})
            self._save_local_storage(data)

    async def search(self, query_vector, top_k=None):
        top_k = top_k or settings.TOP_K
        try:
            results = self.client.search(
                collection=self.collection,
                query_vector=query_vector,
                top_k=top_k
            )
            return [r["metadata"] for r in results]
        except Exception as e:
            logger.warning(f"Vector DB Server unavailable, searching local fallback. Error: {e}")
            data = self._get_local_storage()
            if not data:
                return []
            
            vectors = np.array([item["vector"] for item in data])
            q_vec = np.array(query_vector)
            
            norms = np.linalg.norm(vectors, axis=1)
            q_norm = np.linalg.norm(q_vec)
            
            if q_norm == 0 or np.any(norms == 0):
                similarities = np.dot(vectors, q_vec)
            else:
                similarities = np.dot(vectors, q_vec) / (norms * q_norm)
            
            found_k = min(top_k, len(data))
            indices = np.argsort(similarities)[-found_k:][::-1]
            
            return [data[i]["metadata"] for i in indices]

vector_db = EndeeWrapper()
