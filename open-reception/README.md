# Open Reception

Este proyecto implementa un **chatbot de recepción** especializado en turismo, construido con [Streamlit](https://streamlit.io/), [Langchain](https://python.langchain.com/), y el modelo **Gemini** de Google. El asistente responde preguntas sobre destinos turísticos, atracciones, viajes y temas relacionados, utilizando tanto información interna (RAG) como búsqueda web.

## Características

- **Interfaz web interactiva** con Streamlit.
- **RAG (Retrieval-Augmented Generation):** utiliza documentos internos para responder preguntas específicas del negocio.
- **Búsqueda web** integrada con Google Search para información general y eventos actuales.
- **Historial de chat** persistente por sesión.
- **Modelo Gemini** de Google para generación de respuestas.
- **Fácil extensión** de fuentes de datos agregando archivos `.txt` en la carpeta `data/`.
- **Despliegue con Docker Compose:** Incluye servicios para la app (Streamlit) y la base vectorial Qdrant, ambos listos para desarrollo o producción local.

## Instalación

1. **Clona el repositorio:**
   ```sh
   git clone https://github.com/tu_usuario/desarrollo-de-softbots-y-robots.git
   cd desarrollo-de-softbots-y-robots
   ```

2. **Crea un entorno virtual y activa:**
   ```sh
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Instala las dependencias:**
   ```sh
   pip install -r requirements.txt
   ```

   > **Nota:** El almacenamiento vectorial y la integración con Qdrant ahora usan `langchain-qdrant` (no `qdrant-client` directo).

4. **Configura tu clave de API de Google Gemini y Google Search:**
   - Crea un archivo `secrets.toml` en la carpeta `.streamlit` o usa variables de entorno
   - Debes definir:
     - `GOOGLE_API_KEY` (Gemini)
     - `GOOGLE_SEARCH_ENGINE_ID` (Google Custom Search Engine ID)
     - `GOOGLE_SEARCH_API_KEY` (Google Programmable Search API Key)

## Ejecución

Para iniciar la aplicación localmente:

```sh
make up
make local
```
o directamente:
```sh
docker-compose up --build
streamlit run Home.py --server.port=8501 --server.address=0.0.0.0
```

Con esto levanta el container de Qdrant y luego la aplicación con Streamlit.
Abre tu navegador en [http://localhost:8501](http://localhost:8501).

## Ejecución con Docker Compose (working on progress, still too slow to build)

Para levantar toda la solución (chatbot + base vectorial Qdrant) ejecuta:

```sh
docker-compose up --build
```

Esto iniciará:
- El chatbot en [http://localhost:8501](http://localhost:8501)
- Qdrant en [http://localhost:6333](http://localhost:6333) (API REST)

Los datos vectoriales y la información de usuario se almacenan de forma persistente en el volumen `qdrant_data`.

Puedes detener todo con:
```sh
docker-compose down
```

## Variables de entorno y configuración

- El contenedor `chatbot` se conecta automáticamente a Qdrant usando las variables `QDRANT_HOST` y `QDRANT_PORT` definidas en el `docker-compose.yml`.
- Las claves de API y configuración sensible deben ir en `.streamlit/secrets.toml` (montado por defecto en el contenedor si está en el proyecto).

## Uso

- Accede a la página principal para ver la bienvenida.
- Ve a la pestaña **Chatbot** para interactuar con el asistente.
- Puedes hacer preguntas sobre turismo, reservas, servicios, etc.
- El chatbot usará primero los documentos internos y, si es necesario, buscará en la web.

## Historial de SYSTEM PROMPTS

[Aquí](./docs/SYSTEM_PROMT_HISTORY.md) podrás ver el historial de cambios de o los sys prompts

## Arquitectura

[Aquí](./docs/ARCH.md) podrás ver gráficos de la solución (in progress)

## Personalización

- **Almacenamiento vectorial:** El sistema utiliza Qdrant a través de `langchain-qdrant` para toda la persistencia de embeddings y preferencias de usuario.
- **Cambiar modelo LLM:** [aquí](./utils.py#15) podras cambiar el modelo LLM utilizado
- **Agregar información interna:** coloca archivos `.txt` en la carpeta `data/` para que sean indexados por el RAG.
- **Modificar el prompt del sistema:**  modifica el propmt en `pages/Chatbot.py` y mantén actualizado `docs/SYSTEM_PROMT_HISTORY.md` con tu nueva versión.
- **Cambiar motor de búsqueda web:** El sistema ahora utiliza Google Search API en vez de DuckDuckGo. Puedes ajustar la configuración en `utils.py` y las claves en `.streamlit/secrets.toml`.

## TODO

- Usar containers (con hot reload)
- Cambiar Gemini por Ollama para uso de modelo local
- Crear una API que simule un sistema de hotel con consultas y reservas
- Conectar el modelo con esta API como una tool para que realice acciones mediante el chat
- Integrar con Google Account para simular acciones a nombre del usuario particular
- Permitir capturar ubicación geográfica para el contexto
- Conectar con API de Google Maps ¿puedo mostrar el mapa en el chat?
- Captura de gustos y prefereencias del usuario
  - Utilizar un LLM para extracción (excluir datos personales)
  - Convertir a embeddings
  - Almacenamiento en BBDD Vectorial
  - Integración en el contexto de la conversación

## Referencias

[Basic Chatbot from shashankdeshpande](https://github.com/shashankdeshpande/langchain-chatbot/blob/master/pages/1_%F0%9F%92%AC_basic_chatbot.py)

- **Makefile** con comandos útiles: `make build`, `make up`, `make down`, `make logs`, `make lint` (usa flake8), y `make local` para desarrollo rápido.

## Comandos útiles (Makefile)

- `make build`   — Construye las imágenes Docker
- `make up`      — Levanta todo el stack (chatbot + Qdrant)
- `make down`    — Detiene y elimina los contenedores
- `make logs`    — Muestra logs en tiempo real
- `make lint`    — Corre flake8 sobre el código Python para asegurar calidad
- `make local`   — Ejecuta Streamlit localmente sin Docker

> Para usar `make lint` instala flake8 si no lo tienes: `pip install flake8`
