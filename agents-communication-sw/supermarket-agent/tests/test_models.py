"""
Basic test for the supermarket agent models.
"""
import pytest
from src.models import ProductRestockRequest, AgentConfig


def test_product_restock_request():
    """Test ProductRestockRequest model creation."""
    product = ProductRestockRequest(product_id="test_id", quantity=10)
    assert product.product_id == "test_id"
    assert product.quantity == 10


def test_agent_config():
    """Test AgentConfig model creation."""
    config = AgentConfig(
        name="Test Agent",
        personality="friendly",
        stance="helpful"
    )
    assert config.name == "Test Agent"
    assert config.personality == "friendly"
    assert config.stance == "helpful"
    assert config.model_name == "gemini-2.5-flash"  # default value
    assert abs(config.temperature - 0.7) < 0.001  # default value


def test_agent_config_custom_model():
    """Test AgentConfig with custom model settings."""
    config = AgentConfig(
        name="Custom Agent",
        personality="professional",
        model_name="gemini-1.5-pro",
        temperature=0.5
    )
    assert config.model_name == "gemini-1.5-pro"
    assert abs(config.temperature - 0.5) < 0.001
