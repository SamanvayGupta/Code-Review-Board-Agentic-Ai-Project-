
"""Structured output produced by the Reviewer Manager."""

from typing import List

from pydantic import BaseModel, Field

from src.models.finding import Finding
from src.models.change_state import MergeRecommendation


class ReviewerOutput(BaseModel):
    """Consolidated result of the complete code review."""

    summary: str = Field(
        description="Overall summary of the code review."
    )

    findings: List[Finding] = Field(
        default_factory=list,
        description="Deduplicated and prioritized review findings.",
    )

    merge_recommendation: MergeRecommendation = Field(
        description=(
            "Final recommendation: APPROVE, REQUEST_CHANGES, "
            "or REVIEW_REQUIRED."
        )
    )

    recommendation_reason: str = Field(
        default="No recommendation reason was provided.",
        description="Explanation for the merge recommendation.",
    )
