from __future__ import annotations

import sys
from pathlib import Path

from langchain_core.documents import Document

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from chain import (  # noqa: E402
    OUT_OF_SCOPE_MESSAGE,
    RagAgent,
    _citaciones_desde_documentos,
    is_casing_inspection_question,
)
from ingest import DocsIngestor  # noqa: E402
from vectorstore import source_fingerprint  # noqa: E402


class FakeRetriever:
    def __init__(self, documents):
        self.documents = documents
        self.calls = 0

    def invoke(self, _question):
        self.calls += 1
        return self.documents


class FakeChain:
    def __init__(self, answer):
        self.answer = answer
        self.calls = 0

    def invoke(self, _payload):
        self.calls += 1
        return self.answer


def test_scope_guard_accepts_casing_questions_and_rejects_general_topics():
    assert is_casing_inspection_question(
        "¿Cómo distingo un corto electrolítico en una camisa?"
    )
    assert is_casing_inspection_question(
        "¿Qué indica NACE en la prueba pipe-to-casing?"
    )
    assert not is_casing_inspection_question(
        "¿Cuál es el criterio general de protección catódica?"
    )
    assert not is_casing_inspection_question("¿Cómo estará el clima mañana?")


def test_out_of_scope_question_does_not_call_retriever_or_llm():
    retriever = FakeRetriever([])
    chain = FakeChain({})
    agent = RagAgent(retriever=retriever, document_chain=chain)

    result = agent.busqueda_de_respuestas_RAG("¿Cómo escribo una API en Python?")

    assert result["respuesta"] == OUT_OF_SCOPE_MESSAGE
    assert result["fuera_de_alcance"] is True
    assert retriever.calls == 0
    assert chain.calls == 0


def test_answer_contains_deduplicated_page_citations():
    docs = [
        Document(
            page_content="Primer fragmento",
            metadata={"file_name": "guia_corto_circuito_casings.pdf", "page": 1},
        ),
        Document(
            page_content="Segundo fragmento de la misma página",
            metadata={"file_name": "guia_corto_circuito_casings.pdf", "page": 1},
        ),
    ]
    citations = _citaciones_desde_documentos(docs)

    assert len(citations) == 1
    assert citations[0]["pagina"] == 2
    assert "pág. 2" in citations[0]["etiqueta"]


def test_agent_returns_grounded_answer_and_sources():
    docs = [
        Document(
            page_content="La camisa sigue el cambio de forma atenuada.",
            metadata={"file_name": "guia_corto_circuito_casings.pdf", "page": 2},
        )
    ]
    agent = RagAgent(
        retriever=FakeRetriever(docs),
        document_chain=FakeChain(
            {
                "pregunta": "pregunta",
                "respuesta": "La respuesta atenuada es compatible con acoplamiento.",
                "documentos_encontrados": True,
            }
        ),
    )

    result = agent.busqueda_de_respuestas_RAG(
        "¿Qué significa una respuesta atenuada de la camisa?"
    )

    assert result["documentos_encontrados"] is True
    assert result["citaciones"][0]["pagina"] == 3


def test_real_pdfs_are_ingested_with_page_metadata():
    chunks = DocsIngestor().ingest_docs()
    file_names = {chunk.metadata["file_name"] for chunk in chunks}

    assert len(file_names) == 3
    assert all(isinstance(chunk.metadata.get("page"), int) for chunk in chunks)
    assert all(chunk.page_content.strip() for chunk in chunks)


def test_source_fingerprint_changes_when_a_pdf_changes(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    pdf = docs_dir / "fuente.pdf"
    pdf.write_bytes(b"version uno")
    first = source_fingerprint(docs_dir)
    pdf.write_bytes(b"version dos")

    assert source_fingerprint(docs_dir) != first
