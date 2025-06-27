"""Gemini-based agents for journalist discussions."""

import logging

from langchain_google_genai import ChatGoogleGenerativeAI

from .config import DEFAULT_MODEL_NAME, DEFAULT_TEMPERATURE
from .exceptions import APIKeyError, ConversationError, TopicGenerationError
from .models import TopicStances
from .utils import get_api_key

logger = logging.getLogger(__name__)


class GeminiAgent:
    """A Gemini-based AI agent for journalist discussions."""

    def __init__(
        self,
        agent_name: str,
        personality: str = "",
        stance: str = "",
        model_name: str = DEFAULT_MODEL_NAME,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        """Initialize the Gemini agent.

        Args:
            agent_name: Name of the agent.
            personality: Personality description of the agent.
            stance: Agent's stance on the discussion topic.
            model_name: Name of the Gemini model to use.
            temperature: Temperature parameter for response generation.
        """
        self.agent_name = agent_name
        self.personality = personality
        self.stance = stance
        self.model_name = model_name
        self.temperature = temperature
        self._llm: ChatGoogleGenerativeAI | None = None

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        """Lazy initialization of the LLM."""
        if self._llm is None:
            self._llm = self._configure_llm()
        return self._llm

    def _configure_llm(self) -> ChatGoogleGenerativeAI:
        """Configure the Gemini LLM.

        Returns:
            Configured ChatGoogleGenerativeAI instance.

        Raises:
            APIKeyError: If the API key is not available.
        """
        try:
            api_key = get_api_key()
            return ChatGoogleGenerativeAI(
                model=self.model_name, temperature=self.temperature, api_key=api_key
            )
        except Exception as e:
            logger.error(f"Failed to configure LLM: {e}")
            raise APIKeyError(f"Failed to configure LLM: {e}") from e

    def generate_response(self, topic: str, history: str) -> str:
        """Generate a response for the given topic and conversation history.

        Args:
            topic: The discussion topic.
            history: The conversation history.

        Returns:
            Generated response string.

        Raises:
            ConversationError: If response generation fails.
        """
        try:
            prompt = self._build_prompt(topic, history)
            response = self.llm.invoke(prompt)
            logger.info(f"Generated response for {self.agent_name}")
            return response.content
        except Exception as e:
            logger.error(f"Failed to generate response for {self.agent_name}: {e}")
            raise ConversationError(f"Failed to generate response: {e}") from e

    def generate_response_stream(self, topic: str, history: str):
        """Generate a streaming response for the given topic and conversation history.

        Args:
            topic: The discussion topic.
            history: The conversation history.

        Yields:
            String chunks of the response as they are generated.

        Raises:
            ConversationError: If response generation fails.
        """
        try:
            prompt = self._build_prompt(topic, history)
            logger.info(f"Starting streaming response for {self.agent_name}")

            for chunk in self.llm.stream(prompt):
                if hasattr(chunk, 'content') and chunk.content:
                    yield chunk.content

        except Exception as e:
            logger.error(f"Failed to generate streaming response for {self.agent_name}: {e}")
            raise ConversationError(f"Failed to generate streaming response: {e}") from e

    def _build_prompt(self, topic: str, history: str) -> str:
        """Build the prompt for response generation.

        Args:
            topic: The discussion topic.
            history: The conversation history.

        Returns:
            Formatted prompt string.
        """
        return f"""
        Eres un agente con un role de periodista.
        Comienza la conversación presentándote, y si eres el primero en comenzar la conversación también presentando el tema y tu postura sobre él.
        Tu nombre es: {self.agent_name}
        Tu personalidad es: {self.personality}
        Tu postura sobre el tema "{topic}" es: {self.stance}

        Estas conversando con otro agente de IA sobre un tema de discusión.
        La conversación hasta ahora:
        {history}

        Basado en tu personalidad y postura, ¿cuál es tu respuesta?
        Que tu respuesta sea clara, concisa (no te extiendas mucho en la respuesta) y relevante para el tema de discusión.
        Mantén viva la discusión y que tu respuesta sea coherente con tu personalidad y postura.
        """


class GeminiTopicAgent:
    """A Gemini-based agent for generating discussion topics and stances."""

    def __init__(
        self,
        model_name: str = DEFAULT_MODEL_NAME,
        temperature: float = DEFAULT_TEMPERATURE,
    ):
        """Initialize the topic generation agent.

        Args:
            model_name: Name of the Gemini model to use.
            temperature: Temperature parameter for generation.
        """
        self.model_name = model_name
        self.temperature = temperature
        self._llm: ChatGoogleGenerativeAI | None = None

    @property
    def llm(self) -> ChatGoogleGenerativeAI:
        """Lazy initialization of the LLM with structured output."""
        if self._llm is None:
            self._llm = self._configure_llm()
        return self._llm

    def _configure_llm(self) -> ChatGoogleGenerativeAI:
        """Configure the Gemini LLM with structured output.

        Returns:
            Configured ChatGoogleGenerativeAI instance with structured output.

        Raises:
            APIKeyError: If the API key is not available.
        """
        try:
            api_key = get_api_key()
            llm = ChatGoogleGenerativeAI(
                model=self.model_name, temperature=self.temperature, api_key=api_key
            )
            return llm.with_structured_output(TopicStances)
        except Exception as e:
            logger.error(f"Failed to configure topic LLM: {e}")
            raise APIKeyError(f"Failed to configure topic LLM: {e}") from e

    def generate_topic_and_stances(self, topic: str) -> dict[str, str]:
        """Generate an improved topic and opposing stances.

        Args:
            topic: The initial topic string.

        Returns:
            Dictionary with improved_topic, stance1, and stance2.

        Raises:
            TopicGenerationError: If topic generation fails.
        """
        try:
            prompt = self._build_topic_prompt(topic)
            response = self.llm.invoke(prompt)
            logger.info(f"Generated topic and stances for: {topic}")

            return {
                "improved_topic": response.improved_topic,
                "stance1": response.stance1,
                "stance2": response.stance2,
            }
        except Exception as e:
            logger.error(f"Failed to generate topic and stances: {e}")
            raise TopicGenerationError(f"Failed to generate topic and stances: {e}") from e

    def _build_topic_prompt(self, topic: str) -> str:
        """Build the prompt for topic and stance generation.

        Args:
            topic: The initial topic.

        Returns:
            Formatted prompt string.
        """
        return f"""
        Eres un experto en generar temas de discusión.
        Dado el siguiente tema: "{topic}"

        1. Mejora el tema para que sea más claro y conciso para un debate.
        2. Genera dos posturas opuestas y bien definidas sobre el tema mejorado.
        """
