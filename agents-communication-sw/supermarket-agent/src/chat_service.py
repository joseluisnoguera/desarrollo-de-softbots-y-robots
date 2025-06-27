"""
Chat service for handling conversation logic and tool execution.
"""
import streamlit as st
from typing import List
from langchain_core.messages import AIMessage, ToolMessage
import logging

from .utils import convert_args_to_int
from .exceptions import WholesalerAPIError

logger = logging.getLogger(__name__)


class ChatService:
    """Service for handling chat conversations and tool execution."""

    def __init__(self, agent):
        self.agent = agent

    async def get_agent_response(self) -> None:
        """
        Gets a final response from the agent, handling all intermediate tool calls.
        This function loops until a response without tool calls is received.
        It includes a workaround for an API issue where messages with empty content
        are rejected, by replacing empty content in tool-calling messages with a space.
        """
        history = list(st.session_state.messages)

        while True:
            response = await self.agent.generate_response(history)

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
            tool_results = await self._execute_tool_calls(response.tool_calls)
            history.extend(tool_results)

        # Update the session state with the complete conversation history.
        st.session_state.messages = history

    async def _execute_tool_calls(self, tool_calls: List) -> List[ToolMessage]:
        """Execute tool calls and return tool messages."""
        available_tools = {tool.name: tool for tool in self.agent.tools}
        tool_results = []

        for tool_call in tool_calls:
            tool_to_invoke = available_tools.get(tool_call["name"])
            if tool_to_invoke:
                try:
                    converted_args = convert_args_to_int(tool_call["args"])
                    tool_output = await tool_to_invoke.ainvoke(converted_args)
                    tool_output_str = (
                        str(tool_output)
                        if tool_output is not None and str(tool_output).strip() != ""
                        else "OK"
                    )
                    tool_results.append(
                        ToolMessage(
                            content=tool_output_str,
                            tool_call_id=tool_call["id"]
                        )
                    )
                except WholesalerAPIError as e:
                    logger.warning(
                        f"Wholesaler API error for tool {tool_call['name']}: {e}"
                    )
                    tool_results.append(
                        ToolMessage(
                            content=f"Servicio no disponible temporalmente: {str(e)}",
                            tool_call_id=tool_call["id"]
                        )
                    )
                except Exception as e:
                    logger.error(f"Error executing tool {tool_call['name']}: {e}")
                    tool_results.append(
                        ToolMessage(
                            content=f"Error ejecutando herramienta: {str(e)}",
                            tool_call_id=tool_call["id"]
                        )
                    )
            else:
                error_message = (
                    f"Error: Tool '{tool_call['name']}' was called but is not "
                    "available."
                )
                tool_results.append(
                    ToolMessage(
                        content=error_message,
                        tool_call_id=tool_call['id']
                    )
                )

        return tool_results
