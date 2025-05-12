# Chatbot Recepcionista - Langchain + Gemini + Streamlit

Este proyecto implementa un **chatbot de recepción** especializado en turismo, construido con [Streamlit](https://streamlit.io/), [Langchain](https://python.langchain.com/), y el modelo **Gemini** de Google. El asistente responde preguntas sobre destinos turísticos, atracciones, viajes y temas relacionados, utilizando tanto información interna (RAG) como búsqueda web.

## Características

- **Interfaz web interactiva** con Streamlit.
- **RAG (Retrieval-Augmented Generation):** utiliza documentos internos para responder preguntas específicas del negocio.
- **Búsqueda web** integrada con DuckDuckGo para información general y eventos actuales.
- **Historial de chat** persistente por sesión.
- **Modelo Gemini** de Google para generación de respuestas.
- **Fácil extensión** de fuentes de datos agregando archivos `.txt` en la carpeta `data/`.

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

4. **Configura tu clave de API de Google Gemini:**
   - Crea un archivo `secrets.toml` en la carpeta `.streamlit` o usa variables de entorno
   - Debes definir `GOOGLE_API_KEY`

## Ejecución

Para iniciar la aplicación localmente:

```sh
make local
```
o directamente:
```sh
streamlit run Home.py --server.port=8501 --server.address=0.0.0.0
```

Abre tu navegador en [http://localhost:8501](http://localhost:8501).

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

- **Cambiar modelo LLM:** [aquí](./utils.py#15) podras cambiar el modelo LLM utilizado
- **Agregar información interna:** coloca archivos `.txt` en la carpeta `data/` para que sean indexados por el RAG.
- **Modificar el prompt del sistema:**  modifica el propmt en `pages/Chatbot.py` y mantén actualizado `docs/SYSTEM_PROMT_HISTORY.md` con tu nueva versión.

## TODO

- Usar containers (con hot reload)
- Cambiar Gemini por Ollama para uso de modelo local
- Crear una API que simule un sistema de hotel con consultas y reservas
- Conectar el modelo con esta API como una tool para que realice acciones mediante el chat
- Integrar con Google Account para simular acciones a nombre del usuario particular
- Permitir capturar ubicación geográfica para el contexto
- Captura de gustos y preferecias del usuario
  - Utilizar un LLM para extracción (excluir datos personales)
  - Convertir a embeddings
  - Almacenamiento en BBDD Vectorial
  - Integración en el contexto de la conversación

## Referencias

[Basic Chatbot from shashankdeshpande](https://github.com/shashankdeshpande/langchain-chatbot/blob/master/pages/1_%F0%9F%92%AC_basic_chatbot.py)
