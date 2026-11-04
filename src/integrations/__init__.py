"""GitHub integration package."""

from src.integrations.github_client import (
    GitHubClient,
    GitHubClientError,
)

__all__ = ["GitHubClient", "GitHubClientError"]