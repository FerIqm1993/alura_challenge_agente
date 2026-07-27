# Fuentes documentales

El repositorio incluye los tres PDF que necesita el despliegue:

- `guia_corto_circuito_casings.pdf`
- `Guia_estudio_pruebas_ducto_camisa_cortos_electroliticos.pdf`
- `SP0200-2014-Steel-Cased-Pipeline-Practices.pdf`

El código conserva archivo y página durante la ingesta para mostrar citas
verificables. Antes de redistribuir o reutilizar estas fuentes, corresponde
comprobar que su uso sea compatible con las licencias aplicables.

Al iniciar la aplicación, `src/vectorstore.py` genera un índice local en
`data/faiss_index/`. Esa carpeta también se excluye del repositorio público.
