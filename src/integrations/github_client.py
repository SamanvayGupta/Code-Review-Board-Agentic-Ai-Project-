
"""Read-only GitHub API client for the Automated Code Review Board."""

import logging
import os
from typing import Any

import httpx
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"


class GitHubClientError(Exception):
    """Raised when a GitHub API operation fails."""


class GitHubClient:
    """Client for read-only GitHub API operations."""

    def __init__(self, token: str | None = None):
        self.token = token or os.getenv("GITHUB_TOKEN")

        if not self.token:
            raise GitHubClientError(
                "GITHUB_TOKEN is missing. Add it to your .env file."
            )

        self.headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": f"Bearer {self.token}",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
        }

        self.timeout = 30.0

    async def _get(self, endpoint: str) -> Any:
        """Send an authenticated GET request to GitHub."""

        url = f"{GITHUB_API_BASE}/{endpoint.lstrip('/')}"

        try:
            async with httpx.AsyncClient(
                headers=self.headers,
                timeout=self.timeout,
            ) as client:
                response = await client.get(url)

            if response.status_code == 401:
                raise GitHubClientError(
                    "GitHub authentication failed. Check your token."
                )

            if response.status_code == 403:
                raise GitHubClientError(
                    "GitHub access forbidden. Check token permissions "
                    "and API rate limits."
                )

            if response.status_code == 404:
                raise GitHubClientError(
                    "GitHub resource not found or access is unavailable."
                )

            response.raise_for_status()
            return response.json()

        except httpx.TimeoutException as exc:
            raise GitHubClientError(
                "GitHub API request timed out."
            ) from exc

        except httpx.HTTPStatusError as exc:
            logger.exception("GitHub API returned an HTTP error.")
            raise GitHubClientError(
                f"GitHub API request failed: HTTP {exc.response.status_code}"
            ) from exc

        except httpx.RequestError as exc:
            logger.exception("Could not connect to GitHub.")
            raise GitHubClientError(
                "Could not connect to the GitHub API."
            ) from exc

    async def test_connection(self) -> dict:
        """Verify the token by retrieving the authenticated user."""

        user = await self._get("user")

        return {
            "authenticated": True,
            "username": user.get("login"),
            "name": user.get("name"),
        }

    async def get_repository(self, owner: str, repo: str) -> dict:
        """Retrieve repository information."""

        if not owner.strip() or not repo.strip():
            raise ValueError("Owner and repository name are required.")

        return await self._get(f"repos/{owner}/{repo}")

    async def get_pull_request(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> dict:
        """Retrieve details of a specific Pull Request."""

        if not owner.strip() or not repo.strip():
            raise ValueError("Owner and repository name are required.")

        if pull_number < 1:
            raise ValueError("Pull Request number must be positive.")

        return await self._get(
            f"repos/{owner}/{repo}/pulls/{pull_number}"
        )

    async def get_pull_request_files(
        self,
        owner: str,
        repo: str,
        pull_number: int,
    ) -> list[dict]:
        """Retrieve all changed files in a Pull Request.

        GitHub paginates this endpoint at a maximum of 100 files
        per request. Continue until all pages have been retrieved.
        """

        if not owner.strip() or not repo.strip():
            raise ValueError("Owner and repository name are required.")

        if pull_number < 1:
            raise ValueError("Pull Request number must be positive.")

        all_files = []
        page = 1
        per_page = 100

        while True:
            endpoint = (
                f"repos/{owner}/{repo}/pulls/{pull_number}/files"
                f"?per_page={per_page}&page={page}"
            )

            files = await self._get(endpoint)

            if not isinstance(files, list):
                raise GitHubClientError(
                    "Unexpected response while retrieving PR files."
                )

            all_files.extend(files)

            if len(files) < per_page:
                break

            page += 1

        return all_files
    
    async def get_file_content(
        self,
        owner: str,
        repo: str,
        path: str,
        ref: str,
    ) -> str:
        """Retrieve and decode a file from a GitHub repository."""

        import base64

        if not owner.strip() or not repo.strip():
            raise ValueError("Owner and repository name are required.")

        if not path.strip():
            raise ValueError("File path is required.")

        if not ref.strip():
            raise ValueError("Git reference is required.")

        endpoint = (
            f"repos/{owner}/{repo}/contents/{path}"
            f"?ref={ref}"
        )

        file_data = await self._get(endpoint)

        if file_data.get("type") != "file":
            raise GitHubClientError(
                f"'{path}' is not a regular file."
            )

        encoded_content = file_data.get("content", "")
        encoding = file_data.get("encoding")

        if encoding != "base64":
            raise GitHubClientError(
                f"Unsupported encoding for file '{path}'."
            )

        try:
            decoded_content = base64.b64decode(
                encoded_content
            ).decode("utf-8")

        except (ValueError, UnicodeDecodeError) as exc:
            raise GitHubClientError(
                f"Could not decode file '{path}'."
            ) from exc

        return decoded_content
