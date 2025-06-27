"""UI components for the journalists discussion application."""

import logging

import streamlit as st

from .config import (
    AGENT1_AVATAR,
    AGENT1_NAME,
    AGENT2_AVATAR,
    AVAILABLE_MODELS,
    DEFAULT_AGENT1_NAME,
    DEFAULT_AGENT2_NAME,
    DEFAULT_MESSAGE_COUNT,
    MAX_MESSAGE_COUNT,
    MAX_TEMPERATURE,
    MIN_MESSAGE_COUNT,
    MIN_TEMPERATURE,
    SessionKeys,
)

logger = logging.getLogger(__name__)

# Constants
CONFIG_HELP_MESSAGE = "Esta configuración se aplica en conversaciones nuevas"


class UIComponents:
    """UI components for the application."""

    @staticmethod
    def render_sidebar_configuration() -> bool:
        """Render the sidebar configuration panel.

        Returns:
            bool: True if the start conversation button was clicked.
        """
        from .utils import validate_conversation_requirements

        with st.sidebar:
            st.header("Configuración")

            # General configuration
            st.text_area(
                "Tema de discusión",
                value=st.session_state.get(SessionKeys.DISCUSSION_TOPIC, ""),
                key="sidebar_topic"
            )
            st.slider(
                "Número de turnos por interacción",
                MIN_MESSAGE_COUNT,
                MAX_MESSAGE_COUNT,
                value=st.session_state.get(SessionKeys.MESSAGE_COUNT, DEFAULT_MESSAGE_COUNT),
                key="sidebar_message_count",
            )

            # Agent 1 configuration
            st.header(f"Configuración de {DEFAULT_AGENT1_NAME}")
            st.text_input(
                f"Personalidad de {DEFAULT_AGENT1_NAME}",
                value=st.session_state.get(SessionKeys.AGENT1_PERSONALITY, ""),
                key="sidebar_agent1_personality"
            )
            st.text_area(
                f"Postura de {DEFAULT_AGENT1_NAME}",
                value=st.session_state.get(SessionKeys.AGENT1_STANCE, ""),
                key="sidebar_agent1_stance"
            )

            # Agent 1 model configuration
            st.selectbox(
                "Modelo",
                options=AVAILABLE_MODELS,
                index=AVAILABLE_MODELS.index(st.session_state.get(SessionKeys.AGENT1_MODEL, AVAILABLE_MODELS[0])),
                key="sidebar_agent1_model",
                help=CONFIG_HELP_MESSAGE
            )
            st.slider(
                "Temperatura",
                MIN_TEMPERATURE,
                MAX_TEMPERATURE,
                value=st.session_state.get(SessionKeys.AGENT1_TEMPERATURE, 0.7),
                key="sidebar_agent1_temperature",
                step=0.1,
                help=CONFIG_HELP_MESSAGE
            )

            # Agent 2 configuration
            st.header(f"Configuración de {DEFAULT_AGENT2_NAME}")
            st.text_input(
                f"Personalidad de {DEFAULT_AGENT2_NAME}",
                value=st.session_state.get(SessionKeys.AGENT2_PERSONALITY, ""),
                key="sidebar_agent2_personality"
            )
            st.text_area(
                f"Postura de {DEFAULT_AGENT2_NAME}",
                value=st.session_state.get(SessionKeys.AGENT2_STANCE, ""),
                key="sidebar_agent2_stance"
            )

            # Agent 2 model configuration
            st.selectbox(
                "Modelo",
                options=AVAILABLE_MODELS,
                index=AVAILABLE_MODELS.index(st.session_state.get(SessionKeys.AGENT2_MODEL, AVAILABLE_MODELS[0])),
                key="sidebar_agent2_model",
                help=CONFIG_HELP_MESSAGE
            )
            st.slider(
                "Temperatura",
                MIN_TEMPERATURE,
                MAX_TEMPERATURE,
                value=st.session_state.get(SessionKeys.AGENT2_TEMPERATURE, 0.7),
                key="sidebar_agent2_temperature",
                step=0.1,
                help=CONFIG_HELP_MESSAGE
            )

            # Save configuration button
            if st.button("Guardar Configuración"):
                UIComponents._save_sidebar_configuration()

            # Validate requirements for conversation button
            is_valid, error_message = validate_conversation_requirements()

            # Show validation message if fields are missing
            if not is_valid:
                st.warning(f"⚠️ {error_message}")

            # Render button with conditional enabling
            return st.button(
                "Iniciar/Reiniciar Conversación",
                disabled=not is_valid,
                help="Complete todos los campos requeridos para habilitar" if not is_valid else None
            )

    @staticmethod
    def render_chat_messages() -> None:
        """Render all chat messages with differentiated alignment."""
        # Inject custom CSS for chat styling
        UIComponents._inject_chat_styles()

        messages = st.session_state.get(SessionKeys.MESSAGES, [])

        for message in messages:
            role = message.get("role", "")
            content = message.get("content", "")
            avatar = AGENT1_AVATAR if role == AGENT1_NAME else AGENT2_AVATAR

            # Use default names for display but keep internal logic with original names
            display_name = DEFAULT_AGENT1_NAME if role == AGENT1_NAME else DEFAULT_AGENT2_NAME

            # Determine alignment based on agent
            is_agent1 = role == AGENT1_NAME
            UIComponents._render_aligned_message(content, avatar, display_name, is_agent1)

    @staticmethod
    def _inject_chat_styles() -> None:
        """Inject custom CSS styles for chat message alignment."""
        st.markdown("""
        <style>
        .chat-container {
            display: flex;
            flex-direction: column;
            gap: 15px;
            margin: 10px 0;
        }

        .message-left {
            display: flex;
            justify-content: flex-start;
            align-items: flex-start;
            margin-bottom: 15px;
            width: 100%;
        }

        .message-right {
            display: flex;
            justify-content: flex-end;
            align-items: flex-start;
            margin-bottom: 15px;
            width: 100%;
        }

        .message-bubble {
            max-width: 75%;
            padding: 12px 16px;
            border-radius: 18px;
            word-wrap: break-word;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            color: white !important;
            font-weight: 500;
        }

        .bubble-left {
            background-color: #0e6590 !important;
            border-bottom-left-radius: 4px;
        }

        .bubble-right {
            background-color: #007c3c !important;
            border-bottom-right-radius: 4px;
        }

        .avatar {
            width: 40px;
            height: 40px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            flex-shrink: 0;
            background-color: #f0f0f0;
            border: 2px solid #ddd;
            margin-top: 0px;
        }

        .avatar-left {
            background-color: #e8f4f8;
            border: 2px solid #0e6590;
            margin-right: 0.5rem;
        }

        .avatar-right {
            background-color: #e8f5e8;
            border: 2px solid #007c3c;
            margin-left: 0.5rem;
        }

        .agent-name {
            font-size: 12px;
            font-weight: bold;
            color: #ffffff !important;
            margin-bottom: 4px;
            text-align: left;
        }

        .agent-name-right {
            text-align: right;
        }

        .message-content {
            margin: 0;
            line-height: 1.4;
            color: white !important;
        }

        .message-wrapper {
            display: flex;
            flex-direction: column;
            max-width: 75%;
            align-items: flex-start;
        }

        .message-wrapper-right {
            align-items: flex-end;
            max-width: 75%;
        }

        /* Loader animation styles */
        @keyframes bounce {
            0%, 80%, 100% { transform: scale(0); }
            40% { transform: scale(1); }
        }

        .loader-container {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 4px;
            padding: 8px 0;
        }

        .loader-dot {
            width: 8px;
            height: 8px;
            background-color: white;
            border-radius: 50%;
            animation: bounce 1.4s infinite ease-in-out;
        }

        .loader-dot:nth-child(1) { animation-delay: -0.32s; }
        .loader-dot:nth-child(2) { animation-delay: -0.16s; }
        .loader-dot:nth-child(3) { animation-delay: 0s; }

        @media (max-width: 768px) {
            .message-bubble {
                max-width: 85%;
            }
            .message-wrapper {
                max-width: 85%;
            }
            .message-wrapper-right {
                max-width: 85%;
            }
        }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def _render_aligned_message(content: str, avatar: str, role: str, is_agent1: bool) -> None:
        """Render a single message with proper alignment and WhatsApp-style layout.

        Args:
            content: Message content.
            avatar: Avatar emoji.
            role: Agent role/name.
            is_agent1: True if this is Agent 1 (left alignment).
        """
        alignment_class = "message-left" if is_agent1 else "message-right"
        bubble_class = "bubble-left" if is_agent1 else "bubble-right"
        avatar_class = "avatar-left" if is_agent1 else "avatar-right"
        wrapper_class = "message-wrapper" if is_agent1 else "message-wrapper message-wrapper-right"
        name_class = "agent-name" if is_agent1 else "agent-name agent-name-right"

        # Clean content for HTML safety
        safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_content = safe_content.replace("\n", "<br>")

        if is_agent1:
            # Agent 1: Avatar on left, message content on right with 0.5rem spacing
            message_html = f"""
            <div class="{alignment_class}">
                <div class="avatar {avatar_class}">
                    {avatar}
                </div>
                <div class="{wrapper_class}">
                    <div class="{name_class}">{role}</div>
                    <div class="message-bubble {bubble_class}">
                        <div class="message-content">{safe_content}</div>
                    </div>
                </div>
            </div>
            """
        else:
            # Agent 2: Message content on right, avatar on right (fully right-aligned)
            message_html = f"""
            <div class="{alignment_class}">
                <div class="{wrapper_class}">
                    <div class="{name_class}">{role}</div>
                    <div class="message-bubble {bubble_class}">
                        <div class="message-content">{safe_content}</div>
                    </div>
                </div>
                <div class="avatar {avatar_class}">
                    {avatar}
                </div>
            </div>
            """

        st.markdown(message_html, unsafe_allow_html=True)

    @staticmethod
    def render_loader_bubble(avatar: str, role: str, is_agent1: bool) -> None:
        """Render a loader bubble for an agent that is currently processing.

        Args:
            avatar: Avatar emoji.
            role: Agent role/name.
            is_agent1: True if this is Agent 1 (left alignment).
        """
        alignment_class = "message-left" if is_agent1 else "message-right"
        bubble_class = "bubble-left" if is_agent1 else "bubble-right"
        avatar_class = "avatar-left" if is_agent1 else "avatar-right"
        wrapper_class = "message-wrapper" + ("" if is_agent1 else " message-wrapper-right")
        name_class = "agent-name" + ("" if is_agent1 else " agent-name-right")

        # Loader HTML with simplified animation using CSS classes
        loader_content = """
        <div class="loader-container">
            <div class="loader-dot"></div>
            <div class="loader-dot"></div>
            <div class="loader-dot"></div>
        </div>
        """

        if is_agent1:
            # Agent 1: Avatar on left, loader on right
            message_html = f"""
            <div class="{alignment_class}">
                <div class="avatar {avatar_class}">
                    {avatar}
                </div>
                <div class="{wrapper_class}">
                    <div class="{name_class}">{role}</div>
                    <div class="message-bubble {bubble_class}">
                        {loader_content}
                    </div>
                </div>
            </div>
            """
        else:
            # Agent 2: Loader on left, avatar on right
            message_html = f"""
            <div class="{alignment_class}">
                <div class="{wrapper_class}">
                    <div class="{name_class}">{role}</div>
                    <div class="message-bubble {bubble_class}">
                        {loader_content}
                    </div>
                </div>
                <div class="avatar {avatar_class}">
                    {avatar}
                </div>
            </div>
            """

        st.markdown(message_html, unsafe_allow_html=True)

    @staticmethod
    def render_streaming_message(content: str, avatar: str, role: str, is_agent1: bool, placeholder_key: str) -> None:
        """Render a streaming message that updates in real-time.

        Args:
            content: Current message content.
            avatar: Avatar emoji.
            role: Agent role/name.
            is_agent1: True if this is Agent 1 (left alignment).
            placeholder_key: Unique key for the placeholder.
        """
        alignment_class = "message-left" if is_agent1 else "message-right"
        bubble_class = "bubble-left" if is_agent1 else "bubble-right"
        avatar_class = "avatar-left" if is_agent1 else "avatar-right"
        wrapper_class = "message-wrapper" + ("" if is_agent1 else " message-wrapper-right")
        name_class = "agent-name" + ("" if is_agent1 else " agent-name-right")

        # Clean content for HTML safety
        safe_content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        safe_content = safe_content.replace("\n", "<br>")

        if is_agent1:
            # Agent 1: Avatar on left, message content on right
            message_html = f"""
            <div class="{alignment_class}">
                <div class="avatar {avatar_class}">
                    {avatar}
                </div>
                <div class="{wrapper_class}">
                    <div class="{name_class}">{role}</div>
                    <div class="message-bubble {bubble_class}">
                        <div class="message-content">{safe_content}</div>
                    </div>
                </div>
            </div>
            """
        else:
            # Agent 2: Message content on left, avatar on right
            message_html = f"""
            <div class="{alignment_class}">
                <div class="{wrapper_class}">
                    <div class="{name_class}">{role}</div>
                    <div class="message-bubble {bubble_class}">
                        <div class="message-content">{safe_content}</div>
                    </div>
                </div>
                <div class="avatar {avatar_class}">
                    {avatar}
                </div>
            </div>
            """

        # Use session state to store placeholder for updates
        if placeholder_key not in st.session_state:
            st.session_state[placeholder_key] = st.empty()

        st.session_state[placeholder_key].markdown(message_html, unsafe_allow_html=True)

    @staticmethod
    def render_continue_button() -> bool:
        """Render the continue conversation button centered.

        Returns:
            bool: True if the continue button was clicked.
        """
        messages = st.session_state.get(SessionKeys.MESSAGES, [])

        if messages:
            # Use columns to center the button
            _, col2, _ = st.columns([1, 2, 1])
            with col2:
                return st.button("Continuar Conversación", use_container_width=True)
        return False

    @staticmethod
    def show_validation_error(error_message: str) -> None:
        """Show a validation error message.

        Args:
            error_message: The error message to display.
        """
        st.warning(error_message)
        logger.warning(f"Validation error: {error_message}")

    @staticmethod
    def show_error(error_message: str) -> None:
        """Show an error message.

        Args:
            error_message: The error message to display.
        """
        st.error(error_message)
        logger.error(f"Application error: {error_message}")

    @staticmethod
    def show_success(message: str) -> None:
        """Show a success message.

        Args:
            message: The success message to display.
        """
        st.success(message)
        logger.info(f"Success: {message}")

    @staticmethod
    def _save_sidebar_configuration() -> None:
        """Save current sidebar field values to persistent session state.

        This ensures that values edited in the sidebar are preserved
        when navigating between pages.
        """
        # Save current field values to persistent session state
        st.session_state[SessionKeys.DISCUSSION_TOPIC] = st.session_state.get("sidebar_topic", "")
        st.session_state[SessionKeys.MESSAGE_COUNT] = st.session_state.get("sidebar_message_count", DEFAULT_MESSAGE_COUNT)
        st.session_state[SessionKeys.AGENT1_PERSONALITY] = st.session_state.get("sidebar_agent1_personality", "")
        st.session_state[SessionKeys.AGENT1_STANCE] = st.session_state.get("sidebar_agent1_stance", "")
        st.session_state[SessionKeys.AGENT1_MODEL] = st.session_state.get("sidebar_agent1_model", "")
        st.session_state[SessionKeys.AGENT1_TEMPERATURE] = st.session_state.get("sidebar_agent1_temperature", 0.7)
        st.session_state[SessionKeys.AGENT2_PERSONALITY] = st.session_state.get("sidebar_agent2_personality", "")
        st.session_state[SessionKeys.AGENT2_STANCE] = st.session_state.get("sidebar_agent2_stance", "")
        st.session_state[SessionKeys.AGENT2_MODEL] = st.session_state.get("sidebar_agent2_model", "")
        st.session_state[SessionKeys.AGENT2_TEMPERATURE] = st.session_state.get("sidebar_agent2_temperature", 0.7)

        UIComponents.show_success("¡Configuración guardada exitosamente!")
        logger.info("Sidebar configuration saved to session state")


class TopicUIComponents:
    """UI components for the topic generation page."""

    @staticmethod
    def render_topic_input() -> tuple[str, bool]:
        """Render the topic input field and generate button.

        Supports both button click and Enter key for better UX.
        Only triggers generation when there's text input.

        Returns:
            tuple: (topic, generate_clicked)
        """
        with st.form("topic_form", clear_on_submit=False):
            topic = st.text_input("Ingresa un tema para discusión")
            generate_clicked = st.form_submit_button("Generar Tema")

            # Only trigger if there's actual text content
            if generate_clicked and not topic.strip():
                generate_clicked = False

        return topic, generate_clicked

    @staticmethod
    def render_generated_topic(result: dict) -> bool:
        """Render the generated topic and stances.

        Fields are editable and values are always updated with new generated content.
        The save button will use current field values (edited or original).

        Args:
            result: Dictionary containing improved_topic, stance1, stance2.

        Returns:
            bool: True if save button was clicked.
        """
        # Always update editable fields with newly generated values
        st.session_state["editable_topic"] = result["improved_topic"]
        st.session_state["editable_stance1"] = result["stance1"]
        st.session_state["editable_stance2"] = result["stance2"]

        # Render editable fields
        st.text_area(
            "Tema Mejorado",
            key="editable_topic",
            height=100
        )

        col1, col2 = st.columns(2)
        with col1:
            st.text_area(
                f"Postura de {DEFAULT_AGENT1_NAME}",
                key="editable_stance1",
                height=200
            )
        with col2:
            st.text_area(
                f"Postura de {DEFAULT_AGENT2_NAME}",
                key="editable_stance2",
                height=200
            )

        return st.button("Guardar para Conversación")

    @staticmethod
    def save_topic_to_conversation(result: dict) -> None:
        """Save the current topic and stances to conversation state.

        Reads from editable fields (which may have been modified by user)
        rather than original generated values.

        Args:
            result: Dictionary containing original generated values (unused, kept for compatibility).
        """
        # Read current values from editable fields
        current_topic = st.session_state.get("editable_topic", "")
        current_stance1 = st.session_state.get("editable_stance1", "")
        current_stance2 = st.session_state.get("editable_stance2", "")

        # Save to conversation configuration
        st.session_state[SessionKeys.DISCUSSION_TOPIC] = current_topic
        st.session_state[SessionKeys.AGENT1_STANCE] = current_stance1
        st.session_state[SessionKeys.AGENT2_STANCE] = current_stance2

        UIComponents.show_success("¡Tema y posturas guardados para la conversación!")
        logger.info("Topic and stances saved to conversation state")
