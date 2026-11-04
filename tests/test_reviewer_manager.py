
"""Tests for the Reviewer Manager output model."""

import pytest
from pydantic import ValidationError

from src.models.reviewer_output import ReviewerOutput
from src.models.change_state import MergeRecommendation


def test_reviewer_output_valid():
    """A valid reviewer output should be accepted."""

    output = ReviewerOutput(
        summary="Critical security issues were identified.",
        findings=[],
        merge_recommendation=MergeRecommendation.REQUEST_CHANGES,
        recommendation_reason="SQL injection vulnerability must be fixed.",
    )

    assert output.summary == "Critical security issues were identified."
    assert output.merge_recommendation == MergeRecommendation.REQUEST_CHANGES
    assert output.recommendation_reason


def test_reviewer_output_default_reason():
    """Recommendation reason should have a default value."""

    output = ReviewerOutput(
        summary="Review completed.",
        merge_recommendation=MergeRecommendation.APPROVE,
    )

    assert output.recommendation_reason == (
        "No recommendation reason was provided."
    )


def test_reviewer_output_rejects_invalid_recommendation():
    """Invalid merge recommendations should be rejected."""

    with pytest.raises(ValidationError):
        ReviewerOutput(
            summary="Review completed.",
            merge_recommendation="INVALID",
        )


def test_reviewer_output_default_findings():
    """Findings should default to an empty list."""

    output = ReviewerOutput(
        summary="No issues found.",
        merge_recommendation=MergeRecommendation.APPROVE,
    )

    assert output.findings == []
