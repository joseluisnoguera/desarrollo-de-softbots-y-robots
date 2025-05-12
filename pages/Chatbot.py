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

# Mostrar información sobre la configuración actual
# with st.expander("Ver configuración actual del chatbot"):
#     st.write("**Temas permitidos:**", TOPICS_STR)
#     st.write("**Temas bloqueados:**", BLOCKLIST_STR)
#     st.write("Para cambiar esta configuración, ve a la página de Configuración del Chatbot.")

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
            self.web_search_tool.name = "duckduckgo_search"
            self.web_search_tool.description = "Un motor de búsqueda. Útil cuando necesitas responder preguntas sobre eventos actuales, conocimiento general o temas de turismo no cubiertos en los documentos privados. La entrada debe ser una consulta de búsqueda."
            tools.append(self.web_search_tool)

        if not tools:
             st.error("No se pudieron inicializar herramientas (Retriever o Búsqueda Web). El agente no puede funcionar.")
             return None

        # --- Agente ReAct ---
        # Combina las instrucciones originales con la estructura ReAct
        # Asegúrate de que las palabras clave Thought, Action, Action Input, Observation, Final Answer estén en INGLÉS.
        agent_prompt_template = f"""
Eres un asistente virtual de recepción especializado EXCLUSIVAMENTE en {TOPICS_STR}. Te comportarás de manera {BEHAVIOUR_STR}.
Tu única función es proporcionar información y responder preguntas sobre los temas en los cuales estás especializado.
No debes {BLOCKLIST_STR}. Si la pregunta no es relevante, responde con un mensaje claro y útil que explique que no puedes ayudar con eso.

Tienes acceso a las siguientes herramientas:

{{tools}}

Usa el siguiente formato estricto:

Question: la pregunta de entrada que debes responder
Thought: Siempre debes pensar qué hacer. Considera el historial de chat para una continuación de la conversación. Primero, evalúa si la pregunta es sobre los temas exclusivos que puede hablar. Si no lo es, debes declinar la respuesta en el paso de Final Answer. Si es relevante, evalúa si parece requerir información interna específica del negocio (costos, detalles de servicios propios). Si es así, usa la herramienta 'search_private_documents'. Si 'search_private_documents' no proporciona una respuesta suficiente o la pregunta requiere información actualizada, fechas, o lugares particulares, considera usar 'duckduckgo_search'. Solo usa una herramienta por ciclo de Action.
Action: la acción a tomar, debe ser una de [{{tool_names}}]
Action Input: la entrada para la acción
Observation: el resultado de la acción
... (este ciclo Thought/Action/Action Input/Observation puede repetirse N veces si es necesario refinar la búsqueda o usar otra herramienta)
Thought: Ahora sé la respuesta final basada en las Observaciones y el Historial de Chat. De lo contrario, formulo la respuesta final. No antepongas 'AI:' ni ningún prefijo a tus respuestas. Asegúrate de que la respuesta sea clara y útil.
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
        chat_history_str = "\n".join(chat_history[-5:])

        filter_prompt = (
            f"Eres un filtro inteligente para un chatbot recepcionista profesional. "
            f"Evalúa si el mensaje del usuario está relacionado con: {TOPICS_STR}. "
            f"Si NO está relacionado con estos temas, responde únicamente con la palabra '__OUT_OF_SCOPE__'. "
            f"Si el mensaje SÍ está relacionado o tiene alguna conexión con estos temas, "
            f"devuelve el texto original, que NO sea '__OUT_OF_SCOPE__'."
            f"Considera que el mensaje puede estar dentro una conversación más amplia que es relevante. "
            f"historial reciente de la conversación:\n{chat_history_str}\n\n"
        )
        prompt = f"{filter_prompt}\n\nUsuario: {user_query}\nRespuesta:"
        try:
            response = pre_llm.invoke(prompt)
            logger.debug(f"RAW Response: {response}")

            if hasattr(response, 'content'):
                result = response.content.strip()
            else:
                result = str(response).strip()
            logger.info(f"Filter result: '{result}'")

            is_out_of_scope = result == "__OUT_OF_SCOPE__" or "__OUT_OF_SCOPE__" in result

            if is_out_of_scope:
                logger.debug("Message out of context. Generating customized response.")
                response_prompt = (
                    f"Eres un asistente virtual amable especializado en {TOPICS_STR}. "
                    f"Si el usuario te pregunta sobre tus capacidades, puede brindar información sobre los temas que puedes tratar. "
                    f"El usuario ha hecho una pregunta que está fuera de tu ámbito de especialización. "
                    f"Genera una respuesta amable que:\n"
                    f"1. Explique brevemente que no puedes responder a ese tema específico\n"
                    f"2. Mencione los temas sobre los que sí puedes hablar\n"
                    f"3. Ofrezca una o dos sugerencias concretas relacionadas con {TOPICS_STR} para redirigir la conversación\n"
                    f"4. Si es posible, conecta tu respuesta con el contexto de la conversación previa.\n\n"
                    f"Historial reciente de la conversación:\n{chat_history_str}\n\n"
                    f"La pregunta del usuario fue: '{user_query}'"
                )

                try:
                    custom_response = pre_llm.invoke(response_prompt)
                    if hasattr(custom_response, 'content'):
                        custom_message = custom_response.content.strip()
                    else:
                        custom_message = str(custom_response).strip()

                    logger.debug(f"Generated custom response: {custom_message}")
                    return (custom_message, False)
                except Exception as e:
                    logger.error(f"Error generating custom response: {e}")
                    # Fallback al mensaje predeterminado en caso de error
                    return ("Lo siento, solo puedo responder preguntas sobre turismo, lugares turísticos o eventos. ¿Te gustaría saber sobre algún destino, atracción, o evento?", False)

            logger.info("Message in context.")
            return (user_query, True)

        except Exception as e:
            logger.error(f"LLM Filter exception: {e}")
            logger.info("Allowing original message to pass through.")
            return (user_query, True)


    @utils.enable_chat_history
    def main(self):
        agent_runnable = self.setup_chain()

        if not agent_runnable:
             st.warning("El agente no pudo ser inicializado.")
             return

        for msg in st.session_state.get("messages", []):
            st.chat_message(msg["role"]).write(msg["content"])

        user_query = st.chat_input(placeholder="¡Escribe cualquier consulta!")
        if user_query:
            # Mostrar inmediatamente el mensaje del usuario
            st.session_state.messages.append({"role": "user", "content": user_query})
            st.chat_message("user").write(user_query)

            # --- Preprocesamiento con LLM filtro ---
            preprocessed_query, continue_to_agent = self.preprocess_user_query(user_query)
            if not continue_to_agent:
                st.session_state.messages.append({"role": "assistant", "content": preprocessed_query})
                st.chat_message("assistant").write(preprocessed_query)
                utils.print_qa(BasicChatbot, user_query, preprocessed_query)
                return

            # Si es relevante, continuar con el flujo normal
            session_id = st.session_state.get("session_id", "default")

            chat_history = []
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    chat_history.append({"role": "user", "content": msg["content"]})
                elif msg["role"] == "assistant":
                    chat_history.append({"role": "assistant", "content": msg["content"]})

            with st.chat_message("assistant"):
                response_container = st.empty()
                try:
                    response = agent_runnable.invoke(
                        {"input": preprocessed_query, "chat_history": chat_history},
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


if __name__ == "__main__":
    obj = BasicChatbot()
    obj.main()