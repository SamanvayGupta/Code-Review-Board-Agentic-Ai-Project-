
"""Tests for orchestrator failure handling."""

import pytest
from unittest.mock import AsyncMock

from src.orchestration import review_orchestrator
from src.models.change_state import (
    ChangeState,
    ReviewStatus,
    MergeRecommendation,
)
from src.models.agent_output import AgentReviewOutput
from src.models.reviewer_output import ReviewerOutput
from src.models.finding import Finding, Severity


def create_finding(finding_id, agent_name):
    """Create a sample finding for testing."""

    return Finding(
        id=finding_id,
        agent_name=agent_name,
        title="Test Security Issue",
        description="A sample issue for testing.",
        severity=Severity.HIGH,
    )


def create_agent_result(agent_name):
    """Create a successful specialist agent result."""

    return AgentReviewOutput(
        agent_name=agent_name,
        summary=f"{agent_name} completed successfully.",
        findings=[
            create_finding(f"{agent_name}-001", agent_name)
        ],
    )


@pytest.mark.asyncio
async def test_orchestrator_continues_when_one_agent_fails(monkeypatch):
    """Other agents should continue when one specialist fails."""

    monkeypatch.setattr(
        review_orchestrator,
        "review_diff",
        AsyncMock(side_effect=Exception("Diff Agent error")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_style",
        AsyncMock(return_value=create_agent_result("Style Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_security",
        AsyncMock(return_value=create_agent_result("Security Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_test_coverage",
        AsyncMock(return_value=create_agent_result("Test-Coverage Agent")),
    )

    reviewer_result = ReviewerOutput(
        summary="Review completed with findings.",
        findings=[
            create_finding("consolidated-001", "Reviewer Manager")
        ],
        merge_recommendation=MergeRecommendation.REQUEST_CHANGES,
        recommendation_reason="Issues require correction.",
    )

    reviewer_mock = AsyncMock(return_value=reviewer_result)

    monkeypatch.setattr(
        review_orchestrator,
        "run_reviewer_manager",
        reviewer_mock,
    )

    state = ChangeState()

    result = await review_orchestrator.run_parallel_reviews(state)

    assert result.status == ReviewStatus.FAILED
    assert len(result.errors) == 1
    assert "Diff Agent failed" in result.errors[0]

    # The Reviewer Manager should still run.
    reviewer_mock.assert_awaited_once()

    # The final recommendation should be preserved.
    assert result.merge_recommendation == MergeRecommendation.REQUEST_CHANGES

    # The consolidated finding should be preserved.
    assert len(result.findings) == 1


@pytest.mark.asyncio
async def test_orchestrator_skips_reviewer_if_all_agents_fail(monkeypatch):
    """Reviewer Manager should not run if all specialists fail."""

    failed_agent = AsyncMock(
        side_effect=Exception("Agent unavailable")
    )

    monkeypatch.setattr(review_orchestrator, "review_diff", failed_agent)
    monkeypatch.setattr(review_orchestrator, "review_style", failed_agent)
    monkeypatch.setattr(review_orchestrator, "review_security", failed_agent)
    monkeypatch.setattr(
        review_orchestrator,
        "review_test_coverage",
        failed_agent,
    )

    reviewer_mock = AsyncMock()

    monkeypatch.setattr(
        review_orchestrator,
        "run_reviewer_manager",
        reviewer_mock,
    )

    state = ChangeState()

    result = await review_orchestrator.run_parallel_reviews(state)

    assert result.status == ReviewStatus.FAILED
    assert len(result.errors) == 4
    assert result.merge_recommendation == MergeRecommendation.REVIEW_REQUIRED

    # No specialist succeeded, so Reviewer Manager must be skipped.
    reviewer_mock.assert_not_awaited()


@pytest.mark.asyncio
async def test_orchestrator_handles_reviewer_manager_failure(monkeypatch):
    """Specialist findings should survive manager failure."""

    monkeypatch.setattr(
        review_orchestrator,
        "review_diff",
        AsyncMock(return_value=create_agent_result("Diff Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_style",
        AsyncMock(return_value=create_agent_result("Style Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_security",
        AsyncMock(return_value=create_agent_result("Security Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_test_coverage",
        AsyncMock(return_value=create_agent_result("Test-Coverage Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "run_reviewer_manager",
        AsyncMock(side_effect=Exception("Manager unavailable")),
    )

    state = ChangeState()

    result = await review_orchestrator.run_parallel_reviews(state)

    assert result.status == ReviewStatus.FAILED
    assert len(result.findings) == 4
    assert result.merge_recommendation == MergeRecommendation.REVIEW_REQUIRED
    assert any("Reviewer Manager failed" in error for error in result.errors)
    assert result.review_summary != ""


@pytest.mark.asyncio
async def test_orchestrator_completes_when_everything_succeeds(monkeypatch):
    """A fully successful review should be marked COMPLETED."""

    monkeypatch.setattr(
        review_orchestrator,
        "review_diff",
        AsyncMock(return_value=create_agent_result("Diff Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_style",
        AsyncMock(return_value=create_agent_result("Style Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_security",
        AsyncMock(return_value=create_agent_result("Security Agent")),
    )

    monkeypatch.setattr(
        review_orchestrator,
        "review_test_coverage",
        AsyncMock(return_value=create_agent_result("Test-Coverage Agent")),
    )

    reviewer_result = ReviewerOutput(
        summary="All checks completed.",
        findings=[],
        merge_recommendation=MergeRecommendation.APPROVE,
        recommendation_reason="No blocking issues found.",
    )

    monkeypatch.setattr(
        review_orchestrator,
        "run_reviewer_manager",
        AsyncMock(return_value=reviewer_result),
    )

    state = ChangeState()

    result = await review_orchestrator.run_parallel_reviews(state)

    assert result.status == ReviewStatus.COMPLETED
    assert result.errors == []
    assert result.merge_recommendation == MergeRecommendation.APPROVE
    assert result.review_summary == "All checks completed."
