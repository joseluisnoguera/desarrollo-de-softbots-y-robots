import uvicorn
import os
import logging
from dotenv import load_dotenv

from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
)
from src.agent_executor import (
    WholesalerAgentExecutor,  # type: ignore[import-untyped]
)

# Load environment variables
load_dotenv()

# Configure logging for the main module
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/tmp/wholesaler-agent.log')
    ]
)

logger = logging.getLogger(__name__)


if __name__ == '__main__':
    logger.info("Starting Wholesaler Agent Server...")

    # --8<-- [start:AgentSkill]
    restock_skill = AgentSkill(
        id='restock_products',
        name='Process product restock requests',
        description='Processes restock requests and returns available quantities for products',
        tags=['restock', 'wholesaler', 'inventory'],
        examples=['Please restock products', 'Check availability for products', 'Restock request'],
    )

    general_skill = AgentSkill(
        id='general_assistance',
        name='General wholesaler assistance',
        description='Provides general assistance and information about wholesaler services',
        tags=['assistance', 'wholesaler', 'general'],
        examples=['hello', 'help', 'what can you do'],
    )
    # --8<-- [end:AgentSkill]

    logger.info("Created agent skills for restock and general assistance")

    # --8<-- [start:AgentCard]
    # This will be the public-facing agent card
    public_agent_card = AgentCard(
        name='Wholesaler Agent',
        description='AI-powered wholesaler agent for processing restock requests and inventory management',
        url='http://localhost:8586/',
        version='2.0.0',
        defaultInputModes=['text'],
        defaultOutputModes=['text'],
        capabilities=AgentCapabilities(streaming=True),
        skills=[restock_skill, general_skill],  # Updated skills
        supportsAuthenticatedExtendedCard=False,  # Simplified for now
    )
    # --8<-- [end:AgentCard]

    logger.info("Created public agent card")

    request_handler = DefaultRequestHandler(
        agent_executor=WholesalerAgentExecutor(),
        task_store=InMemoryTaskStore(),
    )

    logger.info("Created request handler with WholesalerAgentExecutor")

    server = A2AStarletteApplication(
        agent_card=public_agent_card,
        http_handler=request_handler,
    )

    logger.info("Created A2A Starlette application")
    logger.info("Server starting on localhost:8586...")
    logger.info("Logs will be written to /tmp/wholesaler-agent.log")

    uvicorn.run(server.build(), host='localhost', port=8586)