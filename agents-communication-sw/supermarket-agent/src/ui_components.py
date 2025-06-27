"""
UI components for the supermarket agent chat interface.
"""
import streamlit as st
from langchain_core.messages import HumanMessage, AIMessage


class ChatUI:
    """UI components for the chat interface."""

    def __init__(self, agent_name: str, agent_avatar: str):
        self.agent_name = agent_name
        self.agent_avatar = agent_avatar

    def render_header(self):
        """Render the chat header."""
        st.markdown("# Chat con el Agente")
        st.write(
            "Esta página es para iniciar una conversación con el agente del "
            "supermercado."
        )

    def render_chat_history(self):
        """Render the chat history."""
        if "messages" in st.session_state:
            for message in st.session_state.messages:
                if isinstance(message, HumanMessage):
                    with st.chat_message("user", avatar="🧑"):
                        st.markdown(message.content)
                # Do not display AIMessages that are only placeholders for tool calls.
                elif isinstance(message, AIMessage) and message.content.strip():
                    with st.chat_message(self.agent_name, avatar=self.agent_avatar):
                        st.markdown(message.content)

    def get_user_input(self) -> str:
        """Get user input and add it to the conversation."""
        prompt = st.chat_input("¿Qué te gustaría comprar?")
        if prompt:
            st.session_state.messages.append(HumanMessage(content=prompt))
            with st.chat_message("user", avatar="🧑"):
                st.markdown(prompt)
        return prompt
