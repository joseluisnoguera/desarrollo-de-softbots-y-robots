"""Conversation page for agent discussions."""

import streamlit as st

from src.config import SessionKeys
from src.conversation_service import ConversationService
from src.exceptions import APIKeyError, ConversationError
from src.ui_components import UIComponents
from src.utils import (
    initialize_session_state,
    setup_logging,
    validate_conversation_requirements,
)

# Setup logging
logger = setup_logging()

# Page configuration
st.set_page_config(page_title="Conversación", page_icon="💬")

# Initialize session state
initialize_session_state()

# Page header
st.markdown("# Conversación")
st.write("Esta página es para iniciar una conversación entre dos agentes de IA.")


def handle_start_conversation() -> None:
    """Handle the start/restart conversation action."""
    is_valid, error_message = validate_conversation_requirements()

    if not is_valid:
        UIComponents.show_validation_error(error_message)
        return

    try:
        # Reset conversation state and mark for regeneration
        ConversationService.reset_conversation()
        st.session_state["_regenerating"] = True
        st.rerun()

    except (ConversationError, APIKeyError) as e:
        UIComponents.show_error(str(e))
    except Exception as e:
        logger.error(f"Unexpected error starting conversation: {e}")
        UIComponents.show_error("Error inesperado al iniciar la conversación.")


def generate_new_conversation() -> None:
    """Generate a new conversation after reset."""
    try:
        # Create agents
        agent1, agent2 = ConversationService.create_agents()
        st.session_state[SessionKeys.AGENT1] = agent1
        st.session_state[SessionKeys.AGENT2] = agent2

        # Generate initial messages with streaming
        history = ConversationService.generate_and_append_messages_streaming(
            agent1=agent1,
            agent2=agent2,
            history="",
            turns=st.session_state[SessionKeys.MESSAGE_COUNT],
            topic=st.session_state[SessionKeys.DISCUSSION_TOPIC],
        )
        st.session_state[SessionKeys.HISTORY] = history

        # Clear regeneration flag
        st.session_state["_regenerating"] = False
        logger.info("Conversation started successfully")

        # Force UI refresh to show sidebar and chat
        st.rerun()

    except Exception as e:
        logger.error(f"Unexpected error starting conversation: {e}")
        UIComponents.show_error("Error inesperado al iniciar la conversación.")
        st.session_state["_regenerating"] = False
        st.rerun()


def handle_continue_conversation() -> None:
    """Handle the continue conversation action."""
    agent1 = st.session_state.get(SessionKeys.AGENT1)
    agent2 = st.session_state.get(SessionKeys.AGENT2)

    if not agent1 or not agent2:
        UIComponents.show_validation_error(
            "Los agentes no se han inicializado. Por favor, inicia una nueva conversación."
        )
        return

    try:
        # Set flag to indicate we're continuing conversation
        st.session_state["_continuing_conversation"] = True
        st.rerun()  # Rerun to update UI immediately

    except (ConversationError, APIKeyError) as e:
        UIComponents.show_error(str(e))
        st.session_state["_continuing_conversation"] = False
    except Exception as e:
        logger.error(f"Unexpected error continuing conversation: {e}")
        UIComponents.show_error("Error inesperado al continuar la conversación.")
        st.session_state["_continuing_conversation"] = False


def continue_conversation_generation() -> None:
    """Generate additional messages for continuing conversation."""
    agent1 = st.session_state.get(SessionKeys.AGENT1)
    agent2 = st.session_state.get(SessionKeys.AGENT2)

    try:
        # Generate additional messages with streaming
        history = ConversationService.generate_and_append_messages_streaming(
            agent1=agent1,
            agent2=agent2,
            history=st.session_state[SessionKeys.HISTORY],
            turns=st.session_state[SessionKeys.MESSAGE_COUNT],
            topic=st.session_state[SessionKeys.DISCUSSION_TOPIC],
        )
        st.session_state[SessionKeys.HISTORY] = history

        # Clear the continuing flag
        st.session_state["_continuing_conversation"] = False

        logger.info("Conversation continued successfully")

        # Force UI refresh to show sidebar and updated chat
        st.rerun()

    except (ConversationError, APIKeyError) as e:
        UIComponents.show_error(str(e))
        st.session_state["_continuing_conversation"] = False
        st.rerun()
    except Exception as e:
        logger.error(f"Unexpected error continuing conversation: {e}")
        UIComponents.show_error("Error inesperado al continuar la conversación.")
        st.session_state["_continuing_conversation"] = False
        st.rerun()


def main() -> None:
    """Main function for the conversation page."""
    # Check if we need to regenerate conversation after reset
    if st.session_state.get("_regenerating", False):
        generate_new_conversation()
        return

    # Check if we need to continue conversation
    if st.session_state.get("_continuing_conversation", False):
        continue_conversation_generation()
        return

    # Render sidebar configuration
    start_conversation = UIComponents.render_sidebar_configuration()

    # Handle start/restart conversation
    if start_conversation:
        handle_start_conversation()
        return  # Exit to prevent rendering old messages

    # Show loading message if continuing conversation
    if st.session_state.get("_continuing_conversation", False):
        st.info("🤖 Los agentes están generando más respuestas...")
        return

    # Render chat messages
    UIComponents.render_chat_messages()

    # Handle continue conversation (pass the continuing state)
    if UIComponents.render_continue_button():
        handle_continue_conversation()


if __name__ == "__main__":
    main()
