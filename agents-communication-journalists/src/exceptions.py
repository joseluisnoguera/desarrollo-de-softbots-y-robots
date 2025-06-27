"""Custom exceptions for the journalists discussion application."""


class AgentError(Exception):
    """Base exception for agent-related errors."""

    pass


class ConfigurationError(AgentError):
    """Exception raised for configuration-related errors."""

    pass


class APIKeyError(AgentError):
    """Exception raised when API key is missing or invalid."""

    pass


class TopicGenerationError(AgentError):
    """Exception raised when topic generation fails."""

    pass


class ConversationError(AgentError):
    """Exception raised during conversation generation."""

    pass
