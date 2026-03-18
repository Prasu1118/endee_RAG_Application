from typing import List, Dict
from app.utils.logging import logger

class MemoryManager:
    def __init__(self, max_history: int = 5):
        self.memory: Dict[str, List[Dict[str, str]]] = {}
        self.max_history = max_history

    def add_interaction(self, session_id: str, question: str, answer: str):
        if session_id not in self.memory:
            self.memory[session_id] = []
        
        self.memory[session_id].append({"q": question, "a": answer})
        
        # Keep only the last N interactions
        if len(self.memory[session_id]) > self.max_history:
            self.memory[session_id] = self.memory[session_id][-self.max_history:]
            
        logger.debug(f"Added to memory for session {session_id}. History size: {len(self.memory[session_id])}")

    def get_history(self, session_id: str) -> List[Dict[str, str]]:
        history = self.memory.get(session_id, [])
        return history

    def format_history(self, session_id: str) -> str:
        history = self.get_history(session_id)
        if not history:
            return ""
        
        formatted = ""
        for h in history:
            formatted += f"User: {h['q']}\nAI: {h['a']}\n"
        return formatted

memory_manager = MemoryManager()
