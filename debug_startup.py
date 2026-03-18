import sys
import traceback
import os

print("--- DIAGNOSTIC START ---")

def trace_import(module_name):
    print(f"DEBUG: Importing {module_name}...")
    try:
        __import__(module_name)
        print(f"DEBUG: Successfully imported {module_name}")
    except Exception:
        print(f"--- ERROR in {module_name} ---")
        traceback.print_exc()
        sys.exit(1)

# Set threading environment variables manually just in case
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"

trace_import("app.utils.logging")
trace_import("app.core.config")
trace_import("app.utils.cache")
trace_import("app.generator.embeddings")
trace_import("app.retriever.vector_store")
trace_import("app.rag.memory")
trace_import("app.generator.llm")
trace_import("app.rag.pipeline")
trace_import("app.ingestion.service")
trace_import("app.ingestion.pipeline")
trace_import("app.api.main")

print("--- ALL IMPORTS SUCCESSFUL ---")
