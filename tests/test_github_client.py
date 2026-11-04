
"""Tests for GitHub client initialization."""
from unittest.mock import AsyncMock
import pytest

from src.integrations.github_client import (
    GitHubClient,
    GitHubClientError,
)


def test_client_rejects_missing_token(monkeypatch):
    """Client should reject missing credentials."""

    monkeypatch.delenv("GITHUB_TOKEN", raising=False)

    with pytest.raises(GitHubClientError, match="GITHUB_TOKEN is missing"):
        GitHubClient()


def test_client_accepts_token():
    """Client should initialize with a supplied token."""

    client = GitHubClient(token="test-token")

    assert client.token == "test-token"
    assert client.headers["Authorization"] == "Bearer test-token"
    assert client.timeout == 30.0


import asyncio
from src.integrations.github_client import GitHubClient


async def check_repository_access():
    client = GitHubClient()

    result = await client._get(
        "repos/SamanvayGupta/Code-Review-Board-Agentic-Ai-Project-"
    )

    print("Repository access successful!")
    print("Repository:", result["full_name"])
    print("Private:", result["private"])
    print("Default branch:", result["default_branch"])


if __name__ == "__main__":
    asyncio.run(check_repository_access())


import pytest



@pytest.mark.asyncio
async def test_get_repository():
    """Repository details should be retrieved correctly."""

    client = GitHubClient(token="test-token")

    expected = {
        "full_name": "SamanvayGupta/Code-Review-Board-Agentic-Ai-Project-",
        "private": False,
        "default_branch": "main",
    }

    client._get = AsyncMock(return_value=expected)

    result = await client.get_repository(
        "SamanvayGupta",
        "Code-Review-Board-Agentic-Ai-Project-",
    )

    assert result["full_name"] == expected["full_name"]
    assert result["private"] is False
    assert result["default_branch"] == "main"


@pytest.mark.asyncio
async def test_get_pull_request():
    """Pull Request details should be retrieved correctly."""

    client = GitHubClient(token="test-token")

    expected = {
        "number": 1,
        "title": "Add authentication",
        "state": "open",
    }

    client._get = AsyncMock(return_value=expected)

    result = await client.get_pull_request(
        "SamanvayGupta",
        "Code-Review-Board-Agentic-Ai-Project-",
        1,
    )

    assert result["number"] == 1
    assert result["title"] == "Add authentication"
    assert result["state"] == "open"


@pytest.mark.asyncio
async def test_get_pull_request_rejects_invalid_number():
    """Invalid Pull Request numbers should be rejected."""

    client = GitHubClient(token="test-token")

    with pytest.raises(ValueError):
        await client.get_pull_request("owner", "repo", 0)

@pytest.mark.asyncio
async def test_get_pull_request_files():
    """Changed files should be retrieved correctly."""

    client = GitHubClient(token="test-token")

    expected_files = [
        {
            "filename": "src/auth.py",
            "status": "modified",
            "additions": 5,
            "deletions": 2,
            "changes": 7,
            "patch": "@@ -1,2 +1,5 @@",
        },
        {
            "filename": "tests/test_auth.py",
            "status": "added",
            "additions": 20,
            "deletions": 0,
            "changes": 20,
            "patch": "@@ -0,0 +1,20 @@",
        },
    ]

    client._get = AsyncMock(return_value=expected_files)

    result = await client.get_pull_request_files(
        "SamanvayGupta",
        "Code-Review-Board-Agentic-Ai-Project-",
        1,
    )

    assert len(result) == 2
    assert result[0]["filename"] == "src/auth.py"
    assert result[1]["status"] == "added"


@pytest.mark.asyncio
async def test_get_pull_request_files_invalid_number():
    """Invalid PR numbers should be rejected."""

    client = GitHubClient(token="test-token")

    with pytest.raises(ValueError):
        await client.get_pull_request_files("owner", "repo", 0)


@pytest.mark.asyncio
async def test_get_pull_request_files_pagination():
    """The client should retrieve multiple pages of changed files."""

    client = GitHubClient(token="test-token")

    first_page = [
        {"filename": f"file_{i}.py", "status": "modified"}
        for i in range(100)
    ]

    second_page = [
        {"filename": "extra_file.py", "status": "added"}
    ]

    client._get = AsyncMock(
        side_effect=[first_page, second_page]
    )

    result = await client.get_pull_request_files(
        "owner",
        "repo",
        1,
    )

    assert len(result) == 101
    assert result[-1]["filename"] == "extra_file.py"
    assert client._get.await_count == 2


import base64


@pytest.mark.asyncio
async def test_get_file_content():
    """File content should be decoded from Base64."""

    client = GitHubClient(token="test-token")

    source_code = "def login():\n    return True\n"
    encoded_content = base64.b64encode(
        source_code.encode("utf-8")
    ).decode("ascii")

    client._get = AsyncMock(
        return_value={
            "type": "file",
            "encoding": "base64",
            "content": encoded_content,
        }
    )

    result = await client.get_file_content(
        "owner",
        "repo",
        "src/auth.py",
        "main",
    )

    assert result == source_code


@pytest.mark.asyncio
async def test_get_file_content_rejects_invalid_path():
    """Empty file paths should be rejected."""

    client = GitHubClient(token="test-token")

    with pytest.raises(ValueError, match="File path is required"):
        await client.get_file_content(
            "owner",
            "repo",
            "",
            "main",
        )


@pytest.mark.asyncio
async def test_get_file_content_rejects_unsupported_encoding():
    """Unsupported GitHub content encodings should be rejected."""

    client = GitHubClient(token="test-token")

    client._get = AsyncMock(
        return_value={
            "type": "file",
            "encoding": "none",
            "content": "",
        }
    )

    with pytest.raises(GitHubClientError, match="Unsupported encoding"):
        await client.get_file_content(
            "owner",
            "repo",
            "src/auth.py",
            "main",
        )


@pytest.mark.asyncio
async def test_get_file_content_rejects_invalid_base64():
    """Invalid Base64 content should be rejected."""

    client = GitHubClient(token="test-token")

    client._get = AsyncMock(
        return_value={
            "type": "file",
            "encoding": "base64",
            "content": "!!!invalid-base64!!!",
        }
    )

    with pytest.raises(GitHubClientError, match="Could not decode"):
        await client.get_file_content(
            "owner",
            "repo",
            "src/auth.py",
            "main",
        )


@pytest.mark.asyncio
async def test_get_file_content_rejects_directory():
    """Directories should not be treated as regular files."""

    client = GitHubClient(token="test-token")

    client._get = AsyncMock(
        return_value={
            "type": "dir",
            "encoding": None,
            "content": None,
        }
    )

    with pytest.raises(GitHubClientError, match="not a regular file"):
        await client.get_file_content(
            "owner",
            "repo",
            "src",
            "main",
        )
