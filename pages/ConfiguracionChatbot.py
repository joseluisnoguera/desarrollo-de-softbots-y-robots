import os
import json
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Configuración del Chatbot", page_icon="⚙️")
st.header('Configuración del Chatbot Recepcionista')

# Definir la ruta del archivo de configuración
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "chatbot_config.json")
os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)

# Función para cargar la configuración actual
def load_config():
    default_config = {
        "BEHAVIOUR_STR": "profesional",
        "TOPICS_STR": "turismo, puntos de interes para turístas, eventos turísticos, direcciones para llegar a lugares turísticos, comercios que utilizarían turistas, atracciones, viajes, eventos que pueden ser de interes para turistas como eventos deportivos, temas relacionados con turismo",
        "BLOCKLIST_STR": "tomar posiciones políticas, religión, temas sensibles, temas no relacionados a los estipulados anteriormente."
    }

    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            st.error(f"Error al cargar la configuración: {e}")
            return default_config
    return default_config

# Función para guardar la configuración
def save_config(config):
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        st.error(f"Error al guardar la configuración: {e}")
        return False

# Cargar la configuración actual
current_config = load_config()

# Crear formulario para modificar la configuración
with st.form("config_form"):
    st.subheader("Ajustes del chatbot")

    # Información sobre el uso
    st.info("""
    **Instrucciones:**
    - Modifica los temas permitidos y bloqueados según tus necesidades
    - Modifica el comportamiento del agente según lo que desees
    - La configuración se aplicará automáticamente al chatbot cuando la guardes
    - Los cambios se mantendrán entre sesiones
    """)

    # Campos de entrada para modificar la configuración
    topics_str = st.text_area(
        "Temas permitidos",
        value=current_config["TOPICS_STR"],
        height=150,
        help="Lista de temas sobre los que el chatbot puede hablar, separados por comas."
    )

    blocklist_str = st.text_area(
        "Temas bloqueados",
        value=current_config["BLOCKLIST_STR"],
        height=100,
        help="Lista de temas prohibidos para el chatbot, separados por comas."
    )

    behaviour_str = st.text_area(
        "Comportamiento del agente",
        value=current_config["BEHAVIOUR_STR"],
        height=100,
        help="Descripción del comportamiento del agente."
    )

    # Añadimos un espacio para mejorar la presentación
    st.write("")

    # Botón de guardado con clara visibilidad
    submit_button = st.form_submit_button(
        label="💾 Guardar configuración",
        type="primary",
        use_container_width=True
    )

# Manejar el guardado de la configuración
if submit_button:
    new_config = {
        "TOPICS_STR": topics_str,
        "BLOCKLIST_STR": blocklist_str,
        "BEHAVIOUR_STR": behaviour_str
    }

    if save_config(new_config):
        st.success("✅ Configuración guardada correctamente. Los cambios se aplicarán a las nuevas conversaciones del chatbot.")

        # Mostrar la configuración actualizada
        st.subheader("Configuración actualizada")
        st.write("**Temas permitidos:**")
        st.info(topics_str)
        st.write("**Temas bloqueados:**")
        st.info(blocklist_str)
        st.write("**Comportamiento del agente:**")
        st.info(behaviour_str)
    else:
        st.error("❌ No se pudo guardar la configuración.")

# Sección de vista previa y prueba
st.subheader("Vista previa de la configuración actual")
with st.expander("Ver configuración actual"):
    st.write("**Temas permitidos:**")
    st.code(current_config["TOPICS_STR"])
    st.write("**Temas bloqueados:**")
    st.code(current_config["BLOCKLIST_STR"])
    st.write("**Comportamiento del agente:**")
    st.code(current_config["BEHAVIOUR_STR"])

# Sección de ayuda
with st.expander("Ayuda"):
    st.write("""
    ### Cómo funciona
    - El chatbot utiliza estas configuraciones para determinar qué temas puede discutir
    - Temas permitidos define los temas permitidos que el chatbot conoce
    - Temas bloqueados define los temas o comportamientos que el chatbot debe evitar

    ### Consejos
    - Sea específico en la definición de los temas permitidos
    - Asegúrese de incluir todas las variantes o sinónimos importantes
    - Mantenga la lista de temas bloqueados actualizada según las necesidades
    """)
