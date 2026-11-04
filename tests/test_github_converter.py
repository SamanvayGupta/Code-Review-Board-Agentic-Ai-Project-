
"""Tests for GitHub Pull Request conversion."""

import pytest

from src.integrations.github_converter import (
    convert_pull_request_to_state,
)
from src.models.change_state import ChangeState


@pytest.fixture
def sample_pull_request():
    return {
        "number": 12,
        "title": "Add authentication",
        "body": "Adds user authentication.",
        "base": {
            "repo": {
                "name": "Code-Review-Board-Agentic-Ai-Project-",
                "owner": {"login": "SamanvayGupta"},
            }
        },
    }


@pytest.fixture
def sample_changed_files():
    return [
        {
            "filename": "src/auth.py",
            "status": "modified",
            "additions": 5,
            "deletions": 2,
            "changes": 7,
            "patch": "@@ -1,2 +1,5 @@\n+def login():",
        },
        {
            "filename": "tests/test_auth.py",
            "status": "added",
            "additions": 10,
            "deletions": 0,
            "changes": 10,
            "patch": "@@ -0,0 +1,10 @@\n+def test_login():",
        },
    ]


def test_convert_pull_request_to_state(
    sample_pull_request,
    sample_changed_files,
):
    state = convert_pull_request_to_state(
        sample_pull_request,
        sample_changed_files,
    )

    assert isinstance(state, ChangeState)
    assert state.title == "Add authentication"
    assert state.description == "Adds user authentication."
    assert len(state.files_changed) == 2
    assert "src/auth.py" in state.file_contents
    assert "def login()" in state.diff


def test_converter_preserves_repository_information(
    sample_pull_request,
    sample_changed_files,
):
    state = convert_pull_request_to_state(
        sample_pull_request,
        sample_changed_files,
    )

    assert state.change_id == (
        "github-SamanvayGupta-"
        "Code-Review-Board-Agentic-Ai-Project--pr-12"
    )
    assert "SamanvayGupta" in state.original_code


def test_converter_handles_missing_patch(sample_pull_request):
    files = [
        {
            "filename": "image.png",
            "status": "modified",
            "additions": 0,
            "deletions": 0,
        }
    ]

    state = convert_pull_request_to_state(
        sample_pull_request,
        files,
    )

    assert state.file_contents["image.png"] == ""
    assert "Patch unavailable" in state.diff


def test_converter_handles_empty_pull_request():
    state = convert_pull_request_to_state({}, [])

    assert state.title == "Untitled Pull Request"
    assert state.files_changed == []
    assert state.diff == ""


def test_converter_rejects_invalid_pull_request():
    with pytest.raises(ValueError):
        convert_pull_request_to_state([], [])
