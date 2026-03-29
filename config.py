from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import os

from dotenv import load_dotenv

load_dotenv()


def _env(name: str, default: str) -> str:
    return os.getenv(name, default).strip()


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    root_dir: Path
    data_dir: Path
    policies_dir: Path
    billing_dir: Path
    index_dir: Path
    api_host: str
    api_port: int
    api_base_url: str
    llm_provider: str
    ollama_base_url: str
    ollama_chat_model: str
    ollama_embedding_model: str
    openai_api_key: str
    openai_base_url: str
    openai_chat_model: str
    openai_embedding_model: str
    http_timeout_sec: int
    allow_cors: bool


def get_settings() -> Settings:
    root = Path(__file__).resolve().parent
    data_dir = Path(_env("DATA_DIR", str(root / "data")))
    policies_dir = Path(_env("POLICIES_DIR", str(data_dir / "policies")))
    billing_dir = Path(_env("BILLING_DIR", str(data_dir / "billing")))
    index_dir = Path(_env("INDEX_DIR", str(root / "faiss_index")))
    return Settings(
        root_dir=root,
        data_dir=data_dir,
        policies_dir=policies_dir,
        billing_dir=billing_dir,
        index_dir=index_dir,
        api_host=_env("API_HOST", "127.0.0.1"),
        api_port=int(_env("API_PORT", "8001")),
        api_base_url=_env("API_BASE_URL", "http://127.0.0.1:8001"),
        llm_provider=_env("LLM_PROVIDER", "ollama"),
        ollama_base_url=_env("OLLAMA_BASE_URL", "http://127.0.0.1:11434"),
        ollama_chat_model=_env("OLLAMA_CHAT_MODEL", "llama3.1:8b"),
        ollama_embedding_model=_env("OLLAMA_EMBEDDING_MODEL", "nomic-embed-text"),
        openai_api_key=_env("OPENAI_API_KEY", ""),
        openai_base_url=_env("OPENAI_BASE_URL", "https://api.openai.com/v1"),
        openai_chat_model=_env("OPENAI_CHAT_MODEL", "gpt-4o-mini"),
        openai_embedding_model=_env("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
        http_timeout_sec=int(_env("HTTP_TIMEOUT_SEC", "30")),
        allow_cors=_env_bool("ALLOW_CORS", True),
    )
