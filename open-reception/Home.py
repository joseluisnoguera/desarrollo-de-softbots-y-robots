import streamlit as st

st.set_page_config(
    page_title="Langchain Chatbot",
    page_icon='💬',
    layout='wide'
)

st.header("Chatbot Recepcionista")
st.subheader("Bienvenido a la Demostración del Chatbot Langchain")

st.write("""
Esta es una aplicación de chatbot sencilla construida usando Streamlit y Langchain. Puedes hacer cualquier pregunta al chatbot y te responderá. El chatbot utiliza el modelo Gemini de Google para generar respuestas.
¡Siéntete libre de explorar las funcionalidades y preguntar lo que quieras!
""")
