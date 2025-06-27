"""
Chat page for the supermarket agent application.
"""
import streamlit as st
import nest_asyncio

from src.gemini_agent import GeminiAgent
from src.chat_service import ChatService
from src.ui_components import ChatUI
from src.utils import setup_event_loop, run_async, initialize_session_state
from src.config import DEFAULT_AGENT_NAME, DEFAULT_AGENT_AVATAR, DEFAULT_PERSONALITY

# Apply nest_asyncio to allow nested event loops, which is crucial for
# gRPC/asyncio compatibility.
nest_asyncio.apply()

# Initialize session state and event loop
setup_event_loop()
initialize_session_state()

# --- Agent Initialization ---
if "agent" not in st.session_state:
    with st.spinner("Iniciando el agente y conectando con las herramientas..."):
        agent = GeminiAgent.create_default(
            DEFAULT_AGENT_NAME,
            DEFAULT_PERSONALITY
        )
        # Run the async initialization
        run_async(agent.initialize())
        st.session_state.agent = agent
        st.session_state.chat_service = ChatService(agent)
        # Rerun to clear the spinner and show the chat interface
        st.rerun()

# Initialize UI components
chat_ui = ChatUI(DEFAULT_AGENT_NAME, DEFAULT_AGENT_AVATAR)

# Render the chat interface
chat_ui.render_header()
chat_ui.render_chat_history()

# Handle user input
if prompt := chat_ui.get_user_input():
    with st.spinner("El agente está pensando..."):
        run_async(st.session_state.chat_service.get_agent_response())
        st.rerun()
