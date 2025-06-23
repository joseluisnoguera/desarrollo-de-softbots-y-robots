import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
import json
from pydantic import BaseModel, Field

class GeminiAgent:
    def __init__(self, agent_name, personality, stance, model_name="gemini-1.5-flash", temperature=0.7):
        self.personality = personality
        self.stance = stance
        self.agent_name = agent_name
        self.model_name = model_name
        self.temperature = temperature
        self.llm = self._configure_llm()

    def _configure_llm(self):
        return ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=st.secrets["GOOGLE_API_KEY"]
        )

    def generate_response(self, topic, history):
        prompt = f"""
        Eres un agente con un role de periodista.
        Comienza la conversación presentándote, y si eres el primero en comenzar la conversación también presentando el tema y tu postura sobre él.
        Tu nombre es: {self.agent_name}
        Tu personalidad es: {self.personality}
        Tu postura sobre el tema "{topic}" es: {self.stance}

        Estas conversando con otro agente de IA sobre un tema de discusión.
        La conversación hasta ahora:
        {history}

        Basado en tu personalidad y postura, ¿cuál es tu respuesta?
        Que tu respuesta sea clara, concisa y relevante para el tema de discusión.
        Mantén viva la discusión y que tu respuesta sea coherente con tu personalidad y postura.
        """
        return self.llm.invoke(prompt).content

class TopicStances(BaseModel):
    improved_topic: str = Field(description="El tema de discusión mejorado, más claro y conciso.")
    stance1: str = Field(description="La primera postura opuesta sobre el tema.")
    stance2: str = Field(description="La segunda postura opuesta sobre el tema.")

class GeminiTopicAgent:
    def __init__(self, model_name="gemini-1.5-flash", temperature=0.7):
        self.model_name = model_name
        self.temperature = temperature
        self.llm = self._configure_llm()

    def _configure_llm(self):
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=st.secrets["GOOGLE_API_KEY"]
        )
        return llm.with_structured_output(TopicStances)

    def generate_topic_and_stances(self, topic):
        prompt = f"""
        Eres un experto en generar temas de discusión.
        Dado el siguiente tema: "{topic}"

        1. Mejora el tema para que sea más claro y conciso para un debate.
        2. Genera dos posturas opuestas y bien definidas sobre el tema mejorado.
        """
        response = self.llm.invoke(prompt)
        return {
            "improved_topic": response.improved_topic,
            "stance1": response.stance1,
            "stance2": response.stance2,
        }
