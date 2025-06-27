# Journalists Discussions

Una aplicación avanzada de discusión entre agentes de IA que actúan como periodistas, construida con tecnologías modernas y siguiendo las mejores prácticas de desarrollo de Python.

## 🚀 Características

- **Interfaz web interactiva** con Streamlit
- **Generación automática de temas** y posturas opuestas
- **Conversaciones dinámicas** entre agentes IA
- **Personalidades configurables** para cada agente
- **Historial de chat persistente** por sesión
- **Arquitectura modular** y extensible
- **Manejo de errores robusto** y logging
- **Testing automatizado** y calidad de código

## 🛠️ Tecnologías Utilizadas

- **Python 3.10+**: Lenguaje de programación principal
- **Streamlit**: Framework para la interfaz web
- **LangChain**: Framework para integración con LLMs
- **Google Gemini**: Modelo de IA para generación de respuestas
- **Pydantic**: Validación y serialización de datos
- **Ruff**: Linting y formateo de código
- **Pytest**: Framework de testing
- **MyPy**: Verificación de tipos estáticos

## 🏗️ Arquitectura del Proyecto

```
agents-communication-journalists/
├── src/                          # Código fuente principal
│   ├── __init__.py              # Inicialización del paquete
│   ├── config.py                # Configuración y constantes
│   ├── models.py                # Modelos de datos Pydantic
│   ├── exceptions.py            # Excepciones personalizadas
│   ├── utils.py                 # Funciones utilitarias
│   ├── gemini_agent.py          # Agentes Gemini
│   ├── conversation_service.py  # Servicio de conversación
│   └── ui_components.py         # Componentes de interfaz
├── pages/                       # Páginas de Streamlit
│   ├── Conversation.py          # Página de conversación
│   └── Topics.py                # Página de generación de temas
├── tests/                       # Tests automatizados
│   ├── __init__.py
│   ├── conftest.py              # Configuración de tests
│   └── test_utils.py            # Tests de utilidades
├── .streamlit/                  # Configuración de Streamlit
│   └── secrets.toml             # Claves de API (no versionado)
├── Home.py                      # Página principal
├── requirements.txt             # Dependencias Python
├── pyproject.toml              # Configuración de herramientas
├── Makefile                    # Comandos de desarrollo
├── .gitignore                  # Archivos ignorados por Git
└── README.md                   # Este archivo
```

## 📦 Instalación y Configuración

### Prerrequisitos

- Python 3.10 o superior
- pip (gestor de paquetes de Python)
- Git (para clonar el repositorio)

### Instalación Rápida

1. **Clona el repositorio:**
   ```bash
   git clone <repository-url>
   cd agents-communication-journalists
   ```

2. **Configura el entorno de desarrollo:**
   ```bash
   make dev
   ```

3. **Configura tu clave de API de Google Gemini:**
   ```bash
   mkdir -p .streamlit
   echo 'GOOGLE_API_KEY = "tu_clave_api_aqui"' > .streamlit/secrets.toml
   ```

4. **Ejecuta la aplicación:**
   ```bash
   make local
   ```

### Instalación Manual

1. **Crear entorno virtual:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # En Linux/Mac
   # o
   venv\Scripts\activate     # En Windows
   ```

2. **Instalar dependencias:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar clave de API:**
   - Crea el archivo `.streamlit/secrets.toml`
   - Añade tu clave de API de Google Gemini:
     ```toml
     GOOGLE_API_KEY = "tu_clave_api_aqui"
     ```

4. **Ejecutar la aplicación:**
   ```bash
   streamlit run Home.py --server.port=8502 --server.address=0.0.0.0
   ```

## 🎮 Uso de la Aplicación

### 1. Página de Inicio
- Información general de la aplicación
- Navegación a las diferentes funcionalidades

### 2. Generación de Temas (`/Topics`)
- **Input**: Ingresa un tema libre en el campo de texto
- **Proceso**: Un agente IA procesa el tema y genera:
  - Versión mejorada del tema para debate
  - Dos posturas opuestas bien definidas
- **Output**: Visualización de resultados en campos no editables
- **Acción**: Botón para guardar el tema y posturas para la conversación

### 3. Conversación (`/Conversation`)

#### Configuración (Barra Lateral)
- **Tema de discusión**: Campo de texto para el tema
- **Turnos por interacción**: Slider (1-10 mensajes)
- **Configuración Agente 1**:
  - Personalidad (campo libre)
  - Postura sobre el tema
- **Configuración Agente 2**:
  - Personalidad (campo libre)
  - Postura sobre el tema

#### Funcionalidad
- **Iniciar Conversación**: Requiere tema y posturas definidas
- **Chat Dinámico**: Visualización de mensajes con avatares
- **Continuar Conversación**: Genera nuevos turnos de diálogo
- **Persistencia**: El historial se mantiene durante la sesión

## 🧪 Desarrollo y Testing

### Comandos de Desarrollo

```bash
# Ver todos los comandos disponibles
make help

