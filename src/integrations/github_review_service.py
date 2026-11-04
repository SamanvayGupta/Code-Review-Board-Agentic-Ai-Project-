
"""Service connecting GitHub Pull Requests to the review orchestrator."""

import logging

from src.integrations.github_client import GitHubClient
from src.integrations.github_converter import (
    convert_pull_request_to_state,
)
from src.orchestration.review_orchestrator import run_parallel_reviews
from src.models.change_state import ChangeState

logger = logging.getLogger(__name__)


class GitHubReviewService:
    """Fetch GitHub Pull Requests and run automated code reviews."""

    def __init__(self, github_client: GitHubClient | None = None):
        self.github_client = github_client or GitHubClient()

    async def review_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> ChangeState:
        """Fetch a PR, retrieve source files, and run code review."""

        logger.info(
            "Starting GitHub review for %s/%s#%s",
            owner,
            repo,
            pull_number,
        )

        # Step 1: Fetch Pull Request details.
        pull_request = await self.github_client.get_pull_request(
            owner,
            repo,
            pull_number,
        )

        # Step 2: Fetch changed files.
        changed_files = await self.github_client.get_pull_request_files(
            owner,
            repo,
            pull_number,
        )

        # Step 3: Get the exact PR head commit.
        head_sha = pull_request.get("head", {}).get("sha")

        if not head_sha:
            raise ValueError(
                "Pull Request does not contain a valid head commit SHA."
            )

        # Step 4: Retrieve complete source files.
        file_contents = {}

        for file_data in changed_files:
            filename = file_data.get("filename")

            if not filename:
                continue

            # Deleted files are not present in the PR head commit.
            if file_data.get("status") == "removed":
                continue

            try:
                content = await self.github_client.get_file_content(
                    owner,
                    repo,
                    filename,
                    head_sha,
                )

                file_contents[filename] = content

            except Exception as exc:
                logger.warning(
                    "Could not retrieve source file %s: %s",
                    filename,
                    exc,
                )

        # Step 5: Convert GitHub data into ChangeState.
        state = convert_pull_request_to_state(
            pull_request,
            changed_files,
            file_contents=file_contents,
        )

        # Step 6: Run the existing review orchestrator.
        logger.info(
            "Starting automated review for PR #%s.",
            pull_number,
        )

        reviewed_state = await run_parallel_reviews(state)

        logger.info(
            "GitHub review completed for PR #%s.",
            pull_number,
        )

        return reviewed_state
