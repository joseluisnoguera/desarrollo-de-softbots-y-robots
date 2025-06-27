"""
Gemini agent for the supermarket application.
"""
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage
from langchain_mcp_adapters.client import MultiServerMCPClient
import logging

from .models import AgentConfig
from .config import get_mcp_server_path, AGENT_SYSTEM_PROMPT
from .tools import wholesaler_restock
from .exceptions import AgentInitializationError

logger = logging.getLogger(__name__)

class GeminiAgent:
    """Gemini-based agent for supermarket operations."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.tools = []
        self.llm = None
        self.mcp_server_path = get_mcp_server_path()
        self.mcp_client = None

    @classmethod
    def create_default(cls, name: str, personality: str, stance: str = ""):
        """Create agent with default configuration."""
        config = AgentConfig(
            name=name,
            personality=personality,
            stance=stance
        )
        return cls(config)

    async def initialize(self):
        """Initializes the agent's tools and LLM asynchronously."""
        if self.tools:
            return  # Already initialized

        try:
            await self._initialize_mcp_tools()
            self.llm = self._configure_llm()
            logger.info("Agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            raise AgentInitializationError(
                f"Agent initialization failed: {e}"
            ) from e

    async def _initialize_mcp_tools(self):
        """Initialize MCP tools and fallback to wholesaler tool if needed."""
        try:
            logger.info(f"Attempting to connect to MCP server at: {self.mcp_server_path}")

            # Create MCP client for the supermarket API
            self.mcp_client = MultiServerMCPClient({
                "supermarket": {
                    "command": "go",
                    "args": ["run", "./cmd/mcp-server/mcp_server.go"],
                    "cwd": self.mcp_server_path,
                    "transport": "stdio"
                }
            })

            logger.info("MCP client created, attempting to get tools...")
            # Get tools from MCP client (supermarket API)
            mcp_tools = await self.mcp_client.get_tools()
            logger.info(f"Retrieved {len(mcp_tools)} MCP tools")

            # Add our custom wholesaler tool
            self.tools = mcp_tools + [wholesaler_restock]
            logger.info("MCP tools initialized successfully")
        except Exception as e:
            logger.warning(f"MCP client initialization failed: {type(e).__name__}: {e}")
            logger.info("Falling back to wholesaler tool only")
            # Fallback to just the wholesaler tool if MCP fails
            self.tools = [wholesaler_restock]

    def _configure_llm(self):
        """Configure the language model with tools."""
        try:
            llm = ChatGoogleGenerativeAI(
                model=self.config.model_name,
                temperature=self.config.temperature,
                api_key=st.secrets["GOOGLE_API_KEY"]
            )
            return llm.bind_tools(self.tools)
        except Exception as e:
            logger.error(f"Failed to configure LLM: {e}")
            raise AgentInitializationError(
                f"LLM configuration failed: {e}"
            ) from e

    async def generate_response(self, history):
        """Generate response from the agent."""
        if not self.llm:
            raise AgentInitializationError(
                "Agent not initialized. Call initialize() first."
            )

        prompt = AGENT_SYSTEM_PROMPT.format(
            agent_name=self.config.name,
            personality=self.config.personality
        )

        messages = [SystemMessage(content=prompt)]
        messages.extend(history)

        return await self.llm.ainvoke(messages)
