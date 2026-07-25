# Historial de versiones

## 1.0.1 - 2026-07-25

- Corrige el arranque directo con `python app.py`.
- Detecta la ausencia del contexto de Streamlit y relanza la aplicación mediante
  su CLI antes de utilizar `session_state`.
- Mantiene compatibilidad con el comando habitual `streamlit run app.py`.

## 1.0.0 - 2026-07-25 - Primera versión

- Agente RAG especializado en inspección y diagnóstico de encamisados.
- Integración con Groq y `llama-3.3-70b-versatile`.
- Ingesta de dos guías técnicas y NACE SP0200-2014.
- Recuperación semántica local mediante embeddings multilingües y FAISS.
- Control conservador para rechazar preguntas fuera del alcance.
- Respuestas sustentadas con citas por documento y página.
- Regeneración automática del índice cuando cambian las fuentes.
- Interfaz Streamlit con historial y visualización de fragmentos.
- Pruebas automatizadas de alcance, ingesta, citas y huella documental.
- Configuración segura para excluir claves y documentos licenciados de Git.
