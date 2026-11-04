
"""Convert GitHub Pull Request data into ChangeState."""

from typing import Any

from src.models.change_state import ChangeState


def convert_pull_request_to_state(
    pull_request: dict[str, Any],
    changed_files: list[dict[str, Any]],
    file_contents: dict[str, str] | None = None,
) -> ChangeState:
    """Convert GitHub PR details, patches, and source files into ChangeState."""

    if not isinstance(pull_request, dict):
        raise ValueError("Pull Request data must be a dictionary.")

    if not isinstance(changed_files, list):
        raise ValueError("Changed files must be provided as a list.")

    if file_contents is not None and not isinstance(file_contents, dict):
        raise ValueError("File contents must be provided as a dictionary.")

    title = pull_request.get("title") or "Untitled Pull Request"
    description = pull_request.get("body") or ""

    base_repo = pull_request.get("base", {}).get("repo", {})
    owner = base_repo.get("owner", {}).get("login", "")
    repo = base_repo.get("name", "")
    pr_number = pull_request.get("number")

    source_contents = {}
    files_changed = []
    diff_sections = []

    for file_data in changed_files:
        if not isinstance(file_data, dict):
            continue

        filename = file_data.get("filename")

        if not filename:
            continue

        files_changed.append(filename)

        patch = file_data.get("patch")

        # Preserve backward compatibility when full source is unavailable.
        if file_contents is None:
            source_contents[filename] = patch or ""
        elif filename in file_contents:
            source_contents[filename] = file_contents[filename]

        if patch:
            diff_sections.append(
                f"File: {filename}\n"
                f"Status: {file_data.get('status', 'modified')}\n"
                f"Additions: {file_data.get('additions', 0)}\n"
                f"Deletions: {file_data.get('deletions', 0)}\n"
                f"Patch:\n{patch}"
            )
        else:
            diff_sections.append(
                f"File: {filename}\n"
                f"Status: {file_data.get('status', 'modified')}\n"
                "Patch unavailable from GitHub."
            )

    diff = "\n\n".join(diff_sections)

    original_code = (
        f"GitHub repository: {owner}/{repo}\n"
        f"Pull Request: #{pr_number}"
    )

    modified_code = "\n\n".join(
        f"File: {filename}\n{content}"
        for filename, content in source_contents.items()
    )

    return ChangeState(
        change_id=f"github-{owner}-{repo}-pr-{pr_number}",
        title=title,
        description=description,
        original_code=original_code,
        modified_code=modified_code,
        diff=diff,
        files_changed=files_changed,
        file_contents=source_contents,
    )
