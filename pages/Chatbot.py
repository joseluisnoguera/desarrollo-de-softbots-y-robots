import utils
import streamlit as st
import os
import json

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.schema import format_document


st.set_page_config(page_title="Chatbot", page_icon="💬")
st.header('Chatbot Recepcionista')

# Definir la ruta del archivo de configuración
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "chatbot_config.json")

# Función para cargar la configuración
def load_config():
    default_config = {
        "BEHAVIOUR_STR": "profesional",
        "TOPICS_STR": "turismo, puntos de interes para turístas, eventos turísticos, direcciones para llegar a lugares turísticos, comercios que utilizarían turistas, atracciones, viajes, eventos que pueden ser de interes para turistas como eventos deportivos, temas relacionados con turismo",
        "BLOCKLIST_STR": "tomar posiciones políticas, religión, temas sensibles, temas no relacionados a los estipulados anteriormente."
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            st.warning("Error al cargar la configuración personalizada. Usando configuración predeterminada.")
            return default_config
    return default_config

# Cargar configuración
config = load_config()
BEHAVIOUR_STR = config["BEHAVIOUR_STR"]
TOPICS_STR = config["TOPICS_STR"]
BLOCKLIST_STR = config["BLOCKLIST_STR"]

DEFAULT_DOCUMENT_PROMPT = PromptTemplate.from_template(template="{page_content}")

def _combine_documents(docs, document_prompt=DEFAULT_DOCUMENT_PROMPT, document_separator="\n\n---\n\n"):
    """Combina documentos recuperados en una sola cadena, separados por un separador claro."""
    doc_strings = [format_document(doc, document_prompt) for doc in docs]
    return document_separator.join(doc_strings)

class BasicChatbot:

    def __init__(self):
        utils.sync_st_session()
        self.llm = utils.configure_llm()
        self.retriever = utils.get_retriever()
        self.web_search_tool = utils.get_web_search_tool()

    def setup_chain(self):
        tools = []
        if self.retriever:
            retriever_tool = create_retriever_tool(
                self.retriever,
                "search_private_documents",
                "Busca y devuelve extractos relevantes de documentos internos del negocio sobre servicios de turismo, costos e información interna. Úsala primero si la pregunta parece sobre información específica del negocio." # Descripción para el agente
            )
            tools.append(retriever_tool)

        if self.web_search_tool:
            tools.append(self.web_search_tool)

        if not tools:
             st.error("No se pudieron inicializar herramientas (Retriever o Búsqueda Web). El agente no puede funcionar.")
             return None

        # --- Agente ReAct ---
        agent_prompt_template = f"""
Eres un asistente virtual de recepción especializado EXCLUSIVAMENTE en {TOPICS_STR}. Te comportarás de manera {BEHAVIOUR_STR}.
Tu única función es proporcionar información y responder preguntas sobre los temas en los cuales estás especializado, y si es necesario, desviar la conversación a esos temas.
No debes {BLOCKLIST_STR}. Si la pregunta no es relevante, responde con un mensaje claro y útil que explique que no puedes ayudar con eso.

Además, haz preguntas sutiles y breves para conocer un poco más al usuario, como sus gustos, intereses, preferencias o necesidades relacionadas con turismo, para poder personalizar mejor la atención en el futuro. Si ya tienes información previa sobre el usuario, puedes usarla para personalizar la conversación.
Deberás dar una respuesta útil más allá de que aún no conozcas todas las preferencias del usuario. No debes hacer preguntas demasiado personales o invasivas.
Si notas que el usuario intenta hablar de temas no relacionados con los que tienes habilitados, redirige la conversación a los temas que sí puedes tratar.

Tienes acceso a las siguientes herramientas:

{{tools}}

Usa el siguiente formato estricto:

Question: la pregunta de entrada que debes responder
Thought: Siempre debes pensar qué hacer. Considera el historial de chat para una continuación de la conversación y la información del usuario que se ha podido conseguir. Primero, evalúa si la pregunta es sobre los temas exclusivos que puedes tratar. Si no lo es, o si puedes responder directamente sin necesidad de herramientas, debes responder directamente en 'Final Answer'. Si la pregunta es relevante y necesitas información adicional, evalúa si parece requerir información interna específica del negocio (costos, detalles de servicios propios) y usa la herramienta 'search_private_documents'. Si 'search_private_documents' no proporciona una respuesta suficiente o la pregunta requiere información actualizada, fechas o lugares particulares, considera usar 'serper_search'. Solo usa una herramienta por ciclo de Action.
Action: la acción a tomar, debe ser una de [{{tool_names}}]
Action Input: la entrada para la acción
Observation: el resultado de la acción
... (este ciclo Thought/Action/Action Input/Observation puede repetirse 3 veces si es necesario refinar la búsqueda o usar otra herramienta)
Thought: Ahora sé la respuesta final basada en las Observaciones y el Historial de Chat. Voy a formular la respuesta final. No antepongas 'AI:' ni ningún prefijo a tus respuestas. Asegúrate de que la respuesta sea clara y útil.
Final Answer: la respuesta final a la pregunta original del usuario. Si declinas responder, explícalo aquí.

¡Comienza ahora!

Historial de Chat Previo:
{{chat_history}}

New Question: {{input}}
{{agent_scratchpad}}
"""
        prompt = PromptTemplate.from_template(agent_prompt_template)

        agent = create_react_agent(self.llm, tools, prompt)

        agent_executor = AgentExecutor(
            agent=agent,
            tools=tools,
            verbose=True,
            handle_parsing_errors=True,
            max_iterations=5
        )

        def get_session_history(session_id):
            return StreamlitChatMessageHistory(key=f"agent_history_{session_id}")

        agent_with_history = RunnableWithMessageHistory(
            agent_executor,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
        )

        return agent_with_history


    def preprocess_user_query(self, user_query):
        logger = utils.logger
        pre_llm = utils.configure_llm()

        chat_history = []
        for msg in st.session_state.get("messages", []):
            if msg["role"] == "user":
                chat_history.append(f"Usuario: {msg['content']}")
            elif msg["role"] == "assistant":
                chat_history.append(f"Asistente: {msg['content']}")
        chat_history_str = "\n".join(chat_history[-10:])

        combined_prompt = (
            f"Eres un filtro inteligente y asistente virtual para un chatbot recepcionista profesional especializado en {TOPICS_STR} que no debe {BLOCKLIST_STR}. "
            f"Evalúa si el mensaje del usuario está relacionado con estos temas. No seas extremadamente literal, si te falta información o el mensaje es ambiguo, dejalo pasar. "
            f"Si el mensaje está relacionado o tiene alguna conexión con estos temas, responde únicamente con '__SCOPE_OK__'. "
            f"Si NO está relacionado, responde con un mensaje amable que:\n"
            f"1. Explique brevemente que no puedes responder a ese tema específico\n"
            f"2. Mencione los temas sobre los que sí puedes hablar\n"
            f"3. Ofrezca una o dos sugerencias concretas relacionadas con {TOPICS_STR} para redirigir la conversación\n"
            f"4. Si es posible, conecta tu respuesta con el contexto de la conversación previa.\n\n"
            f"Historial reciente de la conversación:\n{chat_history_str}\n\n"
            f"Usuario: {user_query}\nRespuesta:"
        )

        try:
            response = pre_llm.invoke(combined_prompt)
            logger.debug(f"RAW Combined Response: {response}")

            if hasattr(response, 'content'):
                result = response.content.strip()
            else:
                result = str(response).strip()
            logger.info(f"Combined filter result: '{result}'")

            if result == "__SCOPE_OK__":
                logger.info("Message in context.")
                return (user_query, True)
            else:
                logger.debug("Message out of context. Returning custom response.")
                return (result, False)

        except Exception as e:
            logger.error(f"LLM Combined Filter exception: {e}")
            logger.info("Allowing original message to pass through.")
            return (user_query, True)


    @utils.enable_chat_history
    def main(self):
        # Generate a unique session ID for the current user
        if "session_id" not in st.session_state:
            st.session_state.session_id = utils.generate_uuid()
        session_id = st.session_state.session_id

        agent_runnable = self.setup_chain()

        if not agent_runnable:
             st.warning("El agente no pudo ser inicializado.")
             return

        # --- Manejo de cambio de usuario simulado y su historial ---
        selected_user_uuid = st.session_state.get("selected_user_uuid", None)
        if selected_user_uuid:
            session_id = selected_user_uuid  # Forzar que session_id sea el usuario seleccionado
            current_messages_key = f"messages_{selected_user_uuid}"
            # Si no existe historial para este usuario, inicializarlo con mensaje de bienvenida
            if current_messages_key not in st.session_state or not st.session_state[current_messages_key]:
                st.session_state[current_messages_key] = [
                    {"role": "assistant", "content": "¡Hola! Soy tu recepcionista virtual. ¿En qué puedo ayudarte hoy?"}
                ]
            # Si el historial global no corresponde al usuario seleccionado, sincronizar
            if st.session_state.get("messages", None) != st.session_state[current_messages_key]:
                # Antes de cambiar, guarda el historial actual en la clave del usuario anterior
                previous_user_uuid = st.session_state.get("_last_user_uuid", None)
                if previous_user_uuid and previous_user_uuid != selected_user_uuid:
                    st.session_state[f"messages_{previous_user_uuid}"] = st.session_state.get("messages", [])
                # Carga el historial del usuario seleccionado
                st.session_state["messages"] = st.session_state[current_messages_key]
                st.session_state["_last_user_uuid"] = selected_user_uuid
        # --- Fin manejo de cambio de usuario ---

        for msg in st.session_state.get("messages", []):
            st.chat_message(msg["role"]).write(msg["content"])

        user_query = st.chat_input(placeholder="¡Escribe cualquier consulta!")
        if user_query:
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.chat_message("user").write(user_query)

            # --- Preprocesamiento con LLM filtro ---
            preprocessed_query, continue_to_agent = self.preprocess_user_query(user_query)
            user_info_key = f"user_info_{session_id}"
            # Extraer y guardar información del usuario SIEMPRE, incluso fuera de contexto
            self.extract_and_store_user_info(user_query, session_id)

            if not continue_to_agent:
                st.session_state.messages.append({"role": "assistant", "content": preprocessed_query})
                st.chat_message("assistant").write(preprocessed_query)
                utils.print_qa(BasicChatbot, user_query, preprocessed_query)
                return

            # Usar la información del usuario para personalizar la respuesta
            user_info_key = f"user_info_{selected_user_uuid}"
            user_info_blocks = st.session_state.get(user_info_key, [])
            # Construir resumen breve de preferencias
            def resumen_preferencias(info_blocks):
                resumen = []
                for block in info_blocks:
                    if isinstance(block, dict):
                        for k, v in block.items():
                            if k == "texto_no_json":
                                continue
                            if isinstance(v, list):
                                resumen.append(f"{k}: {', '.join(map(str, v))}")
                            else:
                                resumen.append(f"{k}: {v}")
                return "; ".join(resumen)
            resumen_usuario = resumen_preferencias(user_info_blocks)
            logger = utils.logger
            logger.debug(f"[DEBUG] Preferencias usadas para contexto: {resumen_usuario}")
            print(f"[DEBUG] Preferencias usadas para contexto: {resumen_usuario}")
            if resumen_usuario:
                contexto_usuario = f"Esta es la última información que tienes de mi: {resumen_usuario}. Ajusta tu respuesta en base a esto, personaliza también como escribes el mensaje. "
            else:
                contexto_usuario = ""

            chat_history = []
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    chat_history.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    chat_history.append({"role": "assistant", "content": msg["content"]})

            with st.chat_message("assistant"):
                response_container = st.empty()
                try:
                    # Inyectar contexto de usuario en el input del agente SIEMPRE
                    agent_input = contexto_usuario + preprocessed_query
                    response = agent_runnable.invoke(
                        {"input": agent_input, "chat_history": chat_history},
                        config={"configurable": {"session_id": session_id}}
                    )
                    final_response_text = response.get('output', "(No se obtuvo respuesta del agente)")
                except Exception as e:
                    final_response_text = f"Error al ejecutar el agente: {e}"
                    st.error(final_response_text)
                    print(f"Agent execution error: {e}")
                response_container.text(final_response_text)
            st.session_state.messages.append({"role": "assistant", "content": final_response_text})
            utils.print_qa(BasicChatbot, preprocessed_query, final_response_text)

    def extract_and_store_user_info(self, user_message, user_uuid):
        from utils import save_user_info_to_disk, load_user_info_from_disk
        import re
        # Recuperar preferencias previas
        key = f"user_info_{user_uuid}"
        prev = st.session_state.get(key, None)
        if prev is None:
            prev = load_user_info_from_disk(user_uuid)
        if isinstance(prev, str):
            try:
                prev_loaded = json.loads(prev)
                if isinstance(prev_loaded, list):
                    prev = prev_loaded
                elif isinstance(prev_loaded, dict):
                    prev = [prev_loaded]
                else:
                    prev = []
            except Exception:
                prev = []
        elif isinstance(prev, dict):
            prev = [prev]
        elif not isinstance(prev, list):
            prev = []
        preferencias_actuales = prev[-1] if prev else {}
        extract_prompt = (
            "Dado el siguiente mensaje de usuario y sus preferencias actuales, genera una nueva versión de las preferencias del usuario. Enfocate en información que sirva para personalizar la atención al cliente. "
            "Detecta también preferencias comunicacionales, como tono, formalidad, etc. "
            "No es necesario que la respuesta sea exhaustiva, pero intenta incluir información útil. "
            "No repitas información que ya esté en las preferencias actuales. "
            "Elimina o actualiza datos que ya no sean válidos (por ejemplo, ubicación, gustos cambiantes, etc). Sólo borralo si estás seguro que ya no es válido. En caso de duda no lo borres."
            "Responde SOLO en formato JSON válido, sin texto adicional. Si no hay información útil, responde exactamente con '__NO_INFO__'.\n"
            f"Preferencias actuales: {json.dumps(preferencias_actuales, ensure_ascii=False)}\n"
            f"Mensaje del usuario: '{user_message}'\n"
            "Ejemplo de respuesta: {\"gustos\": [\"playa\", \"música\"], \"preferencias\": [\"hoteles económicos\"]}"
        )
        llm = utils.configure_llm()
        try:
            response = llm.invoke(extract_prompt)
            if hasattr(response, 'content'):
                result = response.content.strip()
            else:
                result = str(response).strip()
            if result != "__NO_INFO__":
                try:
                    parsed = json.loads(result)
                except Exception:
                    import re
                    json_match = re.search(r'({.*})', result, re.DOTALL)
                    if json_match:
                        try:
                            parsed = json.loads(json_match.group(1))
                        except Exception:
                            st.warning(f"No se pudo parsear la información extraída como JSON. Se guarda como texto plano. Respuesta LLM: {result}")
                            parsed = {"texto_no_json": result}
                    else:
                        st.warning(f"No se pudo parsear la información extraída como JSON. Se guarda como texto plano. Respuesta LLM: {result}")
                        parsed = {"texto_no_json": result}
                # Guardar SOLO la nueva versión (pisa la anterior)
                st.session_state[key] = [parsed]
                save_user_info_to_disk(user_uuid, [parsed])
                # Guardar en Qdrant con ID único
                from utils import store_user_info_vector, configure_embedding_model
                import uuid, time
                unique_id = str(uuid.uuid4())
                try:
                    store_user_info_vector(unique_id, json.dumps(parsed, ensure_ascii=False), embedding_model=configure_embedding_model())
                except Exception as e:
                    print(f"[DEBUG] Error guardando en Qdrant: {e}")
        except Exception as e:
            print(f"Error extrayendo info de usuario: {e}")
        return


if __name__ == "__main__":
    obj = BasicChatbot()
    obj.main()