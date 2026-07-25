"""Lectura y segmentación de las fuentes PDF del agente."""

from __future__ import annotations

from pathlib import Path

from langchain_community.document_loaders import PyMuPDFLoader
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter

from helper import CHUNK_OVERLAP, CHUNK_SIZE

DOCS_DIR = Path(__file__).resolve().parent.parent / "data" / "docs"


class DocsIngestor:
    """Carga únicamente PDF y conserva archivo y página para las citas."""

    def __init__(self, docs_dir: Path = DOCS_DIR):
        self.docs_dir = Path(docs_dir)

    def ingest_docs(self) -> list[Document]:
        pdfs = sorted(self.docs_dir.glob("*.pdf"), key=lambda path: path.name.lower())
        if not pdfs:
            raise FileNotFoundError(f"No se encontraron PDF en {self.docs_dir}")

        pages: list[Document] = []
        errors: list[str] = []

        for pdf_path in pdfs:
            try:
                loaded_pages = PyMuPDFLoader(str(pdf_path)).load()
                for page in loaded_pages:
                    page.metadata["source"] = str(pdf_path.resolve())
                    page.metadata["file_name"] = pdf_path.name
                pages.extend(loaded_pages)
            except Exception as exc:  # pragma: no cover - depende del PDF dañado
                errors.append(f"{pdf_path.name}: {exc}")

        if errors:
            raise RuntimeError("No fue posible cargar todas las fuentes: " + "; ".join(errors))
        if not pages:
            raise RuntimeError("Los PDF no produjeron páginas con contenido.")

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            separators=["\n\n", "\n", ". ", " ", ""],
        )
        return splitter.split_documents(pages)
