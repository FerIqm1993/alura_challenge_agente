"""Índice vectorial local con invalidación automática por huella de fuentes."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from helper import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    EMBEDDINGS_MODEL,
    RELEVANCE_THRESHOLD,
    RETRIEVER_K,
)
from ingest import DOCS_DIR, DocsIngestor

FAISS_INDEX_DIR = Path(__file__).resolve().parent.parent / "data" / "faiss_index"
MANIFEST_PATH = FAISS_INDEX_DIR / "index_manifest.json"
INDEX_FORMAT_VERSION = 2


def source_fingerprint(docs_dir: Path = DOCS_DIR) -> str:
    """Identifica de forma reproducible el contenido y configuración del índice."""

    digest = hashlib.sha256()
    digest.update(
        (
            f"format={INDEX_FORMAT_VERSION};model={EMBEDDINGS_MODEL};"
            f"chunk={CHUNK_SIZE};overlap={CHUNK_OVERLAP}"
        ).encode("utf-8")
    )
    for pdf_path in sorted(Path(docs_dir).glob("*.pdf"), key=lambda path: path.name.lower()):
        digest.update(pdf_path.name.encode("utf-8"))
        with pdf_path.open("rb") as pdf_file:
            for block in iter(lambda: pdf_file.read(1024 * 1024), b""):
                digest.update(block)
    return digest.hexdigest()


class VectorStore:
    def __init__(self, docs_dir: Path = DOCS_DIR, index_dir: Path = FAISS_INDEX_DIR):
        self.docs_dir = Path(docs_dir)
        self.index_dir = Path(index_dir)
        self.manifest_path = self.index_dir / MANIFEST_PATH.name
        self.vectorstore: FAISS | None = None
        self.embeddings_model = HuggingFaceEmbeddings(
            model_name=EMBEDDINGS_MODEL,
            encode_kwargs={"normalize_embeddings": True},
        )

    def _expected_manifest(self) -> dict:
        return {
            "format_version": INDEX_FORMAT_VERSION,
            "source_fingerprint": source_fingerprint(self.docs_dir),
            "embedding_model": EMBEDDINGS_MODEL,
            "chunk_size": CHUNK_SIZE,
            "chunk_overlap": CHUNK_OVERLAP,
        }

    def _index_is_current(self, expected: dict) -> bool:
        required_files = (
            self.index_dir / "index.faiss",
            self.index_dir / "index.pkl",
            self.manifest_path,
        )
        if not all(path.is_file() for path in required_files):
            return False
        try:
            current = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            return False
        return current == expected

    def _build_index(self, expected: dict) -> FAISS:
        chunks = DocsIngestor(self.docs_dir).ingest_docs()
        vectorstore = FAISS.from_documents(chunks, self.embeddings_model)
        self.index_dir.mkdir(parents=True, exist_ok=True)
        vectorstore.save_local(str(self.index_dir))
        self.manifest_path.write_text(
            json.dumps(expected, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        return vectorstore

    def retrieve(self):
        expected = self._expected_manifest()
        if self._index_is_current(expected):
            # Solo se deserializa un índice cuya huella coincide con los PDF y
            # parámetros locales actuales.
            self.vectorstore = FAISS.load_local(
                str(self.index_dir),
                self.embeddings_model,
                allow_dangerous_deserialization=True,
            )
        else:
            self.vectorstore = self._build_index(expected)

        return self.vectorstore.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": RETRIEVER_K,
                "score_threshold": RELEVANCE_THRESHOLD,
            },
        )
