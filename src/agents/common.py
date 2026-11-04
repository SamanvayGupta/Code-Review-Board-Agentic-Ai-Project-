
"""Common utilities used by all review agents."""

import json
import logging

from pydantic import ValidationError
from agent_framework.exceptions import ChatClientException

from src.models.agent_output import AgentReviewOutput
from src.services.model_client import create_agent

logger = logging.getLogger(__name__)


def build_review_agent(name: str, instructions: str):
    """Create a Gemini-powered review agent."""

    return create_agent(
        name=name,
        instructions=instructions,
    )


def extract_json(raw_text: str) -> dict:
    """Extract JSON from a plain or Markdown-formatted response."""

    raw_text = raw_text.strip()

    # Remove Markdown code fences if Gemini includes them.
    if raw_text.startswith("```"):
        lines = raw_text.splitlines()

        if lines[-1].strip() == "```":
            lines = lines[:-1]

        raw_text = "\n".join(lines[1:]).strip()

    # Parse JSON.
    data = json.loads(raw_text)

    if not isinstance(data, dict):
        raise ValueError("Agent response must be a JSON object.")
    
    
    return data



def normalize_findings(data: dict, agent_name: str) -> dict:
    """Normalize Gemini output while preserving strict validation."""

    if not isinstance(data, dict):
        raise ValueError("Agent response must be a JSON object.")

    # Do NOT overwrite the model's agent_name here.
    # run_review_agent must validate that it is correct.

    findings = data.get("findings")

    if not isinstance(findings, list):
        raise ValueError("'findings' must be a JSON list.")

    severity_aliases = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "MEDIUM": "MEDIUM",
        "MODERATE": "MEDIUM",
        "LOW": "LOW",
        "MINOR": "LOW",
        "INFO": "INFO",
        "INFORMATIONAL": "INFO",
    }

    for index, item in enumerate(findings):

        if not isinstance(item, dict):
            raise ValueError(
                f"Finding at index {index} must be a JSON object."
            )

        # Validate finding agent identity before normalization.
        finding_agent = item.get("agent_name")

        if finding_agent and finding_agent != agent_name:
            raise ValueError(
                f"Finding at index {index} has incorrect agent_name."
            )

        item["agent_name"] = agent_name

        # Normalize title.
        if not item.get("title"):
            item["title"] = (
                item.get("issue")
                or item.get("vulnerability")
                or item.get("problem")
            )

        # If the title is missing, use the first sentence of
        # the actual description as a concise title.
        if not item.get("title") and item.get("description"):
            item["title"] = item["description"].split(".")[0][:120]

        if not item.get("title"):
            raise ValueError(
                f"Finding at index {index} has no title."
            )

        if not item.get("description"):
            raise ValueError(
                f"Finding at index {index} has no description."
            )

        # Normalize line number.
        if item.get("line_number") is None:
            item["line_number"] = item.get("line")

        # Normalize file path.
        if item.get("file_path") is None:
            item["file_path"] = item.get("file")

        # Normalize suggestion.
        if not item.get("suggestion"):
            item["suggestion"] = (
                item.get("recommendation") or ""
            )

        # Normalize severity.
        severity = str(item.get("severity", "")).upper().strip()

        if severity not in severity_aliases:
            raise ValueError(
                f"Finding at index {index} has invalid severity: "
                f"{severity}"
            )

        item["severity"] = severity_aliases[severity]

        # Normalize evidence.
        if not item.get("evidence"):
            item["evidence"] = ""

    return data



async def run_review_agent(
    agent,
    agent_name: str,
    prompt: str,
) -> AgentReviewOutput:
    """Execute an agent and validate its JSON response."""

    try:
        logger.info("Starting %s...", agent_name)

        # Execute the Gemini-powered agent.
        response = await agent.run(prompt)

        if not response.text:
            raise ValueError("Agent returned an empty response.")

        # Extract and parse JSON.
        data = extract_json(response.text)
        logger.debug(
            "%s raw response:\n%s",
            agent_name,
            response.text,
        )

        # Normalize the AI-generated findings.
        data = normalize_findings(data, agent_name)

        # Validate the complete response.
        output = AgentReviewOutput.model_validate(data)

        # Validate agent identity.
        if output.agent_name != agent_name:
            raise ValueError(
                f"Expected {agent_name}, got {output.agent_name}"
            )

        # Ensure findings belong to the correct agent.
        for finding in output.findings:

            if finding.agent_name != agent_name:
                raise ValueError(
                    "Finding agent_name does not match its reviewer."
                )

        logger.info(
            "%s completed successfully with %d findings.",
            agent_name,
            len(output.findings),
        )

        return output

    except ChatClientException:
        logger.exception(
            "%s failed during Gemini execution.",
            agent_name,
        )
        raise

    except (
        json.JSONDecodeError,
        ValidationError,
        ValueError,
    ) as exc:

        logger.exception(
            "%s returned invalid output.",
            agent_name,
        )

        raise ValueError(
            f"{agent_name} produced an invalid review response: {exc}"
        ) from exc
