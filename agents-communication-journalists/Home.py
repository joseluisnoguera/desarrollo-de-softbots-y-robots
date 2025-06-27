"""Home page for the journalists discussion application."""

import streamlit as st

from src.utils import setup_logging

# Setup logging
logger = setup_logging()

# Page configuration
st.set_page_config(
    page_title="Inicio",
    page_icon="👋",
)

# Page content
st.write("# ¡Bienvenido a Discusiones entre Periodistas! 👋")

st.markdown(
    """
    Esta es una herramienta para la discusión entre agentes de IA que actúan como periodistas.

    ## Características:

    - **Generación de Temas**: Crea temas de discusión y posturas opuestas automáticamente
    - **Conversaciones Dinámicas**: Dos agentes IA debaten sobre temas con personalidades configurables

    **👈 Selecciona una página de la barra lateral** para comenzar:

    - **Topics**: Genera temas de discusión y posturas opuestas
    - **Conversation**: Inicia discusiones entre agentes periodistas
    """
)

st.info(
    """
    💡 **Consejo**: Comienza en la página de Topics para generar un tema de discusión,
    luego ve a Conversation para ver a los agentes debatir sobre él.
    """
)

logger.info("Home page loaded successfully")
