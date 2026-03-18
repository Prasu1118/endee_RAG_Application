import pytest
from app.core.config import Settings

def test_settings_loading():
    # Mock environment variables
    import os
    os.environ["OPENAI_API_KEY"] = "test-key"
    os.environ["APP_API_KEY"] = "api-key"
    
    s = Settings()
    assert s.OPENAI_API_KEY == "test-key"
    assert s.APP_API_KEY == "api-key"
    assert s.DEBUG is False
