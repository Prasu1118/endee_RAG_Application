import asyncio
from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from app.rag.pipeline import answer_question
from app.ingestion.pipeline import process_file
from app.utils.logging import logger
from app.middleware.auth import get_api_key
from fastapi import Request
from fastapi.responses import JSONResponse

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="Endee RAG API")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/")
async def home(request: Request):
    from app.core.config import settings
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "api_key": settings.APP_API_KEY
    })

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Global error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"message": "An internal server error occurred. Please contact support."}
    )

class ChatRequest(BaseModel):
    q: str

class ChatResponse(BaseModel):
    ans: str

@app.get("/health")
async def health_check():
    # Check Endee connectivity if possible
    from app.retriever.vector_store import vector_db
    try:
        # Simple search for a non-existent vector to check connectivity
        await vector_db.search([0.0]*384, top_k=1)
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
        
    return {
        "status": "healthy",
        "database": db_status,
        "version": "1.0.0"
    }

@app.post("/upload")
async def upload_file(
    background_tasks: BackgroundTasks, 
    file: UploadFile = File(...),
    api_key: str = Depends(get_api_key)
):
    try:
        # READ BYTES HERE - prevent closure bug
        file_bytes = await file.read()
        filename = file.filename
        
        logger.info(f"Scheduling background indexing for: {filename}")
        background_tasks.add_task(process_file, file_bytes, filename)
        
        return {"msg": f"File {filename} received. Indexing started in background."}
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/dashboard/stats")
async def get_stats(api_key: str = Depends(get_api_key)):
    from app.ingestion.manager import ingestion_manager
    return ingestion_manager.get_stats()

@app.get("/dashboard/activity")
async def get_activity(api_key: str = Depends(get_api_key)):
    from app.ingestion.manager import ingestion_manager
    return {
        "activities": ingestion_manager.get_activities(),
        "history": ingestion_manager.get_history()
    }

@app.post("/ask", response_model=ChatResponse)
async def ask(request: ChatRequest, api_key: str = Depends(get_api_key)):
    try:
        ans = await answer_question(request.q)
        return ChatResponse(ans=ans)
    except Exception as e:
        logger.error(f"Question processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/ask/stream")
async def ask_stream(request: ChatRequest, api_key: str = Depends(get_api_key)):
    from app.rag.pipeline import answer_question_stream
    
    async def stream_generator():
        try:
            async for chunk in answer_question_stream(request.q):
                yield chunk
        except Exception as e:
            logger.error(f"Stream generation failed: {e}")
            yield " [Error: Connection to LLM failed] "
            
    return StreamingResponse(stream_generator(), media_type="text/plain")


