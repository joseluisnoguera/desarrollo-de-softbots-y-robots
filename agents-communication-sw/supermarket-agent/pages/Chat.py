import streamlit as st
from src.gemini_agent import GeminiAgent
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
import asyncio
import nest_asyncio

# Apply nest_asyncio to allow nested event loops, which is crucial for gRPC/asyncio compatibility.
nest_asyncio.apply()

# --- Constantes ---
AGENT_NAME = "Supermercado"
AGENT_AVATAR = "🛒"

# --- Event Loop Management for Streamlit ---
# Get or create a persistent event loop for the user session
if "event_loop" not in st.session_state:
    st.session_state.event_loop = asyncio.new_event_loop()

# Set the event loop for the current thread
asyncio.set_event_loop(st.session_state.event_loop)

def run_async(func):
    """A helper to run async functions using the session's event loop."""
    loop = st.session_state.event_loop
    return loop.run_until_complete(func)

# --- Agent Initialization ---
if "agent" not in st.session_state:
    with st.spinner("Iniciando el agente y conectando con las herramientas..."):
        agent = GeminiAgent(
            AGENT_NAME,
            personality="un amigable y servicial agente de supermercado",
            stance=""
        )
        # Run the async initialization
        run_async(agent.initialize())
        st.session_state.agent = agent
        st.session_state.messages = []
        # Rerun to clear the spinner and show the chat interface
        st.rerun()


# --- UI: Título y Descripción ---
st.markdown("# Chat con el Agente")
st.write(
    "Esta página es para iniciar una conversación con el agente del supermercado."
)

def convert_args_to_int(args):
    """Recursively converts float values that are whole numbers to integers."""
    if isinstance(args, dict):
        return {k: convert_args_to_int(v) for k, v in args.items()}
    elif isinstance(args, list):
        return [convert_args_to_int(i) for i in args]
    elif isinstance(args, float) and args.is_integer():
        return int(args)
    return args

# --- Lógica de la Conversación ---
async def get_agent_response():
    """
    Gets a final response from the agent, handling all intermediate tool calls.
    This function loops until a response without tool calls is received.
    It includes a workaround for an API issue where messages with empty content
    are rejected, by replacing empty content in tool-calling messages with a space.
    """
    history = list(st.session_state.messages)

    while True:
        response = await st.session_state.agent.generate_response(history)

        # WORKAROUND: If the response has tool calls but empty content, the next
        # API call will fail. We create a new AIMessage with a single space
        # as content to prevent this error.
        if response.tool_calls and not response.content:
            response = AIMessage(
                content=" ",  # Use a space to avoid empty content error
                tool_calls=response.tool_calls,
                invalid_tool_calls=response.invalid_tool_calls,
                response_metadata=response.response_metadata,
                usage_metadata=response.usage_metadata,
                id=response.id,
                name=response.name,
            )

        history.append(response)

        # If there are no tool calls, we have the final answer.
        if not response.tool_calls:
            break

        # If there are tool calls, execute them and add results to history.
        available_tools = {tool.name: tool for tool in st.session_state.agent.tools}
        tool_results = []
        for tool_call in response.tool_calls:
            tool_to_invoke = available_tools.get(tool_call["name"])
            if tool_to_invoke:
                converted_args = convert_args_to_int(tool_call["args"])
                tool_output = await tool_to_invoke.ainvoke(converted_args)
                tool_output_str = str(tool_output) if tool_output is not None and str(tool_output).strip() != "" else "OK"
                tool_results.append(
                    ToolMessage(content=tool_output_str, tool_call_id=tool_call["id"])
                )
            else:
                error_message = f"Error: Tool '{tool_call['name']}' was called but is not available."
                tool_results.append(ToolMessage(content=error_message, tool_call_id=tool_call['id']))

        history.extend(tool_results)
        # The loop continues, sending the updated history to the agent.

    # Update the session state with the complete conversation history.
    st.session_state.messages = history


# --- Visualización del Chat ---
if "messages" in st.session_state:
    for message in st.session_state.messages:
        if isinstance(message, HumanMessage):
            with st.chat_message("user", avatar="🧑"):
                st.markdown(message.content)
        # Do not display AIMessages that are only placeholders for tool calls.
        elif isinstance(message, AIMessage) and message.content.strip():
            with st.chat_message(AGENT_NAME, avatar=AGENT_AVATAR):
                st.markdown(message.content)

# --- Entrada del Usuario ---
if prompt := st.chat_input("¿Qué te gustaría comprar?"):
    st.session_state.messages.append(HumanMessage(content=prompt))
    with st.chat_message("user", avatar="🧑"):
        st.markdown(prompt)

    with st.spinner("El agente está pensando..."):
        run_async(get_agent_response())
        st.rerun()
