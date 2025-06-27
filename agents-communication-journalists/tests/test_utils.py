"""Tests for utility functions."""

from unittest.mock import patch

import pytest

from src.config import SessionKeys
from src.exceptions import APIKeyError
from src.utils import (
    get_api_key,
    initialize_session_state,
    validate_conversation_requirements,
)


class TestGetApiKey:
    """Tests for get_api_key function."""

    def test_get_api_key_success(self, mock_streamlit):
        """Test successful API key retrieval."""
        result = get_api_key()
        assert result == "fake_api_key"

    def test_get_api_key_missing(self):
        """Test API key missing raises exception."""
        with patch("streamlit.secrets") as mock_secrets:
            mock_secrets.__getitem__.side_effect = KeyError
            with pytest.raises(APIKeyError):
                get_api_key()


class TestValidateConversationRequirements:
    """Tests for validate_conversation_requirements function."""

    def test_validate_success(self):
        """Test successful validation."""
        with patch(
            "streamlit.session_state",
            {
                SessionKeys.DISCUSSION_TOPIC: "Test topic",
                SessionKeys.AGENT1_STANCE: "Stance 1",
                SessionKeys.AGENT2_STANCE: "Stance 2",
            },
        ):
            is_valid, error = validate_conversation_requirements()
            assert is_valid is True
            assert error is None

    def test_validate_missing_topic(self):
        """Test validation fails with missing topic."""
        with patch(
            "streamlit.session_state",
            {
                SessionKeys.DISCUSSION_TOPIC: "",
                SessionKeys.AGENT1_STANCE: "Stance 1",
                SessionKeys.AGENT2_STANCE: "Stance 2",
            },
        ):
            is_valid, error = validate_conversation_requirements()
            assert is_valid is False
            assert "Tema de discusión" in error

    def test_validate_missing_stance(self):
        """Test validation fails with missing stance."""
        with patch(
            "streamlit.session_state",
            {
                SessionKeys.DISCUSSION_TOPIC: "Test topic",
                SessionKeys.AGENT1_STANCE: "",
                SessionKeys.AGENT2_STANCE: "Stance 2",
            },
        ):
            is_valid, error = validate_conversation_requirements()
            assert is_valid is False
            assert "Agente 1" in error


class TestInitializeSessionState:
    """Tests for initialize_session_state function."""

    def test_initialize_empty_state(self):
        """Test initializing empty session state."""
        mock_state = {}
        with patch("streamlit.session_state", mock_state):
            initialize_session_state()
            # Check that some expected keys were set
            assert len(mock_state) > 0
