#!/usr/bin/env python3
"""
Test script to send messages to wholesaler-agent and observe detailed logs.
"""
import httpx
import asyncio
from uuid import uuid4
from a2a.client import A2ACardResolver, A2AClient
from a2a.types import MessageSendParams, SendMessageRequest

async def test_wholesaler_agent():
    """Test the wholesaler-agent with various messages to see detailed logs."""

    async with httpx.AsyncClient() as httpx_client:
        print("=" * 60)
        print("TESTING WHOLESALER AGENT LOGGING")
        print("=" * 60)

        # Set up A2A client
        wholesaler_base_url = 'http://localhost:8586'

        # Initialize A2ACardResolver to fetch agent card
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=wholesaler_base_url,
        )

        # Fetch the agent card from wholesaler
        print("Fetching wholesaler agent card...")
        agent_card = await resolver.get_agent_card()
        print("Successfully fetched wholesaler agent card")

        # Initialize A2A client
        client = A2AClient(
            httpx_client=httpx_client,
            agent_card=agent_card
        )

        # Test 1: Simple greeting
        print("\n1. Testing simple greeting...")
        await send_message(client, 'Hola, ¿cómo estás?')

        # Test 2: Restock request with products
        print("\n2. Testing restock request...")
        restock_message = "I need to restock products: 'product_id': 1, 'quantity': 10 and 'product_id': 2, 'quantity': 5"
        await send_message(client, restock_message)

        # Test 3: More formal restock request
        print("\n3. Testing formal restock request...")
        formal_restock = 'Please restock products: {"product_id": 3, "quantity": 15} and {"product_id": 4, "quantity": 20}'
        await send_message(client, formal_restock)

        # Test 4: General question
        print("\n4. Testing general question...")
        await send_message(client, 'What services do you offer as a wholesaler?')

        print("\n" + "=" * 60)
        print("ALL TESTS COMPLETED")
        print("Check the server logs and /tmp/wholesaler-agent.log for detailed information")
        print("=" * 60)

async def send_message(client: A2AClient, message_text: str):
    """Send a message using the A2A client and print the response."""

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
    print(f"Sending: {message_text}")
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
        response_text = str(response)

    print(f"Response: {response_text[:200]}...")

if __name__ == "__main__":
    asyncio.run(test_wholesaler_agent())
