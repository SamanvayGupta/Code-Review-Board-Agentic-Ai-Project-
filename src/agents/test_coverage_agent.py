
"""Test-Coverage Agent: evaluates tests for modified functionality."""

from src.agents.common import (
    build_review_agent,
    run_review_agent,
)
from src.models.change_state import ChangeState


INSTRUCTIONS = """
You are the Test-Coverage Agent in an enterprise code review system.

Your responsibility is to evaluate whether the submitted
code changes have adequate tests.

Check for:
1. Tests covering newly introduced functionality.
2. Tests covering modified behavior.
3. Missing edge cases.
4. Missing negative and error-path tests.
5. Whether available coverage reports indicate untested code.

Rules:
- Inspect the provided test files and source files.
- Do not assume that a test exists if it was not provided.
- Distinguish missing test evidence from confirmed missing tests.
- Never invent test execution results or coverage percentages.
- Do not claim that tests passed unless actual test results
  were supplied.
- Do not treat missing coverage reports as zero coverage.
- Recommend specific test cases when gaps are identified.
- Return an empty findings list if no actionable gaps exist.

Severity guidance:
HIGH: Important changed functionality has no adequate tests.
MEDIUM: Important edge cases or error paths are untested.
LOW: Minor test improvements.
INFO: Informational observations.

Return ONLY valid JSON:

{
  "agent_name": "Test-Coverage Agent",
  "summary": "Your testing review summary",
  "findings": []
}
"""


def create_test_coverage_agent():
    return build_review_agent(
        name="Test-Coverage Agent",
        instructions=INSTRUCTIONS,
    )


async def review_test_coverage(state: ChangeState):
    """Inspect available tests for the submitted code change."""

    agent = create_test_coverage_agent()

    prompt = f"""
Review the testing quality of the submitted code change.

TITLE:
{state.title}

DESCRIPTION:
{state.description}

FILES CHANGED:
{state.files_changed}

MODIFIED CODE:
{state.modified_code}

SOURCE FILES:
{state.file_contents}

AVAILABLE TEST FILES:
{state.test_files}

COVERAGE REPORT:
{state.coverage_report or "No coverage report was supplied."}

Evaluate whether the modified functionality is adequately tested.

Clearly distinguish between:
- Confirmed missing tests.
- Missing test evidence.
- Actual measured coverage information.

Return the required JSON response.
"""

    return await run_review_agent(
        agent=agent,
        agent_name="Test-Coverage Agent",
        prompt=prompt,
    )
