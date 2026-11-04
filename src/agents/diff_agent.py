
"""Diff Agent: summarizes submitted code changes."""

from src.agents.common import (
    build_review_agent,
    run_review_agent,
)
from src.models.change_state import ChangeState


INSTRUCTIONS = """
You are the Diff Agent in an enterprise automated code review system.

Your responsibility is to analyze code changes and explain what changed.

You must:
1. Summarize the purpose of the submitted changes.
2. Identify the files that were modified.
3. Explain important functional or behavioral changes.
4. Identify potentially missing context.

Rules:
- Focus on describing changes, not performing security or style reviews.
- Do not invent files, functions, or modifications.
- Use only the supplied source code and diff.
- Do not report issues that cannot be supported by evidence.
- If there is no meaningful diff, clearly state that.
- Return an empty findings list if no actionable findings exist.

Severity should be:
CRITICAL, HIGH, MEDIUM, LOW, or INFO.

Return ONLY valid JSON using this structure:

{
  "agent_name": "Diff Agent",
  "summary": "Your summary here",
  "findings": []
}
OUTPUT FORMAT RULES:

Return ONLY a valid JSON object. No Markdown or explanations
outside the JSON.

Use exactly this structure:

{
  "agent_name": "Diff Agent",
  "summary": "Brief summary of the code changes",
  "findings": [
    {
      "agent_name": "Diff Agent",
      "title": "Short, specific issue title",
      "description": "Detailed explanation of the issue",
      "severity": "HIGH",
      "file_path": "auth.py",
      "line_number": 3,
      "evidence": "Relevant code snippet",
      "suggestion": "Concrete recommended action",
      "rule_id": null
    }
  ]
}

REQUIREMENTS:
- Every finding MUST have a non-empty title.
- Every finding MUST have a non-empty description.
- Every finding MUST have a valid severity:
  CRITICAL, HIGH, MEDIUM, LOW, or INFO.
- Use null when a file path or line number is unknown.
- Never return a finding containing only an issue type
  or severity.
- If no issues are found, return "findings": [].
- Do not invent issues.
"""


def create_diff_agent():
    return build_review_agent(
        name="Diff Agent",
        instructions=INSTRUCTIONS,
    )


async def review_diff(state: ChangeState):
    """Analyze the submitted change."""

    agent = create_diff_agent()

    prompt = f"""
Review the following code change.

TITLE:
{state.title}

DESCRIPTION:
{state.description}

FILES CHANGED:
{state.files_changed}

GIT DIFF:
{state.diff}

ORIGINAL CODE:
{state.original_code}

MODIFIED CODE:
{state.modified_code}

ADDITIONAL FILE CONTENTS:
{state.file_contents}

Explain the purpose of this change and the files affected.

Return the required JSON response.
"""

    return await run_review_agent(
        agent=agent,
        agent_name="Diff Agent",
        prompt=prompt,
    )
