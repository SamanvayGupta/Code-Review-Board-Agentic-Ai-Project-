
"""Run all four AI review agents on a sample code change."""

import asyncio
import logging

from src.models import ChangeState, ReviewStatus
from src.orchestration.review_orchestrator import run_parallel_reviews


logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)


async def main():
    print("=" * 65)
    print("       AUTOMATED CODE REVIEW BOARD")
    print("       Multi-Agent Review Demonstration")
    print("=" * 65)

    # ------------------------------------------------
    # 1. Create shared change state
    # ------------------------------------------------

    state = ChangeState(
        title="Add User Authentication",
        description="Introduce a basic login function.",
        status=ReviewStatus.IN_PROGRESS,

        files_changed=[
            "auth.py",
            "test_auth.py",
        ],

        diff="""
+ def login(username, password):
+     query = "SELECT * FROM users WHERE username='" + username + "'"
+     return db.execute(query)
""",

        modified_code="""
def login(username, password):
    query = "SELECT * FROM users WHERE username='" + username + "'"
    return db.execute(query)
""",

        file_contents={
            "auth.py": """
def login(username, password):
    query = "SELECT * FROM users WHERE username='" + username + "'"
    return db.execute(query)
"""
        },

        test_files={
            "test_auth.py": """
def test_login():
    assert login("admin", "password") is not None
"""
        },
    )

    # ------------------------------------------------
    # 2. Execute all four review agents
    # ------------------------------------------------

    print("\nStarting review...")
    print("Launching Diff, Style, Security, and Test-Coverage Agents...")

    reviewed_state = await run_parallel_reviews(state)

    # ------------------------------------------------
    # 3. Display consolidated review results
    # ------------------------------------------------

    print("\n" + "=" * 65)
    print("              REVIEW SUMMARY")
    print("=" * 65)

    print("Change Title       :", reviewed_state.title)
    print("Review Status      :", reviewed_state.status)
    print("Total Findings     :", len(reviewed_state.findings))
    
    print(
        "Merge Recommendation:",
        state.merge_recommendation.value
        if hasattr(state.merge_recommendation, "value")
        else state.merge_recommendation,
    )

    print("\nReview Summary:")
    print(state.review_summary)    
    

    for index, finding in enumerate(reviewed_state.findings, start=1):

        print("\n" + "-" * 65)
        print(f"FINDING #{index}")
        print("-" * 65)

        severity = getattr(finding.severity, "value", finding.severity)

        print("Severity    :", severity)
        print("Agent       :", finding.agent_name)
        print("Title       :", finding.title)
        print("Description :", finding.description)
        print("File        :", finding.file_path)
        print("Line        :", finding.line_number)
        print("Evidence    :", finding.evidence)
        print("Suggestion  :", finding.suggestion)

    # ------------------------------------------------
    # 4. Display agent errors, if any
    # ------------------------------------------------

    if reviewed_state.errors:
        print("\n" + "=" * 65)
        print("                    AGENT ERRORS")
        print("=" * 65)

        for error in reviewed_state.errors:
            print("-", error)

    # ------------------------------------------------
    # 5. Display final completion status
    # ------------------------------------------------

    print("\n" + "=" * 65)
    print("                 REVIEW COMPLETION")
    print("=" * 65)

    if reviewed_state.status == ReviewStatus.COMPLETED:
        print("SUCCESS: All four agents completed their reviews!")
    else:
        print("WARNING: One or more agents failed.")
        print("Check the agent errors above.")

    print("\nPhase 4 review demonstration finished.")
    print("=" * 65)


if __name__ == "__main__":
    asyncio.run(main())
