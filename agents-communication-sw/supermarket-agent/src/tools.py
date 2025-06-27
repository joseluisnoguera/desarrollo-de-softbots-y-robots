"""
Tools for the supermarket agent.
"""
from typing import List, Dict, Any
import logging
import httpx
from langchain_core.tools import tool
from .models import ProductRestockRequest
from .config import WHOLESALER_API_URL, WHOLESALER_TIMEOUT
from .exceptions import WholesalerAPIError

logger = logging.getLogger(__name__)


@tool
async def wholesaler_restock(
    products: List[ProductRestockRequest]
) -> List[Dict[str, Any]]:
    """Call the wholesaler agent to request restocking of products.

    Args:
        products: List of ProductRestockRequest objects with product_id and quantity

    Returns:
        List of dictionaries with 'product_id' and 'quantity' that can be restocked

    Raises:
        WholesalerAPIError: If the API call fails
    """
    try:
        # Convert Pydantic models to dictionaries for API call
        products_data = [
            {"product_id": product.product_id, "quantity": product.quantity}
            for product in products
        ]

        async with httpx.AsyncClient() as client:
            response = await client.post(
                WHOLESALER_API_URL,
                json={"products": products_data},
                timeout=WHOLESALER_TIMEOUT
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        error_msg = f"Network error calling wholesaler agent: {e}"
        logger.error(error_msg)
        raise WholesalerAPIError(error_msg) from e
    except httpx.HTTPStatusError as e:
        error_msg = f"HTTP error {e.response.status_code} calling wholesaler agent"
        logger.error(error_msg)
        raise WholesalerAPIError(error_msg) from e
    except Exception as e:
        error_msg = f"Unexpected error calling wholesaler agent: {e}"
        logger.error(error_msg)
        raise WholesalerAPIError(error_msg) from e
