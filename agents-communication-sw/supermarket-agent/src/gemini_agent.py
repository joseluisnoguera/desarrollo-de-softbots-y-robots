import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
import os
import asyncio
import logging
import httpx
import json

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@tool
async def wholesaler_restock(products: list) -> list:
    """Call the wholesaler agent to request restocking of products.

    Args:
        products: List of dictionaries with 'product_id' and 'quantity' keys

    Returns:
        List of dictionaries with 'product_id' and 'quantity' that can be restocked
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8080/restock",
                json={"products": products},
                timeout=30.0
            )
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logging.error(f"Error calling wholesaler agent: {e}")
        return []

class GeminiAgent:
    def __init__(self, agent_name, personality, stance, model_name="gemini-1.5-flash", temperature=0.7):
        self.personality = personality
        self.stance = stance
        self.agent_name = agent_name
        self.model_name = model_name
        self.temperature = temperature
        self.tools = []
        self.llm = None

        mcp_server_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'supermarket-api'))

        # MCP client configuration for the supermarket API (Go server)
        self.mcp_server_path = mcp_server_path
        self.mcp_client = None

    async def initialize(self):
        """Initializes the agent's tools and LLM asynchronously."""
        if not self.tools:
            try:
                # Create MCP client for the supermarket API
                self.mcp_client = MultiServerMCPClient({
                    "supermarket": {
                        "command": "go",
                        "args": ["run", "cmd/mcp-server/mcp_server.go"],
                        "cwd": self.mcp_server_path
                    }
                })

                # Get tools from MCP client (supermarket API)
                mcp_tools = await self.mcp_client.get_tools()
                # Add our custom wholesaler tool
                self.tools = mcp_tools + [wholesaler_restock]
                self.llm = self._configure_llm()
            except Exception as e:
                logger.error(f"Error initializing MCP client: {e}")
                # Fallback to just the wholesaler tool if MCP fails
                self.tools = [wholesaler_restock]
                self.llm = self._configure_llm()

    def _configure_llm(self):
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=st.secrets["GOOGLE_API_KEY"]
        )
        return llm.bind_tools(self.tools)

    async def generate_response(self, history):
        prompt = f"""
        Eres un agente de IA que representa a un supermercado.
        Tu nombre es: {self.agent_name}
        Tu personalidad es: {self.personality}

        Tu función es ayudar a los clientes con sus necesidades en el supermercado.
        Se te ha proporcionado un conjunto de herramientas para interactuar con los sistemas del supermercado.
        Debes utilizar estas herramientas siempre que sea apropiado para responder a las consultas de los usuarios de forma eficaz.
        Si necesitas reponer mercadería, utiliza al agente Wholesaler para confirmar la reposición de productos, y con esto haz la reposición en el inventario del supermercado.

        **Instrucciones importantes para el uso de herramientas:**
        1.  **Comunicación proactiva:** Antes de ejecutar una herramienta, SIEMPRE debes informar al usuario de la acción que estás a punto de realizar con un mensaje claro y conciso. Por ejemplo: "Voy a consultar el inventario" o "Permíteme añadir eso a tu cesta". Esto asegura que el usuario esté siempre informado y evita enviar mensajes vacíos.
        2.  **Uso encadenado:** A veces necesitarás hacer varias llamadas a diferentes herramientas para completar una tarea. Por ejemplo, para comprar un producto, puede que primero necesites buscar su ID con la herramienta de listar productos y luego usar la herramienta de compra.
        3.  **Búsqueda de IDs:** Si necesitas el ID de algún producto para otra herramienta (como comprar o reponer), utiliza primero la herramienta de listado de productos para encontrarlo. No asumas que conoces el ID.
        """

        messages = [SystemMessage(content=prompt)]
        messages.extend(history)

        return await self.llm.ainvoke(messages)
