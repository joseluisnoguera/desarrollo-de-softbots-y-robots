import streamlit as st
from src.gemini_agent import GeminiAgent

# --- Constantes ---
AGENT1_NAME = "Agente 1"
AGENT2_NAME = "Agente 2"
AGENT1_AVATAR = "🤖"
AGENT2_AVATAR = "👽"

# --- Inicialización del Estado de la Sesión ---
# Usamos setdefault para inicializar las claves solo si no existen.
st.session_state.setdefault("discussion_topic", "")
st.session_state.setdefault("agent1_stance", "")
st.session_state.setdefault("agent2_stance", "")
st.session_state.setdefault("agent1_personality", "")
st.session_state.setdefault("agent2_personality", "")
st.session_state.setdefault("messages", [])
st.session_state.setdefault("agent1", None)
st.session_state.setdefault("agent2", None)
st.session_state.setdefault("history", "")

# --- UI: Título y Descripción ---
st.markdown("# Conversación")
st.write(
    "Esta página es para iniciar una conversación entre dos agentes de IA."
)

# --- UI: Barra Lateral de Configuración ---
with st.sidebar:
    st.header("Configuración")
    st.text_area("Tema de discusión", key="discussion_topic")
    st.slider("Número de turnos por interacción", 1, 10, 1, key="message_count")

    st.header(f"Configuración del {AGENT1_NAME}")
    st.text_input(f"Personalidad del {AGENT1_NAME}", key="agent1_personality")
    st.text_area(f"Postura del {AGENT1_NAME}", key="agent1_stance")

    st.header(f"Configuración del {AGENT2_NAME}")
    st.text_input(f"Personalidad del {AGENT2_NAME}", key="agent2_personality")
    st.text_area(f"Postura del {AGENT2_NAME}", key="agent2_stance")

    start_conversation = st.button("Iniciar/Reiniciar Conversación")

# --- Lógica de la Conversación ---
def generate_and_append_messages(agent1, agent2, history, turns, topic):
    """
    Genera 'turns' de diálogo entre dos agentes, actualiza el historial
    y añade los mensajes al estado de la sesión.
    """
    for _ in range(turns):
        # Turno del Agente 1
        response1 = agent1.generate_response(topic, history)
        st.session_state.messages.append({"role": AGENT1_NAME, "content": response1})
        history += f"{AGENT1_NAME}: {response1}\n"

        # Turno del Agente 2
        response2 = agent2.generate_response(topic, history)
        st.session_state.messages.append({"role": AGENT2_NAME, "content": response2})
        history += f"{AGENT2_NAME}: {response2}\n"
    return history

# --- Manejo de Acciones del Usuario ---
if start_conversation:
    if not st.session_state.discussion_topic:
        st.warning("Por favor, ingresa un tema de discusión.")
    elif not st.session_state.agent1_stance or not st.session_state.agent2_stance:
        st.warning("Ambos agentes necesitan una postura.")
    else:
        # Reiniciar el estado de la conversación
        st.session_state.messages = []
        st.session_state.history = ""
        st.session_state.agent1 = GeminiAgent(
            "Ana Lítica Digital",
            personality=st.session_state.agent1_personality,
            stance=st.session_state.agent1_stance
        )
        st.session_state.agent2 = GeminiAgent(
            "Armando Contenidos",
            personality=st.session_state.agent2_personality,
            stance=st.session_state.agent2_stance
        )
        # Generar los primeros mensajes
        st.session_state.history = generate_and_append_messages(
            st.session_state.agent1,
            st.session_state.agent2,
            st.session_state.history,
            st.session_state.message_count,
            st.session_state.discussion_topic
        )
        st.rerun()

# --- Visualización del Chat ---
for message in st.session_state.messages:
    avatar = AGENT1_AVATAR if message["role"] == AGENT1_NAME else AGENT2_AVATAR
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# El botón para continuar solo aparece si ya hay mensajes en la conversación
if st.session_state.messages and st.button("Continuar Conversación"):
    if st.session_state.agent1 and st.session_state.agent2:
        # Generar y añadir los siguientes mensajes
        st.session_state.history = generate_and_append_messages(
            st.session_state.agent1,
            st.session_state.agent2,
            st.session_state.history,
            st.session_state.message_count,
            st.session_state.discussion_topic
        )
        st.rerun()
    else:
        # Esto no debería ocurrir en el flujo normal, pero es una salvaguarda
        st.warning("Los agentes no se han inicializado. Por favor, inicia una nueva conversación.")
