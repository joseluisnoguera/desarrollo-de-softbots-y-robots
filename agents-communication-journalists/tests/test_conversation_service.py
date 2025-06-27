"""Tests for the conversation service module."""

from unittest.mock import Mock, patch

import pytest

from src.conversation_service import ConversationService
from src.exceptions import ConversationError


class TestConversationService:
    """Test the ConversationService class."""

    @patch('src.conversation_service.st')
    def test_generate_and_append_messages_success(self, mock_st):
        """Test successful message generation."""
        # Setup mocks
        mock_agent1 = Mock()
        mock_agent1.generate_response.return_value = "Response from agent 1"
        mock_agent2 = Mock()
        mock_agent2.generate_response.return_value = "Response from agent 2"

        # Mock session state
        mock_st.session_state = {"messages": []}

        # Test the method
        result = ConversationService.generate_and_append_messages(
            mock_agent1, mock_agent2, "Initial history", 2, "Test topic"
        )

        # Verify responses were generated
        mock_agent1.generate_response.assert_called()
        mock_agent2.generate_response.assert_called()

        # Check that history was updated
        assert "Response from agent 1" in result
        assert "Response from agent 2" in result

    @patch('src.conversation_service.st')
    def test_generate_and_append_messages_agent1_error(self, mock_st):
        """Test error handling when agent1 fails."""
        mock_agent1 = Mock()
        mock_agent1.generate_response.side_effect = Exception("Agent1 error")
        mock_agent2 = Mock()

        mock_st.session_state = {"messages": []}

        with pytest.raises(ConversationError, match="Failed to generate conversation"):
            ConversationService.generate_and_append_messages(
                mock_agent1, mock_agent2, "", 1, "Test topic"
            )

    @patch('src.conversation_service.st')
    def test_generate_and_append_messages_agent2_error(self, mock_st):
        """Test error handling when agent2 fails."""
        mock_agent1 = Mock()
        mock_agent1.generate_response.return_value = "Response from agent 1"
        mock_agent2 = Mock()
        mock_agent2.generate_response.side_effect = Exception("Agent2 error")

        mock_st.session_state = {"messages": []}

        with pytest.raises(ConversationError, match="Failed to generate conversation"):
            ConversationService.generate_and_append_messages(
                mock_agent1, mock_agent2, "", 1, "Test topic"
            )

    @patch('src.conversation_service.st')
    @patch('src.conversation_service.GeminiAgent')
    def test_create_agents_success(self, mock_gemini_agent, mock_st):
        """Test successful agent creation."""
        # Mock session state with mock object that has get method
        mock_session_state = Mock()
        mock_session_state.get.return_value = ""
        mock_st.session_state = mock_session_state

        # Mock agent instances
        mock_agent1 = Mock()
        mock_agent2 = Mock()
        mock_gemini_agent.side_effect = [mock_agent1, mock_agent2]

        # Test the method
        agent1, agent2 = ConversationService.create_agents()

        assert agent1 == mock_agent1
        assert agent2 == mock_agent2
        assert mock_gemini_agent.call_count == 2

    @patch('src.conversation_service.st')
    @patch('src.conversation_service.GeminiAgent')
    def test_create_agents_error(self, mock_gemini_agent, mock_st):
        """Test error handling during agent creation."""
        mock_session_state = Mock()
        mock_session_state.get.return_value = ""
        mock_st.session_state = mock_session_state
        mock_gemini_agent.side_effect = Exception("Agent creation failed")

        with pytest.raises(ConversationError, match="Failed to create agents"):
            ConversationService.create_agents()

    @patch('src.conversation_service.st')
    def test_reset_conversation(self, mock_st):
        """Test conversation reset functionality."""
        # Mock session state
        mock_st.session_state = {
            "messages": [{"role": "test", "content": "test"}],
            "history": "Some history",
            "agent1": Mock(),
            "agent2": Mock()
        }

        ConversationService.reset_conversation()

        # Verify session state was reset
        assert mock_st.session_state["messages"] == []
        assert mock_st.session_state["history"] == ""
        assert mock_st.session_state["agent1"] is None
        assert mock_st.session_state["agent2"] is None

    @patch('src.conversation_service.st')
    def test_generate_multiple_turns(self, mock_st):
        """Test generating multiple conversation turns."""
        mock_agent1 = Mock()
        mock_agent1.generate_response.side_effect = ["Response 1A", "Response 2A"]
        mock_agent2 = Mock()
        mock_agent2.generate_response.side_effect = ["Response 1B", "Response 2B"]

        mock_st.session_state = {"messages": []}

        result = ConversationService.generate_and_append_messages(
            mock_agent1, mock_agent2, "", 2, "Test topic"
        )

        # Verify all responses are in history
        assert "Response 1A" in result
        assert "Response 1B" in result
        assert "Response 2A" in result
        assert "Response 2B" in result

        # Verify correct number of calls
        assert mock_agent1.generate_response.call_count == 2
        assert mock_agent2.generate_response.call_count == 2
