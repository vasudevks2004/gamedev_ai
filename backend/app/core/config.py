import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent
DATA_DIR = BASE_DIR / "data"
PROFILES_DIR = DATA_DIR / "profiles"

PROFILES_DIR.mkdir(parents=True, exist_ok=True)

class Settings(BaseModel):
    app_name: str = "Thangan — Personal GameDev AI Companion"
    version: str = "1.1.0"
    host: str = "127.0.0.1"
    port: int = 8000
    
    # Active LLM configuration
    # Options: "ollama", "gemini", "openai", "mock"
    active_provider: str = "ollama"
    
    # Ollama settings (Local RTX 4060 GPU)
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "qwen2.5-coder:7b"
    
    # Cloud API settings (optional fallbacks)
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    openai_base_url: str = "https://api.openai.com/v1"
    
    gemini_api_key: str = ""
    gemini_model: str = "gemini-1.5-pro"
    
    # Paths
    base_dir: Path = BASE_DIR
    data_dir: Path = DATA_DIR
    profiles_dir: Path = PROFILES_DIR

settings = Settings()
