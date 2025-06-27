"""
Custom exceptions for the supermarket agent application.
"""


class SupermarketAgentError(Exception):
    """Base exception for supermarket agent errors."""
    pass


class MCPConnectionError(SupermarketAgentError):
    """Raised when MCP client connection fails."""
    pass


class ToolExecutionError(SupermarketAgentError):
    """Raised when tool execution fails."""
    pass


class WholesalerAPIError(SupermarketAgentError):
    """Raised when wholesaler API call fails."""
    pass


class AgentInitializationError(SupermarketAgentError):
    """Raised when agent initialization fails."""
    pass
