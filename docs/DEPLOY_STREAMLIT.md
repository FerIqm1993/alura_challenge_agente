# Despliegue en Streamlit Community Cloud

La aplicación obtiene `GROQ_API_KEY` y `GROQ_MODEL` desde variables de entorno.
En Streamlit Community Cloud deben configurarse en **App settings > Secrets**
como valores TOML de nivel raíz:

```toml
GROQ_API_KEY = "TU_CLAVE_DE_GROQ"
GROQ_MODEL = "llama-3.3-70b-versatile"
```

No se debe crear ni subir un archivo `.env` para el despliegue. Streamlit
expone los secretos TOML de nivel raíz como variables de entorno, por lo que no
es necesario cambiar el código que utiliza `os.getenv`.

Después de guardar los secretos, espera su propagación y reinicia la
aplicación desde Streamlit Community Cloud. Si Groq responde con
`expired_api_key`, reemplaza la clave por una nueva y vuelve a reiniciar.

## Desarrollo local

Para ejecutar la aplicación fuera de Streamlit Community Cloud, crea `.env` a
partir de `.env.example` y agrega la clave únicamente en el archivo local:

```powershell
Copy-Item .env.example .env
```

`.env` y `.streamlit/secrets.toml` están excluidos mediante `.gitignore`.
