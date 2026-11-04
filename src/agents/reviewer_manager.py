
"""Reviewer Manager: consolidates and prioritizes code review findings."""

import json
import logging
import re
from src.models.change_state import ChangeState
from src.models.reviewer_output import ReviewerOutput
from src.services.model_client import create_agent

logger = logging.getLogger(__name__)



REVIEWER_INSTRUCTIONS = """
You are the Reviewer Manager in an automated code review system.

You receive findings from four specialized agents:
1. Diff Agent
2. Style Agent
3. Security Agent
4. Test-Coverage Agent

Your responsibilities:

1. Review every submitted finding.
2. Identify duplicates referring to the same underlying issue.
3. Merge duplicate findings into one finding.
4. Preserve the highest severity when merging duplicates.
5. Preserve useful evidence, file paths, line numbers, and suggestions.
6. Retain distinct issues even if they occur in the same function.
7. Sort findings by severity:
   CRITICAL, HIGH, MEDIUM, LOW, INFO.
8. Produce a concise overall review summary.
9. ALWAYS provide recommendation_reason explaining the decision.

Merge recommendation rules:

- REQUEST_CHANGES:
  At least one CRITICAL or HIGH finding exists.

- REVIEW_REQUIRED:
  No CRITICAL or HIGH findings exist, but MEDIUM findings
  or important unresolved uncertainties remain.

- APPROVE:
  No unresolved security, correctness, or significant
  quality issues remain.

Important:
- Never invent findings.
- Never silently discard important information.
- Use only the supplied review data.
- Return valid structured output matching ReviewerOutput.
- Include ALL required fields:
  summary, findings, merge_recommendation,
  recommendation_reason.
"""



reviewer_agent = create_agent(
    name="Reviewer Manager",
    instructions=REVIEWER_INSTRUCTIONS,
)



async def run_reviewer_manager(state: ChangeState) -> ReviewerOutput:
    """Consolidate findings and recommend a merge decision."""

    findings_data = [
        finding.model_dump(mode="json")
        for finding in state.findings
    ]

    review_input = {
        "change_title": state.title,
        "change_description": state.description,
        "findings": findings_data,
    }

    logger.info(
        "Reviewer Manager processing %d findings.",
        len(state.findings),
    )

    response = await reviewer_agent.run(
        json.dumps(review_input, indent=2)
    )

    if not response or not response.text:
        raise ValueError("Reviewer Manager returned an empty response.")

    raw_output = response.text.strip()

    # Remove Markdown JSON code fences if Gemini adds them.
    raw_output = re.sub(
        r"^```(?:json)?\s*",
        "",
        raw_output,
        flags=re.IGNORECASE,
    )
    raw_output = re.sub(r"\s*```$", "", raw_output)

    try:
        result = ReviewerOutput.model_validate_json(raw_output)

    except Exception as exc:
        logger.exception("Failed to validate Reviewer Manager output.")

        logger.error(
            "Reviewer Manager raw response: %s",
            raw_output,
        )

        raise ValueError(
            "Reviewer Manager returned invalid structured output."
        ) from exc

    logger.info(
        "Reviewer Manager completed with %d consolidated findings.",
        len(result.findings),
    )

    return result
