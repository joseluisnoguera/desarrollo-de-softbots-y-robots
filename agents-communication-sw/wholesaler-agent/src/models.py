"""
Models for the wholesaler agent.
"""
from pydantic import BaseModel
from typing import Optional


class AgentConfig(BaseModel):
    """Configuration for the wholesaler agent."""
    name: str
    personality: str
    model_name: str = "gemini-1.5-flash"
    temperature: float = 0.3
    stance: Optional[str] = None


class ProductRestockRequest(BaseModel):
    """Model for product restock requests."""
    product_id: int
    quantity: int


class RestockResponse(BaseModel):
    """Model for restock responses."""
    status: str
    restockable_products: list
    message: str
