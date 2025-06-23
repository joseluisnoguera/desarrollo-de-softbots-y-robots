from src.gemini_agent import get_tools
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Dict, Any
import uvicorn
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Wholesaler Agent", version="1.0.0")

# Get the tools
tools = get_tools()
restock_tool = tools[0]  # We know we only have one tool

class ProductRequest(BaseModel):
    product_id: str
    quantity: int

class RestockRequest(BaseModel):
    products: List[ProductRequest]

class RestockResponse(BaseModel):
    products: List[Dict[str, Any]]

@app.post("/restock", response_model=RestockResponse)
async def restock_endpoint(request: RestockRequest):
    """Endpoint to handle restock requests from other agents."""
    logger.info(f"Received restock request: {request.products}")

    # Convert the request to the format expected by our tool
    products_data = [{"product_id": p.product_id, "quantity": p.quantity} for p in request.products]

    # Call our restock function
    result = restock_tool.func(products_data)

    logger.info(f"Restock response: {result}")

    return RestockResponse(products=result)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "agent": "wholesaler"}

if __name__ == "__main__":
    logger.info("Starting wholesaler agent server...")
    uvicorn.run(app, host="0.0.0.0", port=8080)
