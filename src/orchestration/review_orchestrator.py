
"""Orchestrates code review agents and the Reviewer Manager."""

import logging

from src.agents import (
    review_diff,
    review_style,
    review_security,
    review_test_coverage,
    run_reviewer_manager,
)
from src.models.change_state import (
    ChangeState,
    ReviewStatus,
    MergeRecommendation,
)

logger = logging.getLogger(__name__)


async def run_parallel_reviews(state: ChangeState) -> ChangeState:
    """
    Run the four specialist agents sequentially, then consolidate
    their findings using the Reviewer Manager.

    Sequential execution is retained temporarily for SSL diagnostics.
    """

    state.status = ReviewStatus.IN_PROGRESS
    state.errors.clear()

    agents = [
        ("Diff Agent", review_diff),
        ("Style Agent", review_style),
        ("Security Agent", review_security),
        ("Test-Coverage Agent", review_test_coverage),
    ]

    successful_agents = []
    failed_agents = []
    summaries = []

    logger.info(
        "Starting review with %d specialist agents.",
        len(agents),
    )

    # Step 1: Run the four specialist agents.
    for agent_name, agent_function in agents:
        logger.info("Starting %s...", agent_name)

        try:
            result = await agent_function(state)

            successful_agents.append(agent_name)
            summaries.append(f"{agent_name}: {result.summary}")

            for finding in result.findings:
                state.add_finding(finding)

            logger.info(
                "%s completed with %d findings.",
                agent_name,
                len(result.findings),
            )

        except Exception as exc:
            failed_agents.append(agent_name)
            state.errors.append(f"{agent_name} failed: {exc}")
            logger.exception("%s failed during review.", agent_name)

    # Step 2: Run the Reviewer Manager if at least one
    # specialist agent completed successfully.
    if successful_agents:
        logger.info("Starting Reviewer Manager...")

        try:
            reviewer_result = await run_reviewer_manager(state)

            # Replace the original findings with the consolidated list.
            state.findings = reviewer_result.findings

            # Save the final recommendation.
            state.merge_recommendation = (
                reviewer_result.merge_recommendation
            )

            # Save the overall review summary.
            state.review_summary = reviewer_result.summary

            logger.info(
                "Reviewer Manager completed with %d consolidated findings.",
                len(reviewer_result.findings),
            )

            logger.info(
                "Merge recommendation: %s",
                state.merge_recommendation.value,
            )

        except Exception as exc:
            state.errors.append(f"Reviewer Manager failed: {exc}")
            state.merge_recommendation = (
                MergeRecommendation.REVIEW_REQUIRED
            )

            # Preserve all specialist findings if consolidation fails.
            state.review_summary = "\n".join(summaries)

            logger.exception("Reviewer Manager failed.")

            failed_agents.append("Reviewer Manager")

    else:
        state.review_summary = "No specialist agents completed successfully."
        state.merge_recommendation = (
            MergeRecommendation.REVIEW_REQUIRED
        )

    # Step 3: Set the final review status.
    if failed_agents:
        state.status = ReviewStatus.FAILED
    else:
        state.status = ReviewStatus.COMPLETED

    logger.info(
        "Review finished: %d/%d specialist agents succeeded.",
        len(successful_agents),
        len(agents),
    )

    if failed_agents:
        logger.warning(
            "Failed components: %s",
            ", ".join(failed_agents),
        )

    return state
