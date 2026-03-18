from app.generator.embeddings import get_embedding
from app.retriever.vector_store import vector_db
from app.rag.memory import memory_manager
from app.generator.llm import llm_generator
from app.utils.logging import logger
from app.utils.cache import response_cache
from app.core.config import settings
from app.ingestion.manager import ingestion_manager

async def answer_question(question: str, session_id: str = "default"):
    # 0. Check cache
    cache_key = f"{session_id}:{question}"
    cached_ans = response_cache.get(cache_key)
    if cached_ans:
        logger.info(f"Returning cached answer for session {session_id}")
        return cached_ans

    logger.info(f"Answering question for session {session_id}: {question}")
    
    # 1. Get embedding for the question
    query_vector = await get_embedding(question)
    
    # 2. Retrieve relevant context from Endee
    context_results = await vector_db.search(query_vector, top_k=10) # Get more for reranking
    
    # 3. Re-rank results
    from app.retriever.reranker import simple_rerank
    top_docs = simple_rerank(question, context_results, top_n=settings.TOP_K)
    
    context_text = "\n---\n".join([f"[Source: {r.get('source', 'Unknown')}] {r['text']}" for r in top_docs])
    
    # 3. Get session history
    history_text = memory_manager.format_history(session_id)
    
    # 4. Prepare prompt
    system_prompt = """
    You are an Enterprise RAG Assistant. Use the provided context to answer the user's question.
    Strictly follow these rules:
    - If the context doesn't contain the answer, say "I don't have enough information in my documents to answer this."
    - Be concise and professional.
    - MUST include citations in the answer using the [Source: filename] format provided in the context.
    - If information comes from multiple sources, cite all of them.
    """
    
    prompt = f"""
    --- CONVERSATION HISTORY ---
    {history_text}
    
    --- RELEVANT CONTEXT ---
    {context_text}
    
    --- USER QUESTION ---
    {question}
    
    Response:
    """
    
    # 5. Generate response using LLM
    try:
        answer = await llm_generator.generate_response(prompt, system_prompt)
        
        # 6. Update memory and cache
        memory_manager.add_interaction(session_id, question, answer)
        response_cache.set(cache_key, answer)
        
        # 7. Track for Dashboard
        ingestion_manager.add_query(question, answer)
        
        return answer
    except Exception as e:
        logger.error(f"RAG Pipeline error: {e}")
        return "I'm sorry, I'm currently unable to process your request. Please try again later."

async def answer_question_stream(question: str, session_id: str = "default"):
    # 0. Initial Check
    stats = ingestion_manager.get_stats()
    if stats["is_indexing"] and stats["total_documents"] == 0:
        yield "System is still processing your first document. Please wait a few seconds... "
        return

    # 1. Get embedding and context
    query_vector = await get_embedding(question)
    context_results = await vector_db.search(query_vector, top_k=settings.TOP_K)
    
    # 2. Simple rerank and context prep
    from app.retriever.reranker import simple_rerank
    top_docs = simple_rerank(question, context_results, top_n=settings.TOP_K)
    
    context_text = ""
    sources = []
    if not top_docs:
        context_text = "No relevant context found."
    else:
        context_text = "\n---\n".join([f"[Source: {r.get('source', 'Unknown')}] {r['text']}" for r in top_docs])
        sources = list(set([r.get('source', 'Unknown') for r in top_docs]))

    # 3. History
    history_text = memory_manager.format_history(session_id)
    
    # 4. Prompt
    system_prompt = f"You are an Enterprise RAG Assistant. Context FOUND: {len(top_docs) > 0}. If no context, acknowledge you're answering from general knowledge but mention the knowledge base was empty."
    prompt = f"HISTORY:\n{history_text}\n\nCONTEXT:\n{context_text}\n\nQUESTION: {question}\n\nResponse:"

    # 5. Stream
    full_response = ""
    async for chunk in llm_generator.generate_stream(prompt, system_prompt):
        full_response += chunk
        yield chunk

    # 6. Save to memory
    memory_manager.add_interaction(session_id, question, full_response)
    
    # 7. Track for Dashboard
    ingestion_manager.add_query(question, full_response)
