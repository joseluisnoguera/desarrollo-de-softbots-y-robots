# Journalists Discussions

Este proyecto utiliza las herramientas de Langchain, Gemini y Streamlit para brindar una herramienta de discusión entre agentes de AI, actualmente sólo desarrollado para utilizar modelos de Gemini.

## Características

- **Interfaz web interactiva** con Streamlit.
- **Historial de chat** persistente por sesión.
- **Modelo Gemini** de Google para generación de respuestas.

## Instalación

1. **Clona el repositorio:**
   ```sh
   git clone https://github.com/tu_usuario/desarrollo-de-softbots-y-robots.git
   cd desarrollo-de-softbots-y-robots/agents-communication-journalists
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

4. **Configura tu clave de API de Google Gemini y Google Search:**
   - Crea un archivo `secrets.toml` en la carpeta `.streamlit` o usa variables de entorno
   - Debes definir:
     - `GOOGLE_API_KEY` (Gemini)

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


## Funcionalidades

### Ventana de temas

Aquí se visualiza sólo un input de texto libre, en el cuál el usuario puede cargar un tema a que se pueda discutir entre los dos agentes "Periodistas".
Esto se le enviará a un agente que tiene por objetivo:
 - Dar una versión méjorada del tema a tratar, preparado para ser usado como input para modelos
 - Brindar dos posibles posturas opuestas que se pueden tomar sobre este tema
Visualmente, la respuesta se dara:
  - Tema a tratar mejorado en un campo de texto no editable
  - Posibles posturas opuestas mediante dos campos de texto no editables que ocupan la mitad de la visual cada uno, uno al lado del otro

### Ventana de conversación

Se visualiza un chat, en el cual participarán los dos agentes (agentes independientes entre si)
A la izquierda se tiene un menú con tres bloques de configuración, uno general sobre la conversación en el cuál:
 - Se puede definir el tema de discusión
 - Se puede configurar cuantos mensajes permitir a los agentes durante la conversación (mínimo 1, máximo 10)
 - Botón de continuar con conversación, que toma el valor de cantida de mensaje que pueden mandarse al momento de accionar

Luego, los otros dos bloques representan las configución particular por cada agente, sin que estas pueda modificar su role como "Periodistas", en el cual en cada uno se puede:
 - Configurar "Personalidad" del agente mediante un campo de texto libre
 - Configuración de "postura" del agente sobre el tema a conversar

El accionar de iniciar la conversación no puede darse si no hay un tema de conversación inicial, luego de iniciada la conversación este campo no es modificable, o si a alguno de los agentes "Periodistas" les falta su postura, siendo estos campos de postura modificables sobre cada iteración de la conversación, pero no pueden estar vacíos para continuar tocar el botón de continuar conversación.

### TODO

[] Agregar más agentes y poder configurar cada "Periodista" con distintos modelos