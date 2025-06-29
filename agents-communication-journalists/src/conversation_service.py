"""Conversation service for managing agent interactions."""

import logging

import streamlit as st

from .config import AGENT1_NAME, AGENT2_NAME, SessionKeys
from .exceptions import ConversationError
from .gemini_agent import GeminiAgent
from .models import ChatMessage

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations between agents."""

    @staticmethod
    def generate_and_append_messages(
        agent1: GeminiAgent, agent2: GeminiAgent, history: str, turns: int, topic: str
    ) -> str:
        """Generate conversation turns between two agents.

        Args:
            agent1: First agent.
            agent2: Second agent.
            history: Current conversation history.
            turns: Number of turns to generate.
            topic: Discussion topic.

        Returns:
            Updated conversation history.

        Raises:
            ConversationError: If conversation generation fails.
        """
        try:
            current_history = history

            for turn in range(turns):
                logger.info(f"Generating turn {turn + 1}/{turns}")

                # Agent 1 turn
                try:
                    response1 = agent1.generate_response(topic, current_history)
                    message1 = ChatMessage(role=AGENT1_NAME, content=response1)
                    st.session_state[SessionKeys.MESSAGES].append(message1.dict())
                    current_history += f"{AGENT1_NAME}: {response1}\n"
                    logger.debug(f"{AGENT1_NAME} response: {response1[:100]}...")
                except Exception as e:
                    logger.error(f"Failed to generate response from {AGENT1_NAME}: {e}")
                    raise ConversationError(
                        f"Error generating response from {AGENT1_NAME}: {e}"
                    ) from e

                # Agent 2 turn
                try:
                    response2 = agent2.generate_response(topic, current_history)
                    message2 = ChatMessage(role=AGENT2_NAME, content=response2)
                    st.session_state[SessionKeys.MESSAGES].append(message2.dict())
                    current_history += f"{AGENT2_NAME}: {response2}\n"
                    logger.debug(f"{AGENT2_NAME} response: {response2[:100]}...")
                except Exception as e:
                    logger.error(f"Failed to generate response from {AGENT2_NAME}: {e}")
                    raise ConversationError(
                        f"Error generating response from {AGENT2_NAME}: {e}"
                    ) from e

            return current_history

        except Exception as e:
            logger.error(f"Failed to generate conversation: {e}")
            raise ConversationError(f"Failed to generate conversation: {e}") from e

    @staticmethod
    def create_agents() -> tuple[GeminiAgent, GeminiAgent]:
        """Create and configure both agents from session state.

        Returns:
            Tuple of (agent1, agent2).

        Raises:
            ConversationError: If agent creation fails.
        """
        try:
            from .config import DEFAULT_AGENT1_NAME, DEFAULT_AGENT2_NAME

            agent1 = GeminiAgent(
                agent_name=DEFAULT_AGENT1_NAME,
                personality=st.session_state.get(SessionKeys.AGENT1_PERSONALITY, ""),
                stance=st.session_state.get(SessionKeys.AGENT1_STANCE, ""),
                model_name=st.session_state.get(SessionKeys.AGENT1_MODEL, ""),
                temperature=st.session_state.get(SessionKeys.AGENT1_TEMPERATURE, 0.7),
            )

            agent2 = GeminiAgent(
                agent_name=DEFAULT_AGENT2_NAME,
                personality=st.session_state.get(SessionKeys.AGENT2_PERSONALITY, ""),
                stance=st.session_state.get(SessionKeys.AGENT2_STANCE, ""),
                model_name=st.session_state.get(SessionKeys.AGENT2_MODEL, ""),
                temperature=st.session_state.get(SessionKeys.AGENT2_TEMPERATURE, 0.7),
            )

            logger.info("Successfully created both agents")
            return agent1, agent2

        except Exception as e:
            logger.error(f"Failed to create agents: {e}")
            raise ConversationError(f"Failed to create agents: {e}") from e

    @staticmethod
    def reset_conversation() -> None:
        """Reset the conversation state."""
        st.session_state[SessionKeys.MESSAGES] = []
        st.session_state[SessionKeys.HISTORY] = ""
        st.session_state[SessionKeys.AGENT1] = None
        st.session_state[SessionKeys.AGENT2] = None
        logger.info("Conversation state reset")

    @staticmethod
    def generate_and_append_messages_streaming(
        agent1: GeminiAgent,
        agent2: GeminiAgent,
        history: str,
        turns: int,
        topic: str,
    ) -> str:
        """Generate conversation messages with direct addition to session state.

        Args:
            agent1: First agent.
            agent2: Second agent.
            history: Current conversation history.
            turns: Number of turns to generate.
            topic: Discussion topic.

        Returns:
            Updated conversation history.

        Raises:
            ConversationError: If message generation fails.
        """
        try:
            current_history = history

            # Import here to avoid circular imports
            from .config import AGENT1_NAME, AGENT2_NAME

            for turn in range(turns):
                logger.info(f"Generating streaming turn {turn + 1}/{turns}")

                # Agent 1 turn - generate complete response first
                try:
                    response1 = agent1.generate_response(topic, current_history)
                    message1 = ChatMessage(role=AGENT1_NAME, content=response1)
                    st.session_state[SessionKeys.MESSAGES].append(message1.dict())
                    current_history += f"{AGENT1_NAME}: {response1}\n"
                    logger.debug(f"{AGENT1_NAME} response: {response1[:100]}...")

                except Exception as e:
                    logger.error(f"Failed to generate response from {AGENT1_NAME}: {e}")
                    raise ConversationError(
                        f"Error generating response from {AGENT1_NAME}: {e}"
                    ) from e

                # Agent 2 turn - generate complete response first
                try:
                    response2 = agent2.generate_response(topic, current_history)
                    message2 = ChatMessage(role=AGENT2_NAME, content=response2)
                    st.session_state[SessionKeys.MESSAGES].append(message2.dict())
                    current_history += f"{AGENT2_NAME}: {response2}\n"
                    logger.debug(f"{AGENT2_NAME} response: {response2[:100]}...")

                except Exception as e:
                    logger.error(f"Failed to generate response from {AGENT2_NAME}: {e}")
                    raise ConversationError(
                        f"Error generating response from {AGENT2_NAME}: {e}"
                    ) from e

            return current_history

        except Exception as e:
            logger.error(f"Failed to generate conversation: {e}")
            raise ConversationError(f"Failed to generate conversation: {e}") from e
