"""Data models for the journalists discussion application."""

from pydantic import BaseModel, Field


class TopicStances(BaseModel):
    """Model for topic generation with opposing stances."""

    improved_topic: str = Field(
        description="El tema de discusión mejorado, más claro y conciso."
    )
    stance1: str = Field(description="La primera postura opuesta sobre el tema.")
    stance2: str = Field(description="La segunda postura opuesta sobre el tema.")


class ChatMessage(BaseModel):
    """Model for chat messages."""

    role: str = Field(description="The role/name of the agent sending the message.")
    content: str = Field(description="The content of the message.")


class AgentConfiguration(BaseModel):
    """Model for agent configuration."""

    name: str = Field(description="The name of the agent.")
    personality: str = Field(default="", description="The personality of the agent.")
    stance: str = Field(default="", description="The stance of the agent on the topic.")
    model_name: str = Field(
        default="gemini-1.5-flash", description="The model name to use."
    )
    temperature: float = Field(
        default=0.7, description="The temperature for the model."
    )


class ConversationState(BaseModel):
    """Model for conversation state."""

    topic: str = Field(default="", description="The discussion topic.")
    messages: list[ChatMessage] = Field(
        default_factory=list, description="List of messages."
    )
    history: str = Field(default="", description="Conversation history as text.")
    agent1_config: AgentConfiguration = Field(default_factory=AgentConfiguration)
    agent2_config: AgentConfiguration = Field(default_factory=AgentConfiguration)
    message_count: int = Field(
        default=1, description="Number of turns per interaction."
    )
