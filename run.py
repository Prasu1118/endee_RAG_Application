import os

# Mitigate OpenBLAS profiling/memory/threading issues on Windows
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

import uvicorn
from dotenv import load_dotenv
from app.utils.logging import logger

load_dotenv()

# Pre-flight environment check
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    logger.error("OPENAI_API_KEY is not set in environment!")
    # In production, we might want to exit here, but for now we logger.error

def run():
    logger.info("Starting Enterprise RAG Platform on http://localhost:5000")
    uvicorn.run(
        "app.api.main:app",
        host="0.0.0.0",
        port=5000,
        reload=True if os.getenv("DEBUG") == "True" else False
    )

if __name__ == "__main__":
    run()