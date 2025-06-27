"""Topics page for generating discussion topics and stances."""

import streamlit as st

from src.config import SessionKeys
from src.exceptions import APIKeyError, TopicGenerationError
from src.gemini_agent import GeminiTopicAgent
from src.ui_components import TopicUIComponents, UIComponents
from src.utils import setup_logging

# Setup logging
logger = setup_logging()

# Page configuration
st.set_page_config(page_title="Topics", page_icon="📝")

# Page header
st.markdown("# Temas")
st.sidebar.header("Temas")

st.write(
    """
    Esta página te permite generar un tema de discusión y ver dos posturas diferentes sobre él.
    """
)


def handle_topic_generation(topic: str) -> None:
    """Handle topic generation request.

    Args:
        topic: The input topic string.
    """
    if not topic.strip():
        UIComponents.show_validation_error("Por favor, ingresa un tema.")
        return

    try:
        agent = GeminiTopicAgent()
        result = agent.generate_topic_and_stances(topic)
        st.session_state[SessionKeys.GENERATED_TOPIC] = result
        logger.info(f"Successfully generated topic for: {topic}")

    except (TopicGenerationError, APIKeyError) as e:
        UIComponents.show_error(str(e))
    except Exception as e:
        logger.error(f"Unexpected error generating topic: {e}")
        UIComponents.show_error("Error inesperado al generar el tema.")


def main() -> None:
    """Main function for the topics page."""
    # Render topic input
    topic, generate_clicked = TopicUIComponents.render_topic_input()

    # Handle topic generation
    if generate_clicked:
        handle_topic_generation(topic)

    # Render generated topic if available
    generated_topic = st.session_state.get(SessionKeys.GENERATED_TOPIC)
    if generated_topic:
        save_clicked = TopicUIComponents.render_generated_topic(generated_topic)

        if save_clicked:
            TopicUIComponents.save_topic_to_conversation(generated_topic)


if __name__ == "__main__":
    main()
