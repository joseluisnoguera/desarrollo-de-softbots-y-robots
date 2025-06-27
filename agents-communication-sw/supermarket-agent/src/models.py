"""
Data models for the supermarket agent application.
"""
from typing import List
from pydantic import BaseModel, Field


class ProductRestockRequest(BaseModel):
    """Product restock request item"""
    product_id: str = Field(description="The ID of the product to restock")
    quantity: int = Field(description="The quantity to restock")


class AgentConfig(BaseModel):
    """Configuration for the Gemini agent"""
    name: str
    personality: str
    stance: str = ""
    model_name: str = "gemini-2.5-flash"
    temperature: float = 0.7


class MCPServerConfig(BaseModel):
    """Configuration for MCP server connection"""
    command: str
    args: List[str]
    cwd: str
