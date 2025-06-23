import streamlit as st
import json
from src.gemini_agent import GeminiTopicAgent

st.set_page_config(page_title="Topics", page_icon="📝")

st.markdown("# Temas")
st.sidebar.header("Temas")

st.write(
    """
    Esta página te permite generar un tema de discusión y ver dos posturas diferentes sobre él.
    """
)

topic = st.text_input("Ingresa un tema para discusión")

if st.button("Generar Tema"):
    if topic:
        agent = GeminiTopicAgent()
        result = agent.generate_topic_and_stances(topic)
        st.session_state.generated_topic = result
    else:
        st.warning("Por favor, ingresa un tema.")

if "generated_topic" in st.session_state:
    result = st.session_state.generated_topic
    st.text_area("Tema Mejorado", result["improved_topic"], height=100, disabled=True)
    col1, col2 = st.columns(2)
    with col1:
        st.text_area("Postura 1", result["stance1"], height=200, disabled=True)
    with col2:
        st.text_area("Postura 2", result["stance2"], height=200, disabled=True)

    if st.button("Guardar para Conversación"):
        st.session_state.discussion_topic = result["improved_topic"]
        st.session_state.agent1_stance = result["stance1"]
        st.session_state.agent2_stance = result["stance2"]
        st.success("¡Tema y posturas guardados para la conversación!")
