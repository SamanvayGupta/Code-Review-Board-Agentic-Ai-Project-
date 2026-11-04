
"""Shared Gemini-backed Microsoft Agent Framework client."""

import truststore

# Use the operating system's trusted certificate store.
# This must run before importing networking/model libraries.
truststore.inject_into_ssl()

from dotenv import load_dotenv

from agent_framework import Agent
from agent_framework.gemini import GeminiChatClient

load_dotenv()


def create_agent(name: str, instructions: str) -> Agent:
    """Create an agent using the configured Gemini model."""

    client = GeminiChatClient()

    return Agent(
        client=client,
        name=name,
        instructions=instructions,
    )
