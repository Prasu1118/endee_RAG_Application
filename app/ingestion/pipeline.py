from app.ingestion.service import ingestion_service
from app.generator.embeddings import get_embedding
from app.retriever.vector_store import vector_db
from app.utils.logging import logger
from app.ingestion.manager import ingestion_manager
import asyncio

async def process_file(file_bytes: bytes, filename: str):
    try:
        ingestion_manager.start_indexing(filename)
        logger.info(f"Processing bytes for file: {filename}")
        
        # Ingestion service needs to be updated to handle bytes
        text = await ingestion_service.parse_bytes(file_bytes, filename)
        chunks = ingestion_service.chunk_text(text)
        
        logger.info(f"Created {len(chunks)} chunks from {filename}")
        
        for i, chunk in enumerate(chunks):
            # Log progress for large files
            if i % 10 == 0:
                logger.debug(f"Indexing chunk {i}/{len(chunks)} for {filename}")
                
            vector = await get_embedding(chunk)
            metadata = {
                "text": chunk,
                "source": filename,
                "chunk_id": i
            }
            await vector_db.insert(vector, metadata)
        
        ingestion_manager.end_indexing(filename, len(chunks))
        return {"chunks_processed": len(chunks)}
        
    except Exception as e:
        logger.error(f"Failed to process {filename}: {e}")
        ingestion_manager.indexing_failed(filename, str(e))
        raise e
