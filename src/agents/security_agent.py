
"""Security Agent: detects potentially unsafe code patterns."""

from src.agents.common import (
    build_review_agent,
    run_review_agent,
)
from src.models.change_state import ChangeState


INSTRUCTIONS = """
You are the Security Agent in an enterprise code review system.

Your responsibility is to identify security vulnerabilities
and unsafe coding patterns.

Check for:
1. Hardcoded credentials, passwords, and API keys.
2. SQL injection and unsafe database queries.
3. Command injection and unsafe shell execution.
4. Insecure deserialization.
5. Weak authentication or authorization.
6. Unsafe file handling and path traversal.
7. Exposure of sensitive information.

Rules:
- Prioritize exploitable and evidence-backed vulnerabilities.
- Never claim a secret is valid without verification.
- Do not repeat complete secret values in your findings.
- Do not invent vulnerabilities.
- Consider the surrounding code before reporting a problem.
- Include exact evidence, redacting sensitive values.
- Provide a line number only when reasonably certain.
- Do not report style problems.
- Return an empty findings list when no issues exist.

Severity guidance:
CRITICAL: Severe, directly exploitable vulnerabilities.
HIGH: Significant security vulnerabilities.
MEDIUM: Meaningful security weaknesses.
LOW: Minor security concerns.
INFO: Informational security observations.

Return ONLY valid JSON:

{
  "agent_name": "Security Agent",
  "summary": "Your security review summary",
  "findings": []
}
"""


def create_security_agent():
    return build_review_agent(
        name="Security Agent",
        instructions=INSTRUCTIONS,
    )


async def review_security(state: ChangeState):
    """Analyze the submitted change for security issues."""

    agent = create_security_agent()

    prompt = f"""
Perform a security review of the following code change.

TITLE:
{state.title}

DESCRIPTION:
{state.description}

GIT DIFF:
{state.diff}

FILES CHANGED:
{state.files_changed}

MODIFIED CODE:
{state.modified_code}

FILE CONTENTS:
{state.file_contents}

Inspect the supplied code for security vulnerabilities.

Do not assume that a vulnerability exists simply because
a particular coding pattern appears.

Return the required JSON response.
"""

    return await run_review_agent(
        agent=agent,
        agent_name="Security Agent",
        prompt=prompt,
    )
