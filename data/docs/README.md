# Fuentes locales

Coloca en esta carpeta, sin cambiar sus nombres:

- `guia_corto_circuito_casings.pdf`
- `Guia_estudio_pruebas_ducto_camisa_cortos_electroliticos.pdf`
- `SP0200-2014-Steel-Cased-Pipeline-Practices.pdf`

Los archivos PDF están excluidos de Git para respetar sus licencias y evitar la
redistribución accidental de documentación técnica. El código conserva archivo
y página durante la ingesta para mostrar citas verificables.

Al iniciar la aplicación, `src/vectorstore.py` genera un índice local en
`data/faiss_index/`. Esa carpeta también se excluye del repositorio público.
