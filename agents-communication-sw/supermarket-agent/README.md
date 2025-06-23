# SuperMarket Agent

Este agente tiene como funcionalidades:
 - Responder que items hay disponibles en el supermercado
 - Comprar items del supermercado
 - Reponer los items del supermercado, para esto deberá comunicarse con un agente mayorista que le confirmará que pude reponer y qué no

## Características

- **Interfaz web interactiva** con Streamlit.
- **Historial de chat** persistente por sesión.
- **Modelo Gemini** de Google para generación de respuestas.

## Instalación

1. **Clona el repositorio:**
   ```sh
   git clone https://github.com/tu_usuario/desarrollo-de-softbots-y-robots.git
   cd desarrollo-de-softbots-y-robots/agents-communication-sw/supermarket-agent
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
   - Debes definir:
     - `GOOGLE_API_KEY` (Gemini)

## Ejecución

Para iniciar la aplicación localmente:

```sh
make local
```
o directamente:
```sh
streamlit run Home.py --server.port=8503 --server.address=0.0.0.0
```

Abre tu navegador en [http://localhost:8503](http://localhost:8503)