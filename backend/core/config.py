import os
from pathlib import Path
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    api_base_url: str = "http://localhost:8000"
    qdrant_host: str = "localhost"
    qdrant_port: int = 6333
    qdrant_collection_name: str = "edhac_chunks"
    embedding_model_name: str = "BAAI/bge-small-en-v1.5"
    groq_api_key: str = ""
    openai_api_key: str = ""
    top_k_default: int = 5
    data_dir: str = str(Path(__file__).resolve().parent.parent.parent / "data")

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
