#!/usr/bin/env python3
"""
Test script to verify the fixes in the wholesaler agent.
"""
import asyncio
import sys
import os

# Add the src directory to the path
sys.path.append('/home/jnoguera/projects/desarrollo-de-softbots-y-robots/agents-communication-sw/wholesaler-agent/src')

from gemini_agent import WholesalerGeminiAgent
from config import DEFAULT_AGENT_NAME, DEFAULT_PERSONALITY

async def test_gemini_agent():
    """Test the gemini agent with different messages."""

    print("Testing Wholesaler Gemini Agent Fallback Responses...")

    # Create agent
    agent = WholesalerGeminiAgent.create_default(
        name=DEFAULT_AGENT_NAME,
        personality=DEFAULT_PERSONALITY
    )

    # Test messages
    test_messages = [
        "Hola, ¿cómo estás?",
        "I need to restock products: 'product_id': 1, 'quantity': 10 and 'product_id': 2, 'quantity': 5",
        'Please restock products: {"product_id": 3, "quantity": 15} and {"product_id": 4, "quantity": 20}',
        "What services do you offer as a wholesaler?"
    ]

    for i, message in enumerate(test_messages, 1):
        print(f"\n{'='*60}")
        print(f"Test {i}: {message}")
        print('='*60)

        try:
            # Test fallback response directly
            result = agent._create_fallback_response(message)
            print(f"Fallback Response: {result}")
        except Exception as e:
            print(f"Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_gemini_agent())
