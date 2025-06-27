"""
Utility functions for the supermarket agent application.
"""
import asyncio
import streamlit as st
from typing import Any, Dict, List, Union


def setup_event_loop():
    """Set up persistent event loop for Streamlit session."""
    if "event_loop" not in st.session_state:
        st.session_state.event_loop = asyncio.new_event_loop()

    # Set the event loop for the current thread
    asyncio.set_event_loop(st.session_state.event_loop)


def run_async(func):
    """A helper to run async functions using the session's event loop."""
    loop = st.session_state.event_loop
    return loop.run_until_complete(func)


def convert_args_to_int(
    args: Union[Dict, List, float, Any]
) -> Union[Dict, List, int, Any]:
    """Recursively converts float values that are whole numbers to integers."""
    if isinstance(args, dict):
        return {k: convert_args_to_int(v) for k, v in args.items()}
    elif isinstance(args, list):
        return [convert_args_to_int(i) for i in args]
    elif isinstance(args, float) and args.is_integer():
        return int(args)
    return args


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
