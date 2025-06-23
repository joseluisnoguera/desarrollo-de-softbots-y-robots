import os
import json
import streamlit as st

# Configuración de la página
st.set_page_config(page_title="Configuración del Chatbot", page_icon="⚙️")
st.header('Configuración del Chatbot Recepcionista')

# --- Usuarios simulados ---
SIMULATED_USERS = [
    {"name": "Usuario 1", "uuid": "b1e7c1e2-1a2b-4c3d-9e4f-1a2b3c4d5e6f"},
    {"name": "Usuario 2", "uuid": "a2b3c4d5-6e7f-8a9b-0c1d-2e3f4a5b6c7d"},
    {"name": "Usuario 3", "uuid": "c3d4e5f6-7a8b-9c0d-1e2f-3a4b5c6d7e8f"}
]

st.subheader("Selector de usuario")
user_names = [user["name"] for user in SIMULATED_USERS]
# Determinar el índice del usuario seleccionado según session_state
selected_uuid = st.session_state.get("selected_user_uuid", SIMULATED_USERS[0]["uuid"])
selected_user_idx = next((i for i, u in enumerate(SIMULATED_USERS) if u["uuid"] == selected_uuid), 0)
selected_user_idx = st.selectbox(
    "Selecciona un usuario:",
    range(len(user_names)),
    format_func=lambda i: user_names[i],
    key="user_selector",
    index=selected_user_idx
)
selected_user = SIMULATED_USERS[selected_user_idx]
# Si el usuario seleccionado cambia, actualiza session_state y recarga
if st.session_state.get("selected_user_uuid", None) != selected_user["uuid"]:
    st.session_state["selected_user_uuid"] = selected_user["uuid"]
    st.session_state["selected_user_name"] = selected_user["name"]
    st.rerun()
st.info(f"Usuario seleccionado: {selected_user['name']} (UUID: {selected_user['uuid']})")

# --- Visualización de información recolectada por usuario ---
st.subheader("Información recolectada de usuarios")
info_user = selected_user  # Usar el usuario seleccionado en el selector principal
user_info_key = f"user_info_{info_user['uuid']}"
user_info = st.session_state.get(user_info_key, None)
if user_info is None:
    try:
        from utils import load_user_info_from_disk
        user_info = load_user_info_from_disk(info_user['uuid'])
        st.session_state[user_info_key] = user_info
    except Exception:
        user_info = []
with st.expander(f"Ver información recolectada para {info_user['name']}"):
    if not user_info or user_info == "No hay información recolectada para este usuario.":
        st.info("No hay información recolectada para este usuario.")
    else:
        # Si es string, intentar parsear
        if isinstance(user_info, str):
            try:
                user_info = json.loads(user_info)
            except Exception:
                st.warning("No se pudo interpretar la información como JSON. Mostrando texto plano.")
                st.code(user_info)
                user_info = None
        if user_info:
            if isinstance(user_info, list):
                for idx, item in enumerate(user_info):
                    st.markdown(f"**Bloque {idx+1}:**")
                    # Edición y borrado
                    col1, col2 = st.columns([3,1])
                    with col1:
                        if isinstance(item, dict):
                            st.json(item, expanded=False)
                        else:
                            st.code(str(item))
                    with col2:
                        if st.button("✏️ Editar", key=f"edit_{info_user['uuid'].replace('-', '')}_{idx}"):
                            st.session_state[f"edit_mode_{info_user['uuid'].replace('-', '')}_{idx}"] = True
                        if st.button("🗑️ Borrar", key=f"delete_{info_user['uuid'].replace('-', '')}_{idx}"):
                            user_info.pop(idx)
                            st.session_state[user_info_key] = user_info
                            # Guardar en disco
                            from utils import save_user_info_to_disk
                            save_user_info_to_disk(info_user['uuid'], user_info)
                            st.rerun()
                    # Edición en línea
                    if st.session_state.get(f"edit_mode_{info_user['uuid'].replace('-', '')}_{idx}", False):
                        edited = st.text_area("Editar bloque (JSON)", value=json.dumps(item, ensure_ascii=False, indent=2), key=f"edit_area_{info_user['uuid'].replace('-', '')}_{idx}")
                        if st.button("💾 Guardar cambios", key=f"save_{info_user['uuid'].replace('-', '')}_{idx}"):
                            try:
                                new_item = json.loads(edited)
                                user_info[idx] = new_item
                                st.session_state[user_info_key] = user_info
                                from utils import save_user_info_to_disk
                                save_user_info_to_disk(info_user['uuid'], user_info)
                                st.session_state[f"edit_mode_{info_user['uuid'].replace('-', '')}_{idx}"] = False
                                st.success("Bloque editado correctamente.")
                                st.rerun()
                            except Exception as e:
                                st.error(f"Error al guardar: {e}")
                        if st.button("❌ Cancelar", key=f"cancel_{info_user['uuid'].replace('-', '')}_{idx}"):
                            st.session_state[f"edit_mode_{info_user['uuid'].replace('-', '')}_{idx}"] = False
                            st.rerun()
            elif isinstance(user_info, dict):
                for k, v in user_info.items():
                    st.write(f"- **{k}:** {v}")
            else:
                st.code(str(user_info))

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

# Sección de ayuda
st.subheader("Ayuda")
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
