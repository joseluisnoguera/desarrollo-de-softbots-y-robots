from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.utils import new_agent_text_message
import json
import random
import re
import logging
import datetime

from .gemini_agent import WholesalerGeminiAgent
from .models import AgentConfig
from .config import DEFAULT_AGENT_NAME, DEFAULT_PERSONALITY

# Configure detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/wholesaler-agent.log')
    ]
)

logger = logging.getLogger(__name__)

def log_message_details(direction: str, message: str, context: str = ""):
    """Log message details with timestamp and direction."""
    timestamp = datetime.datetime.now().isoformat()
    separator = "=" * 80
    logger.info(f"\n{separator}")
    logger.info(f"[{timestamp}] {direction} MESSAGE")
    if context:
        logger.info(f"Context: {context}")
    logger.info(f"Content: {message}")
    logger.info(f"{separator}\n")


# --8<-- [start:WholesalerAgent]
class WholesalerAgent:
    """Wholesaler Agent that processes restock requests using Gemini."""

    def __init__(self):
        """Initialize the wholesaler agent with Gemini."""
        self.gemini_agent = None
        self._initialize_gemini()

    def _initialize_gemini(self):
        """Initialize the Gemini agent."""
        try:
            self.gemini_agent = WholesalerGeminiAgent.create_default(
                name=DEFAULT_AGENT_NAME,
                personality=DEFAULT_PERSONALITY
            )
            self.gemini_agent.initialize()
            logger.info("Wholesaler Gemini agent initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini agent: {e}")
            self.gemini_agent = None

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.gemini_agent:
                self.gemini_agent.cleanup()
                self.gemini_agent = None
            logger.info("WholesalerAgent cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error during WholesalerAgent cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore errors during destruction

    async def invoke(self, message: str) -> str:
        """Process a restock request and return available quantities using Gemini."""

        # Try to use Gemini agent if available
        if self.gemini_agent and self.gemini_agent.is_initialized():
            try:
                if "restock" in message.lower() and "product" in message.lower():
                    return await self.gemini_agent.process_restock_request(message)
                else:
                    # For non-restock messages, use Gemini for general responses
                    return await self.gemini_agent.process_restock_request(
                        f"Responde a este mensaje como un mayorista: {message}"
                    )
            except Exception:
                return self._fallback_restock_processing(message)
        else:
            # Fallback to original logic if Gemini is not available
            return self._fallback_restock_processing(message)

    def _fallback_restock_processing(self, message: str) -> str:
        """Fallback processing when Gemini is not available."""
        if "restock" in message.lower() and "product" in message.lower():
            return self._process_restock_request_fallback(message)
        else:
            return json.dumps({
                "status": "success",
                "message": "Hello! I'm a wholesaler agent. How can I help you?",
                "restockable_products": []
            }, indent=2)

    def _process_restock_request_fallback(self, message: str) -> str:
        """Fallback restock processing using original logic."""
        logger.info("Processing restock request using fallback logic")

        try:
            products_data = []

            # Extract product_id and quantity patterns - handle both single and double quotes
            patterns = [
                r'"product_id":\s*(\d+),\s*"quantity":\s*(\d+)',  # JSON with double quotes
                r"'product_id':\s*(\d+),\s*'quantity':\s*(\d+)",  # Python dict with single quotes
                r"product_id[=:]?\s*(\d+).*?quantity[=:]?\s*(\d+)",  # Natural language
            ]

            matches = []
            for pattern in patterns:
                matches.extend(re.findall(pattern, message))
                if matches:  # If we found matches, use them
                    logger.info(f"Found product matches using pattern: {pattern}")
                    break

            logger.info(f"Extracted {len(matches)} product requests from message")

            if matches:
                for product_id_str, quantity_str in matches:
                    product_id = int(product_id_str)
                    requested_quantity = int(quantity_str)

                    # Simulate wholesaler availability: 0 to requested quantity
                    available_quantity = random.randint(0, requested_quantity)

                    logger.info(f"Product {product_id}: requested={requested_quantity}, available={available_quantity}")

                    products_data.append({
                        "product_id": product_id,
                        "quantity": available_quantity
                    })

            # Return structured JSON response
            response = {
                "status": "success",
                "restockable_products": products_data,
                "message": f"Wholesaler can restock {len(products_data)} products (fallback mode)"
            }

            logger.info(f"Generated fallback response for {len(products_data)} products")
            return json.dumps(response, indent=2)

        except Exception as e:
            logger.error(f"Error in fallback restock processing: {str(e)}")
            # Return error response
            error_response = {
                "status": "error",
                "message": f"Failed to process restock request: {str(e)}",
                "restockable_products": []
            }
            return json.dumps(error_response, indent=2)


# --8<-- [end:WholesalerAgent]


# --8<-- [start:WholesalerAgentExecutor_init]
class WholesalerAgentExecutor(AgentExecutor):
    """Wholesaler Agent Executor Implementation."""

    def __init__(self):
        self.agent = WholesalerAgent()

    def cleanup(self):
        """Clean up resources."""
        try:
            if self.agent:
                self.agent.cleanup()
            logger.info("WholesalerAgentExecutor cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error during WholesalerAgentExecutor cleanup: {e}")

    def __del__(self):
        """Destructor to ensure cleanup."""
        try:
            self.cleanup()
        except Exception:
            pass  # Ignore errors during destruction

    # --8<-- [end:WholesalerAgentExecutor_init]
    # --8<-- [start:WholesalerAgentExecutor_execute]
    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        # Log execution start
        logger.info("WholesalerAgentExecutor.execute called")

        # Extract message from context
        message_text = ""
        if hasattr(context, 'message') and context.message:
            if hasattr(context.message, 'parts') and context.message.parts:
                # Handle different Part object structures
                part = context.message.parts[0]
                if hasattr(part, 'text'):
                    message_text = part.text
                elif hasattr(part, 'content') and hasattr(part.content, 'text'):
                    message_text = part.content.text
                elif hasattr(part, 'kind') and part.kind == 'text':
                    # Try to access text content in different ways
                    if hasattr(part, 'text'):
                        message_text = part.text
                    elif hasattr(part, 'content'):
                        message_text = str(part.content)
                else:
                    # If we can't extract text properly, convert to string and extract
                    part_str = str(part)
                    # Extract text from TextPart string representation like: root=TextPart(kind='text', metadata=None, text='actual text')
                    import re
                    match = re.search(r"text='([^']*)'", part_str)
                    if match:
                        message_text = match.group(1)
                    else:
                        message_text = part_str

        # Log extracted message
        log_message_details("EXTRACTED", message_text, "WholesalerAgentExecutor.execute")

        # Process the message
        result = await self.agent.invoke(message_text)

        # Log final result being sent to event queue
        log_message_details("QUEUING", result, "WholesalerAgentExecutor.execute - to event_queue")

        await event_queue.enqueue_event(new_agent_text_message(result))

        logger.info("WholesalerAgentExecutor.execute completed successfully")

    # --8<-- [end:WholesalerAgentExecutor_execute]

    # --8<-- [start:WholesalerAgentExecutor_cancel]
    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')

    # --8<-- [end:WholesalerAgentExecutor_cancel]


# Keep the old HelloWorldAgent for compatibility
class HelloWorldAgent:
    """Hello World Agent."""

    async def invoke(self) -> str:
        return 'Hello World'


class HelloWorldAgentExecutor(AgentExecutor):
    """Test AgentProxy Implementation."""

    def __init__(self):
        self.agent = HelloWorldAgent()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        result = await self.agent.invoke()
        await event_queue.enqueue_event(new_agent_text_message(result))

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        raise Exception('cancel not supported')