"""
Custom exceptions for the wholesaler agent.
"""


class AgentInitializationError(Exception):
    """Raised when agent initialization fails."""
    pass


class WholesalerAgentError(Exception):
    """Raised when wholesaler agent operations fail."""
    pass
