"""Configuración central de la aplicación."""

from __future__ import annotations

import os

import streamlit as st
from dotenv import load_dotenv

load_dotenv()


def _streamlit_secret(name: str) -> str | None:
    """Lee un secreto TOML sin fallar cuando no existe configuración local."""

    try:
        value = st.secrets.get(name)
    except FileNotFoundError:
        return None
    if value is None:
        return None
    value = str(value).strip()
    return value or None


def get_setting(name: str, default: str | None = None) -> str | None:
    """Prioriza Streamlit Secrets y conserva el entorno como respaldo local."""

    return _streamlit_secret(name) or os.getenv(name) or default


# GROQ_API_KEY es el nombre oficial. Se conserva GROP_API_KEY como alias para
# evitar que un error tipográfico en una configuración existente rompa la app.
GROQ_API_KEY = get_setting("GROQ_API_KEY") or get_setting("GROP_API_KEY")
GROQ_MODEL = get_setting("GROQ_MODEL", "llama-3.3-70b-versatile")
EMBEDDINGS_MODEL = get_setting(
    "EMBEDDINGS_MODEL",
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
)

CHUNK_SIZE = int(get_setting("CHUNK_SIZE", "1200"))
CHUNK_OVERLAP = int(get_setting("CHUNK_OVERLAP", "200"))
RETRIEVER_K = int(get_setting("RETRIEVER_K", "6"))
RELEVANCE_THRESHOLD = float(get_setting("RELEVANCE_THRESHOLD", "0.22"))


def require_groq_api_key() -> str:
    """Devuelve la clave configurada o explica cómo configurarla."""

    api_key = get_setting("GROQ_API_KEY") or get_setting("GROP_API_KEY")
    if not api_key:
        raise RuntimeError(
            "No se encontró GROQ_API_KEY. Configúrala como secreto TOML de "
            "nivel raíz en Streamlit Community Cloud o en un archivo .env "
            "local, y después reinicia la aplicación."
        )
    return api_key
