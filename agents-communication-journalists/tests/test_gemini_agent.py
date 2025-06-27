"""Tests for the Gemini agent module."""

from unittest.mock import Mock, patch

import pytest

from src.exceptions import APIKeyError, ConversationError
from src.gemini_agent import GeminiAgent


class TestGeminiAgent:
    """Test the GeminiAgent class."""

    def test_initialization_default(self):
        """Test agent initialization with defaults."""
        agent = GeminiAgent("TestAgent")

        assert agent.agent_name == "TestAgent"
        assert agent.personality == ""
        assert agent.stance == ""
        assert agent.model_name == "gemini-1.5-flash"
        assert agent.temperature == 0.7

    def test_initialization_custom(self):
        """Test agent initialization with custom values."""
        agent = GeminiAgent(
            agent_name="CustomAgent",
            personality="Friendly",
            stance="Pro-environment",
            model_name="gemini-pro",
            temperature=0.5
        )

        assert agent.agent_name == "CustomAgent"
        assert agent.personality == "Friendly"
        assert agent.stance == "Pro-environment"
        assert agent.model_name == "gemini-pro"
        assert abs(agent.temperature - 0.5) < 0.001

    @patch('src.gemini_agent.get_api_key')
    @patch('src.gemini_agent.ChatGoogleGenerativeAI')
    def test_llm_lazy_initialization(self, mock_chat_llm, mock_get_api_key):
        """Test lazy initialization of LLM."""
        mock_get_api_key.return_value = "fake-api-key"
        mock_llm_instance = Mock()
        mock_chat_llm.return_value = mock_llm_instance

        agent = GeminiAgent("TestAgent")

        # LLM should not be initialized yet
        assert agent._llm is None

        # Access LLM property to trigger initialization
        llm = agent.llm

        assert llm == mock_llm_instance
        mock_get_api_key.assert_called_once()
        mock_chat_llm.assert_called_once()

    @patch('src.gemini_agent.get_api_key')
    def test_configure_llm_missing_api_key(self, mock_get_api_key):
        """Test LLM configuration with missing API key."""
        mock_get_api_key.side_effect = APIKeyError("API key not found")

        agent = GeminiAgent("TestAgent")

        with pytest.raises(APIKeyError):
            _ = agent.llm

    @patch('src.gemini_agent.get_api_key')
    @patch('src.gemini_agent.ChatGoogleGenerativeAI')
    def test_generate_response_success(self, mock_chat_llm, mock_get_api_key):
        """Test successful response generation."""
        mock_get_api_key.return_value = "fake-api-key"
        mock_llm = Mock()
        mock_response = Mock()
        mock_response.content = "Generated response"
        mock_llm.invoke.return_value = mock_response
        mock_chat_llm.return_value = mock_llm

        agent = GeminiAgent("TestAgent", personality="Journalist")
        result = agent.generate_response("Test prompt", "Test history")

        assert "Generated response" in result
        mock_llm.invoke.assert_called_once()

    @patch('src.gemini_agent.get_api_key')
    @patch('src.gemini_agent.ChatGoogleGenerativeAI')
    def test_generate_response_llm_error(self, mock_chat_llm, mock_get_api_key):
        """Test response generation with LLM error."""
        mock_get_api_key.return_value = "fake-api-key"
        mock_llm = Mock()
        mock_llm.invoke.side_effect = Exception("LLM error")
        mock_chat_llm.return_value = mock_llm

        agent = GeminiAgent("TestAgent")

        with pytest.raises(ConversationError):
            agent.generate_response("Test prompt", "Test history")
