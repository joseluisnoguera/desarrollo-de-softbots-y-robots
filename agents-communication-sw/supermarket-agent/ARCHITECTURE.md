# Supermarket Agent - Refactored Architecture

## Overview

This project has been refactored to follow best practices for Python development, including proper separation of concerns, modular design, and comprehensive error handling.

## Project Structure

```
src/
├── __init__.py              # Package initialization and logging setup
├── models.py                # Pydantic data models and schemas
├── config.py                # Configuration constants and settings
├── exceptions.py            # Custom exception classes
├── tools.py                 # LangChain tools and external API calls
├── utils.py                 # Utility functions
├── ui_components.py         # Streamlit UI components
├── chat_service.py          # Chat conversation logic
└── gemini_agent.py          # Main agent implementation

pages/
├── Chat.py                  # Main chat interface (refactored)
└── Home.py                  # Landing page

tests/                       # Unit tests (to be implemented)
requirements.txt             # Python dependencies
Makefile                     # Build and development commands
```

## Key Improvements

### 1. Separation of Concerns

- **Models** (`models.py`): All data structures and configuration models
- **Configuration** (`config.py`): Constants, settings, and system prompts
- **Tools** (`tools.py`): External API integrations and LangChain tools
- **UI Components** (`ui_components.py`): Reusable Streamlit components
- **Chat Service** (`chat_service.py`): Business logic for conversation handling
- **Agent** (`gemini_agent.py`): Core agent implementation

### 2. Error Handling

- Custom exception hierarchy for different error types
- Graceful fallback when MCP server is unavailable
- Proper logging and error propagation
- User-friendly error messages in Spanish

### 3. Type Safety

- Full type hints throughout the codebase
- Pydantic models for data validation
- Proper return type annotations

### 4. Code Quality

- All code passes lint checks (ruff)
- Consistent code formatting
- Comprehensive docstrings
- Modular design for easy testing

## Usage

### Running the Application

```bash
# Install dependencies
pip install -r requirements.txt

# Run the Streamlit app
streamlit run Home.py

# Or run linting
make lint
```

### Agent Configuration

The agent can be configured using the `AgentConfig` model:

```python
from src.models import AgentConfig
from src.gemini_agent import GeminiAgent

config = AgentConfig(
    name="SuperMarket AI",
    personality="helpful and friendly",
    model_name="gemini-2.5-flash",
    temperature=0.7
)

agent = GeminiAgent(config)
await agent.initialize()
```

### Error Handling

The application includes comprehensive error handling:

- `MCPConnectionError`: When MCP server connection fails
- `ToolExecutionError`: When tool execution fails
- `WholesalerAPIError`: When wholesaler API calls fail
- `AgentInitializationError`: When agent setup fails

## Development Guidelines

### Adding New Tools

1. Define the tool in `src/tools.py`
2. Add proper type hints and error handling
3. Include comprehensive docstrings
4. Handle API failures gracefully

### Adding New UI Components

1. Create reusable components in `src/ui_components.py`
2. Follow Streamlit best practices
3. Keep components focused on presentation only

### Configuration Changes

1. Add new constants to `src/config.py`
2. Use environment variables for sensitive data
3. Update the `AgentConfig` model if needed

## Testing

Unit tests should be added to the `tests/` directory following pytest conventions:

```bash
# Run tests (when implemented)
pytest tests/

# Run with coverage
pytest --cov=src tests/
```

## Best Practices Implemented

1. **Single Responsibility Principle**: Each module has a clear, focused purpose
2. **Dependency Injection**: Configuration and dependencies are injected
3. **Error Handling**: Comprehensive exception handling with proper logging
4. **Type Safety**: Full type hints and Pydantic validation
5. **Documentation**: Clear docstrings and README documentation
6. **Code Quality**: Consistent formatting and lint-free code
7. **Modularity**: Easy to test, extend, and maintain

## Future Improvements

1. Add comprehensive unit tests
2. Implement configuration management (environment variables)
3. Add metrics and monitoring
4. Implement caching for API calls
5. Add support for multiple languages
6. Implement rate limiting for API calls
