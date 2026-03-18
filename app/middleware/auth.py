from fastapi import Request, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
from app.core.config import settings
from app.utils.logging import logger

API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

async def get_api_key(api_key: str = Security(api_key_header)):
    # In a real enterprise app, this would check against a DB or HashiCorp Vault
    # For now, we use a simple env-based check or allow if not set for dev
    expected_key = settings.APP_API_KEY
    
    if not expected_key or expected_key == "your-secure-api-key-here":
        # Disable auth if key is default/unset for better local UX
        logger.warning("APP_API_KEY not set. Authentication is disabled.")
        return None
        
    if api_key == expected_key:
        return api_key
    else:
        raise HTTPException(
            status_code=403, detail="Could not validate API Key"
        )

import os
