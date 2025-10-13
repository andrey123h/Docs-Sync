from fastapi import HTTPException
from typing import Dict, Any
from github_app.handlers.git_hub_client import GitHubClient



class PullRequestService:
    """Business rules for processing pull request events"""

    def __init__(self, github_client: GitHubClient):
        self.github = github_client

    def _log_file_comparison(
        self,
        file_path: str,
        head_content: str,
        base_content: str,
        pr_number: int,
        is_first_file: bool = False
    ) -> None:
        """
        Log file content comparison for debugging purposes.

        Args:
            file_path (str): Path of the file being compared
            head_content (str): Content from HEAD (PR branch)
            base_content (str): Content from BASE (target branch)
            pr_number (int): Pull request number
            is_first_file (bool): Whether this is the first file in the list
        """
        if is_first_file:
            print(f"\n{'='*60}")
            print(f"Changed Python files in PR #{pr_number}:")
            print(f"{'='*60}")

        print(f"\n📄 File: {file_path}")
        print(f"{'-'*60}")

        # Print validation results
        if head_content:
            print(f"✓ HEAD content (PR branch) - {len(head_content)} characters:")
            print(f"--- First 300 characters ---")
            print(head_content[:300])
            print(f"--- End of HEAD preview ---\n")
        else:
            print(f"⚠️  HEAD content not found (possibly a new file)")

        if base_content:
            print(f"✓ BASE content (target branch) - {len(base_content)} characters:")
            print(f"--- First 300 characters ---")
            print(base_content[:300])
            print(f"--- End of BASE preview ---\n")
        else:
            print(f"⚠️  BASE content not found (possibly a new file)")

        # Compare if both exist
        if head_content and base_content:
            if head_content == base_content:
                print(f"ℹ️  Note: HEAD and BASE are identical")
            else:
                print(f"✓ Files differ - HEAD has {len(head_content)} chars, BASE has {len(base_content)} chars")

        print(f"{'-'*60}")

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

        # Process changed Python files
        if python_files:
            for idx, file_path in enumerate(python_files):
                # Fetch HEAD version (PR branch)
                head_content = await self.github.get_file_content(
                    installation_id, owner, repo, pr_number, file_path, ref_type="head"
                )

                # Fetch BASE version (target branch)
                base_content = await self.github.get_file_content(
                    installation_id, owner, repo, pr_number, file_path, ref_type="base"
                )

                # Log comparison for debugging
                self._log_file_comparison(file_path, head_content, base_content, pr_number, is_first_file=(idx == 0))
        else:
            print(f"No Python files changed in PR #{pr_number}")

        # Post PR comment
        comment_url = await self.github.post_pr_comment(
            installation_id, owner, repo, pr_number, "Hello from Docs-Sync"
        )

        return {"message": "Comment posted successfully", "comment_url": comment_url}
