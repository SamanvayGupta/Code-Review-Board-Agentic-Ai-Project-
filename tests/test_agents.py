
"""Tests for common review-agent functionality."""

import asyncio
from types import SimpleNamespace

import pytest

from src.agents.common import run_review_agent


class FakeAgent:
    """Simulates a Gemini agent without making API calls."""

    def __init__(self, response_text):
        self.response_text = response_text

    async def run(self, prompt):
        return SimpleNamespace(text=self.response_text)


def test_valid_agent_response():
    fake = FakeAgent("""
    {
        "agent_name": "Security Agent",
        "summary": "One security issue found.",
        "findings": [
            {
                "agent_name": "Security Agent",
                "title": "Possible SQL injection",
                "description": "Unsafe SQL construction.",
                "severity": "HIGH",
                "file_path": "database.py",
                "line_number": 10,
                "evidence": "query = user_input",
                "suggestion": "Use parameterized queries."
            }
        ]
    }
    """)

    result = asyncio.run(
        run_review_agent(
            fake,
            "Security Agent",
            "Review this code."
        )
    )

    assert result.agent_name == "Security Agent"
    assert len(result.findings) == 1
    assert result.findings[0].severity == "HIGH"


def test_empty_findings_response():
    fake = FakeAgent("""
    {
        "agent_name": "Style Agent",
        "summary": "No actionable issues identified.",
        "findings": []
    }
    """)

    result = asyncio.run(
        run_review_agent(
            fake,
            "Style Agent",
            "Review this code."
        )
    )

    assert result.findings == []


def test_invalid_json_response():
    fake = FakeAgent("This is not valid JSON.")

    with pytest.raises(ValueError):
        asyncio.run(
            run_review_agent(
                fake,
                "Security Agent",
                "Review this code."
            )
        )


def test_wrong_agent_name():
    fake = FakeAgent("""
    {
        "agent_name": "Style Agent",
        "summary": "Review completed.",
        "findings": []
    }
    """)

    with pytest.raises(ValueError):
        asyncio.run(
            run_review_agent(
                fake,
                "Security Agent",
                "Review this code."
            )
        )


def test_invalid_finding_severity():
    fake = FakeAgent("""
    {
        "agent_name": "Security Agent",
        "summary": "Review completed.",
        "findings": [
            {
                "agent_name": "Security Agent",
                "title": "Bad severity",
                "description": "Invalid severity value.",
                "severity": "EXTREME"
            }
        ]
    }
    """)

    with pytest.raises(ValueError):
        asyncio.run(
            run_review_agent(
                fake,
                "Security Agent",
                "Review this code."
            )
        )
