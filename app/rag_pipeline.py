from utils.embeddings import get_embedding
from utils.endee_client import search
from app.memory import get_memory, add_memory
from openai import OpenAI
import time

client = OpenAI()

def answer_question(question):
    try:
        query_vector = get_embedding(question)
        contexts = search(query_vector)
        context_text = "\n".join(contexts)

        history = get_memory()
        history_text = ""
        for h in history:
            history_text += f"Q:{h['q']} A:{h['a']}\n"

        prompt = f"""
You are AI assistant.

Conversation History:
{history_text}

Context:
{context_text}

Question:
{question}
"""
        # Resilience: Retry logic for capacity or temporary issues
        max_retries = 2
        for attempt in range(max_retries + 1):
            try:
                res = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role":"user","content":prompt}]
                )
                ans = res.choices[0].message.content
                add_memory(question, ans)
                return ans
            except Exception as e:
                if attempt < max_retries and ("capacity" in str(e).lower() or "limit" in str(e).lower()):
                    print(f"DEBUG: LLM Capacity reached, retrying in 2s... (Attempt {attempt+1})")
                    time.sleep(2)
                    continue
                raise e

    except Exception as e:
        print(f"ERROR in RAG Pipeline: {e}")
        return "I'm currently experiencing high demand. Please try again in a moment, or ask a simpler question."