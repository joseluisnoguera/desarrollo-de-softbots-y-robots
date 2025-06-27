"""Configuration module for the journalists discussion application."""

from typing import Final

# Agent constants
AGENT1_NAME: Final[str] = "Agente 1"
AGENT2_NAME: Final[str] = "Agente 2"
AGENT1_AVATAR: Final[str] = "🧑‍🚀"
AGENT2_AVATAR: Final[str] = "👽"

# Default agent names
DEFAULT_AGENT1_NAME: Final[str] = "Ana Lítica Digital"
DEFAULT_AGENT2_NAME: Final[str] = "Armando Contenidos"

# Model configuration
DEFAULT_MODEL_NAME: Final[str] = "gemini-1.5-flash"
DEFAULT_TEMPERATURE: Final[float] = 0.7

# Available models for selection
AVAILABLE_MODELS: Final[list[str]] = ["gemini-1.5-flash","gemini-2.0-flash","gemini-2.5-flash"]

# Individual agent configurations
DEFAULT_AGENT1_MODEL: Final[str] = DEFAULT_MODEL_NAME
DEFAULT_AGENT1_TEMPERATURE: Final[float] = DEFAULT_TEMPERATURE
DEFAULT_AGENT2_MODEL: Final[str] = DEFAULT_MODEL_NAME
DEFAULT_AGENT2_TEMPERATURE: Final[float] = DEFAULT_TEMPERATURE

# Temperature limits
MIN_TEMPERATURE: Final[float] = 0.0
MAX_TEMPERATURE: Final[float] = 2.0

# UI configuration
MIN_MESSAGE_COUNT: Final[int] = 1
MAX_MESSAGE_COUNT: Final[int] = 10
DEFAULT_MESSAGE_COUNT: Final[int] = 1


# Session state keys
class SessionKeys:
    """Session state keys for consistent access."""

    DISCUSSION_TOPIC = "discussion_topic"
    AGENT1_STANCE = "agent1_stance"
    AGENT2_STANCE = "agent2_stance"
    AGENT1_PERSONALITY = "agent1_personality"
    AGENT2_PERSONALITY = "agent2_personality"
    MESSAGES = "messages"
    AGENT1 = "agent1"
    AGENT2 = "agent2"
    HISTORY = "history"
    MESSAGE_COUNT = "message_count"
    GENERATED_TOPIC = "generated_topic"

    # Agent configuration keys
    AGENT1_MODEL = "agent1_model"
    AGENT1_TEMPERATURE = "agent1_temperature"
    AGENT2_MODEL = "agent2_model"
    AGENT2_TEMPERATURE = "agent2_temperature"
