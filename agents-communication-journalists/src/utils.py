"""Utility functions for the journalists discussion application."""

import logging

import streamlit as st

from .config import SessionKeys
from .exceptions import APIKeyError


def setup_logging() -> logging.Logger:
    """Set up logging configuration."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    return logging.getLogger(__name__)


def get_api_key() -> str:
    """Get Google API key from Streamlit secrets.

    Returns:
        str: The API key.

    Raises:
        APIKeyError: If the API key is not found.
    """
    try:
        return st.secrets["GOOGLE_API_KEY"]
    except KeyError as e:
        raise APIKeyError(
            "Google API key not found in secrets. "
            "Please add GOOGLE_API_KEY to your .streamlit/secrets.toml file."
        ) from e


def initialize_session_state() -> None:
    """Initialize Streamlit session state with default values."""
    from .config import (
        DEFAULT_AGENT1_MODEL,
        DEFAULT_AGENT1_TEMPERATURE,
        DEFAULT_AGENT2_MODEL,
        DEFAULT_AGENT2_TEMPERATURE,
        DEFAULT_MESSAGE_COUNT,
    )

    default_values = {
        SessionKeys.DISCUSSION_TOPIC: "",
        SessionKeys.AGENT1_STANCE: "",
        SessionKeys.AGENT2_STANCE: "",
        SessionKeys.AGENT1_PERSONALITY: "",
        SessionKeys.AGENT2_PERSONALITY: "",
        SessionKeys.MESSAGES: [],
        SessionKeys.AGENT1: None,
        SessionKeys.AGENT2: None,
        SessionKeys.HISTORY: "",
        SessionKeys.MESSAGE_COUNT: DEFAULT_MESSAGE_COUNT,
        SessionKeys.AGENT1_MODEL: DEFAULT_AGENT1_MODEL,
        SessionKeys.AGENT1_TEMPERATURE: DEFAULT_AGENT1_TEMPERATURE,
        SessionKeys.AGENT2_MODEL: DEFAULT_AGENT2_MODEL,
        SessionKeys.AGENT2_TEMPERATURE: DEFAULT_AGENT2_TEMPERATURE,
    }

    for key, value in default_values.items():
        st.session_state.setdefault(key, value)


def validate_conversation_requirements() -> tuple[bool, str | None]:
    """Validate that all requirements for starting a conversation are met.

    Returns:
        tuple: (is_valid, error_message)
    """
    missing_fields = []

    # Check discussion topic
    topic = st.session_state.get(SessionKeys.DISCUSSION_TOPIC, "").strip()
    if not topic:
        missing_fields.append("Tema de discusión")

    # Check agent stances
    stance1 = st.session_state.get(SessionKeys.AGENT1_STANCE, "").strip()
    if not stance1:
        missing_fields.append("Postura del Agente 1")

    stance2 = st.session_state.get(SessionKeys.AGENT2_STANCE, "").strip()
    if not stance2:
        missing_fields.append("Postura del Agente 2")

    if missing_fields:
        if len(missing_fields) == 1:
            error_message = f"Falta completar: {missing_fields[0]}"
        elif len(missing_fields) == 2:
            error_message = f"Faltan completar: {missing_fields[0]} y {missing_fields[1]}"
        else:
            error_message = f"Faltan completar: {', '.join(missing_fields[:-1])} y {missing_fields[-1]}"
        return False, error_message

    return True, None


def clear_conversation_state() -> None:
    """Clear conversation-related session state."""
    st.session_state[SessionKeys.MESSAGES] = []
    st.session_state[SessionKeys.HISTORY] = ""
    st.session_state[SessionKeys.AGENT1] = None
    st.session_state[SessionKeys.AGENT2] = None
