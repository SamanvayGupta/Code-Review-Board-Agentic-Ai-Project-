
import asyncio

from src.integrations.github_client import GitHubClient


async def main():
    client = GitHubClient()

    result = await client._get(
        "repos/SamanvayGupta/Code-Review-Board-Agentic-Ai-Project-/pulls?state=open"
    )

    if not result:
        print("No open Pull Requests found.")
        return

    print(f"Found {len(result)} open Pull Request(s):\n")

    for pr in result:
        print(f"PR Number: #{pr['number']}")
        print(f"Title: {pr['title']}")
        print(f"Author: {pr['user']['login']}")
        print(f"URL: {pr['html_url']}")
        print("-" * 50)


if __name__ == "__main__":
    asyncio.run(main())