# Configurar entorno de desarrollo
make dev

# Ejecutar la aplicación
make local

# Ejecutar tests
make test

# Tests con cobertura
make test-cov

# Linting y formateo
make lint
make format

# Verificación de tipos
make type-check

# Ejecutar todas las verificaciones de calidad
make quality

# Limpiar archivos generados
make clean
```

### Estructura de Testing

- **Unit Tests**: Tests para funciones individuales
- **Integration Tests**: Tests para componentes completos
- **Mocking**: Simulación de APIs externas y Streamlit
- **Coverage**: Reporte de cobertura de código

### Herramientas de Calidad

- **Ruff**: Linting rápido y moderno
- **Black**: Formateo automático de código
- **isort**: Organización de imports
- **MyPy**: Verificación de tipos estáticos
- **Pytest**: Framework de testing robusto

## 🔧 Configuración Avanzada

### Variables de Entorno
```bash
# .streamlit/secrets.toml
GOOGLE_API_KEY = "tu_clave_gemini"

# Opcional: configuración adicional
MODEL_NAME = "gemini-1.5-flash"
TEMPERATURE = 0.7
MAX_MESSAGE_COUNT = 10
```

### Personalización de Agentes
- Modifica `src/config.py` para cambiar nombres y avatares por defecto
- Ajusta `src/gemini_agent.py` para personalizar prompts
- Extiende `src/models.py` para nuevos tipos de datos

## 🐛 Troubleshooting

### Problemas Comunes

1. **Error "ModuleNotFoundError"**:
   ```bash
   # Asegúrate de que el entorno virtual esté activado
   source venv/bin/activate
   make install
   ```

2. **Error de API Key**:
   ```bash
   # Verifica que el archivo secrets.toml existe y tiene la clave correcta
   cat .streamlit/secrets.toml
   ```

3. **Puerto ocupado**:
   ```bash
   # Cambia el puerto en el Makefile o usa directamente
   streamlit run Home.py --server.port=8503
   ```

4. **Errores de importación**:
   ```bash
   # Reinstala las dependencias
   pip install -r requirements.txt --force-reinstall
   ```

### Logging y Debugging

- Los logs se muestran en la consola durante la ejecución
- Nivel de logging configurable en `src/utils.py`
- Usa las herramientas de debugging de Streamlit: `st.write()`, `st.json()`

## 🚀 Despliegue

### Streamlit Cloud
1. Sube el código a GitHub
2. Conecta tu repositorio en [share.streamlit.io](https://share.streamlit.io)
3. Configura los secrets en la interfaz web

### Docker (Opcional)
```bash
# Construir imagen
make docker-build

# Ejecutar contenedor
make docker-run
```

## 🤝 Contribución

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/nueva-funcionalidad`)
3. Ejecuta las verificaciones de calidad (`make quality`)
4. Commit tus cambios (`git commit -am 'Añade nueva funcionalidad'`)
5. Push a la rama (`git push origin feature/nueva-funcionalidad`)
6. Crea un Pull Request

### Estándares de Código

- Seguir PEP 8 (verificado automáticamente con Ruff)
- Documentar funciones con docstrings
- Añadir tests para nuevas funcionalidades
- Manejar errores apropiadamente
- Usar type hints cuando sea posible

## 📄 Licencia

Este proyecto está bajo la licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 🙏 Agradecimientos

- **Google Gemini**: Por proporcionar las capacidades de IA
- **LangChain**: Por el framework de integración con LLMs
- **Streamlit**: Por la plataforma de aplicaciones web
- **Comunidad Python**: Por las excelentes herramientas de desarrollo

## 📞 Soporte

Para reportar bugs o solicitar nuevas funcionalidades, por favor:
1. Revisa los issues existentes en GitHub
2. Crea un nuevo issue con detalles específicos
3. Incluye información del entorno y pasos para reproducir

---

**¡Disfruta creando discusiones fascinantes entre agentes periodistas! 🎉**