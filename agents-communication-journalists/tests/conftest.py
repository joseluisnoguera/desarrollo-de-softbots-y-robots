"""Test configuration and fixtures."""

from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_streamlit():
    """Mock streamlit for testing."""
    with patch("streamlit.secrets") as mock_secrets:
        mock_secrets.__getitem__.return_value = "fake_api_key"
        yield mock_secrets


@pytest.fixture
def mock_gemini_response():
    """Mock Gemini API response."""
    mock_response = Mock()
    mock_response.content = "Test response content"
    return mock_response


@pytest.fixture
def sample_topic_stances():
    """Sample topic stances for testing."""
    return {
        "improved_topic": "Sample improved topic",
        "stance1": "First stance on the topic",
        "stance2": "Opposing stance on the topic",
    }


@pytest.fixture
def sample_agent_config():
    """Sample agent configuration for testing."""
    return {
        "name": "Test Agent",
        "personality": "Professional and analytical",
        "stance": "Pro-technology stance",
        "model_name": "gemini-1.5-flash",
        "temperature": 0.7,
    }
