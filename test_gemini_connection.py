
"""Smoke test for the Gemini Agent Framework connection."""

import asyncio
import os

from dotenv import load_dotenv

from src.services.model_client import create_agent


async def main() -> None:
    load_dotenv()

    if not os.getenv("GOOGLE_API_KEY"):
        raise RuntimeError(
            "GOOGLE_API_KEY is missing. "
            "Add your Gemini API key to the project-root .env file."
        )

    agent = create_agent(
        name="ConnectionTestAgent",
        instructions=(
            "You are a concise Python code reviewer. "
            "Respond clearly and briefly."
        ),
    )

    prompt = """
    Review this Python function:

    def add(a, b):
        return a + b

    In two bullet points, explain what it does
    and whether you notice an obvious issue.
    """

    print("Sending a test request to Gemini...\n")

    result = await agent.run(prompt)

    print("Gemini response:")
    print(result.text)


if __name__ == "__main__":
    asyncio.run(main())
