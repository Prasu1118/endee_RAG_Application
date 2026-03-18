import sys
import os
import json
import numpy as np
import requests

sys.path.append("./endee")

from endee.src.client import Client

client = Client()

COLLECTION = "rag_docs"
LOCAL_STORAGE_PATH = "local_vector_store.json"

def get_local_storage():
    if os.path.exists(LOCAL_STORAGE_PATH):
        try:
            with open(LOCAL_STORAGE_PATH, "r") as f:
                return json.load(f)
        except:
            return []
    return []

def save_local_storage(data):
    with open(LOCAL_STORAGE_PATH, "w") as f:
        json.dump(data, f)

def insert(vector, metadata):
    try:
        # Attempt server-side insert
        client.insert(
            collection=COLLECTION,
            vector=vector,
            metadata=metadata
        )
    except Exception as e:
        print(f"DEBUG: Vector DB Server unavailable, using local fallback. Error: {e}")
        data = get_local_storage()
        data.append({"vector": vector, "metadata": metadata})
        save_local_storage(data)

def search(query_vector):
    try:
        # Attempt server-side search
        results = client.search(
            collection=COLLECTION,
            query_vector=query_vector,
            top_k=4
        )
        return [r["metadata"]["text"] for r in results]
    except Exception as e:
        print(f"DEBUG: Vector DB Server unavailable, searching local fallback. Error: {e}")
        data = get_local_storage()
        if not data:
            return []
        
        # Simple Cosine Similarity fallback using Numpy
        vectors = np.array([item["vector"] for item in data])
        q_vec = np.array(query_vector)
        
        # Normalize vectors for cosine similarity
        norms = np.linalg.norm(vectors, axis=1)
        q_norm = np.linalg.norm(q_vec)
        
        if q_norm == 0 or np.any(norms == 0):
            # Fallback to simple dot product if norms are zero
            similarities = np.dot(vectors, q_vec)
        else:
            similarities = np.dot(vectors, q_vec) / (norms * q_norm)
        
        # Get top K indices
        top_k = min(4, len(data))
        indices = np.argsort(similarities)[-top_k:][::-1]
        
        return [data[i]["metadata"]["text"] for i in indices]