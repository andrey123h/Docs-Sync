from fastapi import HTTPException
from typing import Dict, Any
from git_hub_client import GitHubClient


class PullRequestService:
    """Business rules for processing pull request events"""

    def __init__(self, github_client: GitHubClient):
        self.github = github_client

    async def process_opened(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        installation_id = event_data.get("installation", {}).get("id")
        repository = event_data.get("repository", {})
        pull_request = event_data.get("pull_request", {})

        owner = repository.get("owner", {}).get("login")
        repo = repository.get("name")
        pr_number = pull_request.get("number")

        # Validate required fields
        if not all([installation_id, owner, repo, pr_number]):
            raise HTTPException(
                status_code=400,
                detail="Missing required data: installation_id, owner, repo, or pr_number"
            )

        # Changed Python files
        python_files = await self.github.get_changed_python_files(
            installation_id, owner, repo, pr_number
        )

        if python_files:
            print(f"Changed Python files in PR #{pr_number}:")
            for file in python_files:
                print(f"  - {file}")
        else:
            print(f"No Python files changed in PR #{pr_number}")

        # Post PR comment
        comment_url = await self.github.post_pr_comment(
            installation_id, owner, repo, pr_number, "Hello from Docs-Sync"
        )

        return {"message": "Comment posted successfully", "comment_url": comment_url}
