"""
Tools for the supermarket agent.
"""
from typing import List, Dict, Any
import logging
import httpx
from uuid import uuid4
from langchain_core.tools import tool
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest
from .models import ProductRestockRequest
from .config import WHOLESALER_TIMEOUT
from .exceptions import WholesalerAPIError

logger = logging.getLogger(__name__)


@tool
async def wholesaler_restock(
    products: List[ProductRestockRequest]
) -> List[Dict[str, Any]]:
    """Call the wholesaler agent via A2A to request restocking of products.

    Args:
        products: List of ProductRestockRequest objects with product_id and quantity

    Returns:
        List of dictionaries with 'product_id' and 'quantity' that can be restocked

    Raises:
        WholesalerAPIError: If the A2A call fails
    """
    try:
        # Convert Pydantic models to dictionaries for API call
        products_data = [
            {"product_id": product.product_id, "quantity": product.quantity}
            for product in products
        ]

        # Wholesaler agent A2A server URL
        wholesaler_base_url = 'http://localhost:8586'

        async with httpx.AsyncClient(timeout=WHOLESALER_TIMEOUT) as httpx_client:
            # Initialize A2ACardResolver to fetch agent card
            resolver = A2ACardResolver(
                httpx_client=httpx_client,
                base_url=wholesaler_base_url,
            )

            # Fetch the agent card from wholesaler
            logger.info(f"Fetching wholesaler agent card from {wholesaler_base_url}")
            agent_card = await resolver.get_agent_card()
            logger.info("Successfully fetched wholesaler agent card")

            # Initialize A2A client
            client = A2AClient(
                httpx_client=httpx_client,
                agent_card=agent_card
            )

            # Prepare the message to send to wholesaler
            message_text = f"Please restock the following products: {products_data}"

            send_message_payload = {
                'message': {
                    'role': 'user',
                    'parts': [
                        {'kind': 'text', 'text': message_text}
                    ],
                    'messageId': uuid4().hex,
                },
            }

            request = SendMessageRequest(
                id=str(uuid4()),
                params=MessageSendParams(**send_message_payload)
            )

            # Send message to wholesaler agent via A2A
            logger.info("Sending restock request to wholesaler agent via A2A")
            response = await client.send_message(request)

            # Extract the response message
            response_text = ""
            if hasattr(response, 'root') and hasattr(response.root, 'result'):
                # Handle the nested response structure
                result = response.root.result
                if hasattr(result, 'parts') and result.parts:
                    response_text = result.parts[0].text if hasattr(result.parts[0], 'text') else str(result.parts[0])
            elif hasattr(response, 'result') and hasattr(response.result, 'parts'):
                response_text = response.result.parts[0].text if response.result.parts else "No response"
            else:
                logger.warning(f"Unexpected response format: {type(response)}")
                return products_data

            logger.info(f"Wholesaler response: {response_text}")

            # Try to parse JSON response from wholesaler
            try:
                import json
                wholesaler_data = json.loads(response_text)

                if wholesaler_data.get("status") == "success":
                    restockable_products = wholesaler_data.get("restockable_products", [])
                    logger.info(f"Wholesaler can restock {len(restockable_products)} products")
                    return restockable_products
                else:
                    logger.warning(f"Wholesaler error: {wholesaler_data.get('message')}")
                    return []

            except json.JSONDecodeError:
                logger.warning("Could not parse wholesaler response as JSON")
                # Fallback: return original products data
                return products_data

    except Exception as e:
        error_msg = f"A2A error calling wholesaler agent: {e}"
        logger.error(error_msg)
        raise WholesalerAPIError(error_msg) from e
