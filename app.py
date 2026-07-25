"""Interfaz Streamlit del Asistente en Protección Catódica."""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

sys.path.insert(0, str(Path(__file__).parent / "src"))

from chain import RagAgent

st.set_page_config(
    page_title="Asistente en Protección Catódica",
    page_icon="🛡️",
    layout="centered",
)

PALETTE_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap');
html, body, [class*="css"] { font-family: 'IBM Plex Sans', sans-serif; }
h1, h2, h3 { color: #17324D; font-weight: 700; }
.stChatMessage { border: 1px solid #CCD8E2; border-radius: 12px; }
.source-note {
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.75rem;
    color: #566573;
}
</style>
"""
st.markdown(PALETTE_CSS, unsafe_allow_html=True)


@st.cache_resource(show_spinner="Preparando documentos e índice de búsqueda...")
def cargar_agente() -> RagAgent:
    return RagAgent()


def render_citas(citas: list[dict]) -> None:
    if not citas:
        return
    st.caption("Fuentes consultadas")
    for cita in citas:
        with st.expander(cita["etiqueta"]):
            st.write(cita["contenido"])


with st.sidebar:
    st.markdown("### Alcance")
    st.write(
        "Responde exclusivamente sobre **inspección y diagnóstico de ductos "
        "encamisados**, con base en dos guías técnicas y NACE SP0200-2014."
    )
    st.markdown("**Preguntas de ejemplo**")
    st.markdown(
        "- ¿Cómo se distingue un corto metálico de uno electrolítico en una camisa?\n"
        "- ¿Qué mediciones deben registrarse en una prueba ducto-camisa?\n"
        "- ¿Cómo interpreta NACE SP0200-2014 una camisa eléctricamente aislada?\n"
        "- ¿Dónde debe colocarse el electrodo de referencia en una prueba de encamisado?"
    )
    st.info(
        "Las respuestas sirven como apoyo documental y no sustituyen "
        "procedimientos aprobados ni el criterio de ingeniería."
    )

st.title("Asistente en Protección Catódica")
st.caption("Consulta técnica de inspección de encamisados con citas por página.")

try:
    agente = cargar_agente()
except Exception as exc:
    st.error(f"No fue posible iniciar el agente: {exc}")
    st.info("Verifica GROQ_API_KEY y las dependencias; después reinicia la aplicación.")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []

for mensaje in st.session_state.messages:
    with st.chat_message(mensaje["role"]):
        st.write(mensaje["content"])
        if mensaje["role"] == "assistant":
            render_citas(mensaje.get("citaciones", []))

pregunta = st.chat_input("Pregunta sobre inspección de encamisados...")

if pregunta:
    st.session_state.messages.append({"role": "user", "content": pregunta})
    with st.chat_message("user"):
        st.write(pregunta)

    with st.chat_message("assistant"):
        with st.spinner("Consultando las fuentes técnicas..."):
            try:
                resultado = agente.busqueda_de_respuestas_RAG(pregunta)
            except Exception as exc:
                resultado = {
                    "respuesta": (
                        "No fue posible consultar el modelo en este momento. "
                        f"Detalle: {exc}"
                    ),
                    "citaciones": [],
                    "documentos_encontrados": False,
                }
        st.write(resultado["respuesta"])
        render_citas(resultado.get("citaciones", []))
        if not resultado.get("documentos_encontrados"):
            st.markdown(
                '<span class="source-note">Sin evidencia documental citada.</span>',
                unsafe_allow_html=True,
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": resultado["respuesta"],
            "citaciones": resultado.get("citaciones", []),
            "documentos_encontrados": resultado.get(
                "documentos_encontrados", False
            ),
        }
    )
