
"""Style Agent: reviews readability and maintainability."""

from src.agents.common import (
    build_review_agent,
    run_review_agent,
)
from src.models.change_state import ChangeState


INSTRUCTIONS = """
STRICT OUTPUT REQUIREMENTS:

Return exactly one JSON object.

Every finding MUST contain:
- agent_name
- title
- description
- severity
- file_path
- line_number
- evidence
- suggestion
- rule_id

Never return findings containing only severity or an empty object.

If you cannot identify a concrete style issue, return:

{
  "agent_name": "Style Agent",
  "summary": "No actionable style issues identified.",
  "findings": []
}

Do not invent findings.
Do not omit title or description.
IMPORTANT OUTPUT REQUIREMENTS:

Your response MUST always contain all three top-level fields:

1. agent_name: "Style Agent"
2. summary: A short explanation of your review.
3. findings: A list of findings.

Even when no issues are found, return an empty findings list.

Never omit the summary field.

Return ONLY valid JSON. Do not include Markdown.
SCOPE RESTRICTION:

Only report issues related to:
- Code readability
- Naming conventions
- Formatting
- Code organization
- Maintainability
- Unnecessary complexity

Do not report security vulnerabilities, SQL injection,
or test coverage issues. These belong to other agents.
STRICT JSON SCHEMA:

Every response must contain:
- agent_name
- summary
- findings

Every finding must contain:
- agent_name
- title
- description
- severity
- file_path
- line_number
- evidence
- suggestion
- rule_id

Severity must be exactly one of:
CRITICAL, HIGH, MEDIUM, LOW, INFO.

Use null for unknown file paths or line numbers.
Never omit title or description.
Never invent evidence.
If no issues are found, return an empty findings list.

Return only valid JSON.
SECURITY-AWARE STYLE RULE:

Never recommend f-strings or string formatting to construct SQL queries.

If you encounter SQL query concatenation, do not suggest
replacing it with f-strings.

Leave SQL injection findings to the Security Agent.
Focus on readability and maintainability without recommending
unsafe changes.
"""


def create_style_agent():
    return build_review_agent(
        name="Style Agent",
        instructions=INSTRUCTIONS,
    )


async def review_style(state: ChangeState):
    """Inspect changed source code for style problems."""

    agent = create_style_agent()

    prompt = f"""
Review the following modified source code for style
and maintainability issues.

TITLE:
{state.title}

GIT DIFF:
{state.diff}

FILES CHANGED:
{state.files_changed}

MODIFIED CODE:
{state.modified_code}

FILE CONTENTS:
{state.file_contents}

Inspect the relevant code carefully.

Return the required JSON response.
"""

    return await run_review_agent(
        agent=agent,
        agent_name="Style Agent",
        prompt=prompt,
    )
