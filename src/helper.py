"""Configuración central de la aplicación."""

from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()

# GROQ_API_KEY es el nombre oficial. Se conserva GROP_API_KEY como alias para
# evitar que un error tipográfico en una configuración existente rompa la app.
GROQ_API_KEY = os.getenv("GROQ_API_KEY") or os.getenv("GROP_API_KEY")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDINGS_MODEL = os.getenv(
    "EMBEDDINGS_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))
RETRIEVER_K = int(os.getenv("RETRIEVER_K", "6"))
RELEVANCE_THRESHOLD = float(os.getenv("RELEVANCE_THRESHOLD", "0.22"))


def require_groq_api_key() -> str:
    """Devuelve la clave configurada o explica cómo configurarla."""

    if not GROQ_API_KEY:
        raise RuntimeError(
            "No se encontró GROQ_API_KEY. Copia .env.example como .env "
            "y agrega una clave válida de Groq."
        )
    return GROQ_API_KEY
