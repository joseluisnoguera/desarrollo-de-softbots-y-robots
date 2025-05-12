import utils
import streamlit as st

from langchain.agents import AgentExecutor, create_react_agent
from langchain.tools.retriever import create_retriever_tool
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain.schema import format_document


st.set_page_config(page_title="Chatbot", page_icon="💬")
st.header('Chatbot Recepcionista')

TOPICS_STR = "turismo, lugares turísticos, eventos turísticos, direcciones para llegar a lugares turísticos, comercios que utilizarían turistas, atracciones, viajes, temas relacionados con turismo"
BLOCKLIST_STR = "tomar posiciones políticas, religión, temas sensibles, temas no relacionados a los estipulados anteriomente."

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
        agent_prompt_template = """
Eres un asistente virtual de recepción especializado EXCLUSIVAMENTE en {TOPICS_STR}.
Tu única función es proporcionar información y responder preguntas sobre los temas en los cuales estás especializado.
No debes {BLOCKLIST_STR}. Si la pregunta no es relevante, responde con un mensaje claro y útil que explique que no puedes ayudar con eso.

Tienes acceso a las siguientes herramientas:

{tools}

Usa el siguiente formato estricto:

Question: la pregunta de entrada que debes responder
Thought: Siempre debes pensar qué hacer. Considera el historial de chat. Primero, evalúa si la pregunta es sobre turismo, lugares que visitarían turístas o eventos turísticos. Si no lo es, debes declinar la respuesta en el paso de Final Answer. Si es sobre turismo, evalúa si parece requerir información interna específica del negocio (costos, detalles de servicios propios). Si es así, usa la herramienta 'search_private_documents'. Si 'search_private_documents' no proporciona una respuesta suficiente o la pregunta es sobre conocimiento general de turismo, direcciones para llegar a lugares turísticos, eventos actuales relacionados con viajes, o información no específica del negocio, considera usar 'duckduckgo_search'. Solo usa una herramienta por ciclo de Action.
Action: la acción a tomar, debe ser una de [{tool_names}]
Action Input: la entrada para la acción
Observation: el resultado de la acción
... (este ciclo Thought/Action/Action Input/Observation puede repetirse N veces si es necesario refinar la búsqueda o usar otra herramienta)
Thought: Ahora sé la respuesta final basada en las Observaciones y el Historial de Chat. De lo contrario, formulo la respuesta final. No antepongas 'AI:' ni ningún prefijo a tus respuestas. Asegúrate de que la respuesta sea clara y útil.
Final Answer: la respuesta final a la pregunta original del usuario. Si declinas responder, explícalo aquí.

¡Comienza ahora!

Historial de Chat Previo:
{chat_history}

New Question: {input}
{agent_scratchpad}
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
        logger = utils.logger  # Usa el logger configurado en utils.py
        pre_llm = utils.configure_llm()
        system_prompt = f"""
            Eres un filtro inteligente para un chatbot recepcionista profesional.
            Si el mensaje del usuario NO es sobre {TOPICS_STR}, devuelve SOLO este texto: '__OUT_OF_SCOPE__'.
            Si el mensaje es relevante pero ambiguo, ajústalo para que sea claro y enfocado en los temas válidos, o el original.
        """
        prompt = f"{system_prompt}\n\nUsuario: {user_query}\nRespuesta:"
        logger.debug(f"Preprocess prompt enviado al LLM:\n{prompt}")
        try:
            response = pre_llm.invoke(prompt)
            logger.debug(f"Respuesta cruda del LLM filtro: {response}")
            if hasattr(response, 'content'):
                result = response.content.strip()
            else:
                result = str(response).strip()
            logger.debug(f"Resultado procesado del filtro: {result}")
        except Exception as e:
            logger.error(f"Excepción en filtro LLM: {e}")
            return ("__OUT_OF_SCOPE__", False)
        if result == "__OUT_OF_SCOPE__":
            logger.info("Mensaje fuera de contexto detectado por filtro.")
            return ("Lo siento, solo puedo responder preguntas sobre turismo, lugares turísticos o eventos. ¿Te gustaría saber sobre algún destino, atracción, o evento?", False)
        logger.info("Mensaje considerado relevante por filtro.")
        return (result, True)

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
            # --- Preprocesamiento con LLM filtro ---
            preprocessed_query, continue_to_agent = self.preprocess_user_query(user_query)
            if not continue_to_agent:
                st.session_state.messages.append({"role": "user", "content": user_query})
                st.chat_message("user").write(user_query)
                st.session_state.messages.append({"role": "assistant", "content": preprocessed_query})
                st.chat_message("assistant").write(preprocessed_query)
                utils.print_qa(BasicChatbot, user_query, preprocessed_query)
                return
            # Si es relevante, continuar con el flujo normal
            st.session_state.messages.append({"role": "user", "content": preprocessed_query})
            st.chat_message("user").write(preprocessed_query)
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