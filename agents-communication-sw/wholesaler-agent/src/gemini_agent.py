"""
Gemini agent for the wholesaler application.
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import SystemMessage, HumanMessage
import logging
import json

from .models import AgentConfig
from .config import WHOLESALER_SYSTEM_PROMPT
from .exceptions import AgentInitializationError

logger = logging.getLogger(__name__)


class WholesalerGeminiAgent:
    """Gemini-based agent for wholesaler operations."""

    def __init__(self, config: AgentConfig):
        self.config = config
        self.llm = None
        self._initialized = False

    @classmethod
    def create_default(cls, name: str, personality: str):
        """Create agent with default configuration."""
        config = AgentConfig(
            name=name,
            personality=personality
        )
        return cls(config)

    def initialize(self):
        """Initialize the agent's LLM."""
        if self._initialized:
            logger.info("Agent already initialized, skipping")
            return

        try:
            # Get API key from environment variable
            api_key = os.getenv("GOOGLE_API_KEY")
            if not api_key:
                raise AgentInitializationError("GOOGLE_API_KEY environment variable not set")

            self.llm = ChatGoogleGenerativeAI(
                model=self.config.model_name,
                temperature=self.config.temperature,
                api_key=api_key
            )
            self._initialized = True
            logger.info("Wholesaler Gemini agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize wholesaler agent: {e}")
            raise AgentInitializationError(
                f"Wholesaler agent initialization failed: {e}"
            ) from e

    async def process_restock_request(self, message: str) -> str:
        """Process a restock request using Gemini."""
        if not self.is_initialized():
            return self._create_fallback_response(message)

        try:
            # Prepare the system prompt
            system_prompt = WHOLESALER_SYSTEM_PROMPT.format(
                agent_name=self.config.name,
                personality=self.config.personality
            )

            # Create messages
            messages = [
                SystemMessage(content=system_prompt),
                HumanMessage(content=message)
            ]

            # Get response from Gemini
            response = await self.llm.ainvoke(messages)

            # Extract text content
            response_text = response.content if hasattr(response, 'content') else str(response)

            # Try to extract and validate JSON response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_part = response_text[json_start:json_end]
                # Validate JSON
                parsed_json = json.loads(json_part)
                return json_part
            else:
                return self._create_fallback_response(message)

        except Exception:
            return self._create_fallback_response(message)

    def _create_fallback_response(self, message: str) -> str:
        """Create a fallback response when Gemini doesn't return valid JSON."""
        try:
            import re
            import random

            # Extract product info from the message
            patterns = [
                r'"product_id":\s*(\d+),\s*"quantity":\s*(\d+)',
                r"'product_id':\s*(\d+),\s*'quantity':\s*(\d+)",
                r"product_id[=:]?\s*(\d+).*?quantity[=:]?\s*(\d+)",
                r"(\d+).*?(\d+)",  # Simple: any two numbers
            ]

            products = []
            for pattern in patterns:
                try:
                    matches = re.findall(pattern, message, re.IGNORECASE)
                    if matches:
                        for match in matches:
                            try:
                                product_id = int(match[0])
                                requested_quantity = int(match[1])
                                available_quantity = random.randint(0, requested_quantity)

                                products.append({
                                    "product_id": product_id,
                                    "quantity": available_quantity
                                })
                            except (ValueError, IndexError):
                                continue
                        break
                except Exception:
                    continue

            # Create response
            if "restock" in message.lower() or "product" in message.lower():
                response = {
                    "status": "success",
                    "restockable_products": products,
                    "message": f"Wholesaler can restock {len(products)} products"
                }
            else:
                response = {
                    "status": "success",
                    "message": "Hello! I'm a wholesaler agent. I can help with product restocking.",
                    "restockable_products": []
                }

            return json.dumps(response, indent=2)

        except Exception:
            return json.dumps({
                "status": "error",
                "message": "Processing failed",
                "restockable_products": []
            }, indent=2)

    def _create_error_response(self, error_msg: str) -> str:
        """Create an error response."""
        response = {
            "status": "error",
            "message": f"Wholesaler agent error: {error_msg}",
            "restockable_products": []
        }
        return json.dumps(response, indent=2)

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.llm:
                # Clear the LLM reference
                self.llm = None
            self._initialized = False
            logger.info("Wholesaler Gemini agent cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error during cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore errors during destruction

    def is_initialized(self) -> bool:
        """Check if the agent is properly initialized."""
        return self._initialized and self.llm is not None
