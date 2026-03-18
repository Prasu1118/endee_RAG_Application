import time
from typing import List, Dict
from app.utils.logging import logger

class IngestionManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IngestionManager, cls).__new__(cls)
            cls._instance.stats = {
                "total_documents": 0,
                "total_chunks": 0,
                "is_indexing": False,
                "last_indexed": None
            }
            cls._instance.activities = []
            cls._instance.query_history = []
        return cls._instance

    def start_indexing(self, filename: str):
        self.stats["is_indexing"] = True
        self.add_activity(f"Started indexing: {filename}", "info")

    def end_indexing(self, filename: str, chunks_count: int):
        self.stats["is_indexing"] = False
        self.stats["total_documents"] += 1
        self.stats["total_chunks"] += chunks_count
        self.stats["last_indexed"] = time.strftime("%Y-%m-%d %H:%M:%S")
        self.add_activity(f"Successfully indexed {filename} ({chunks_count} chunks)", "success")

    def indexing_failed(self, filename: str, error: str):
        self.stats["is_indexing"] = False
        self.add_activity(f"Failed to index {filename}: {error}", "error")

    def add_activity(self, message: str, type: str = "info"):
        activity = {
            "timestamp": time.strftime("%H:%M:%S"),
            "message": message,
            "type": type
        }
        self.activities.insert(0, activity)
        # Keep only last 20 activities
        self.activities = self.activities[:20]

    def add_query(self, query: str, response: str):
        entry = {
            "timestamp": time.strftime("%H:%M:%S"),
            "query": query,
            "response_preview": response[:100] + "..." if len(response) > 100 else response
        }
        self.query_history.insert(0, entry)
        self.query_history = self.query_history[:15]

    def get_stats(self) -> Dict:
        return self.stats

    def get_activities(self) -> List[Dict]:
        return self.activities

    def get_history(self) -> List[Dict]:
        return self.query_history

ingestion_manager = IngestionManager()
