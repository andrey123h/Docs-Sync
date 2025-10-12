from typing import List
from fastapi import HTTPException
from github.GithubException import GithubException
from github_app.security.auth import GitHubAuth


class GitHubClient:
    """ This class handles interactions with the GitHub API. """

    # Initialize with GitHubAuth instance for authentication
    def __init__(self, auth: GitHubAuth):
        self.auth = auth

    async def get_changed_python_files(
        self, installation_id: int, owner: str, repo: str, pr_number: int
    ) -> List[str]:
        """
               Get all changed Python files in a pull request.

               Retrieves the list of files modified in a specific pull request and filters to return only Python files.

               Args:
                   installation_id (int): GitHub App installation ID for authentication
                   owner (str): Repository owner (user or organization name)
                   repo (str): Repository name
                   pr_number (int): Pull request number

               Returns:
                   List[str]: List of Python file paths that were changed in the PR.
                             Returns empty list if no Python files changed or on error.
               """
        try:
            github = self.auth.get_github_instance(installation_id)
            repository = github.get_repo(f"{owner}/{repo}")
            pull_request = repository.get_pull(pr_number)

            return [
                file.filename for file in pull_request.get_files()
                if file.filename.endswith(".py")
            ]
        except GithubException as e:
            error_message = e.data.get("message", str(e)) if getattr(e, "data", None) else str(e)
            print(f"GitHub API error getting changed files: {error_message}")
            return []
        except Exception as e:
            print(f"Error getting changed files: {str(e)}")
            return []

    async def post_pr_comment(
        self, installation_id: int, owner: str, repo: str, pr_number: int, body: str
    ) -> str:
        """
               Post a comment to a pull request.
               Creates a new comment on the specified pull request with the provided content.

               Returns:
                   str: HTML URL of the created comment
               """
        try:
            github = self.auth.get_github_instance(installation_id)
            repository = github.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(pr_number)

            comment = issue.create_comment(body)
            return comment.html_url
        except GithubException as e:
            error_message = e.data.get("message", str(e)) if getattr(e, "data", None) else str(e)
            raise HTTPException(
                status_code=getattr(e, "status", 500),
                detail=f"GitHub API error: {error_message}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error posting comment to PR: {str(e)}"
            )

    async def get_file_content(
        self, installation_id: int, owner: str, repo: str, pr_number: int, file_path: str, ref_type: str = "head"
    ) -> str:
        """
        Fetch raw content of a file from a pull request base or head commit.

        Retrieves the content of a specific file at the state it exists in
        either the base commit (target branch) or head commit (PR branch).

        Args:
            installation_id (int): GitHub App installation ID for authentication
            owner (str): Repository owner (user or organization name)
            repo (str): Repository name
            pr_number (int): Pull request number
            file_path (str): Path of the target file
            ref_type (str): "base" or "head" (default: "head")

        Returns:
            str: Decoded file content as UTF-8 string. Returns empty string if
                 file not found or on error.
        """
        try:
            github = self.auth.get_github_instance(installation_id)
            repository = github.get_repo(f"{owner}/{repo}")
            pull_request = repository.get_pull(pr_number)

            # Resolve the correct commit SHA based on ref_type. Default to head.
            ref_sha = pull_request.head.sha if ref_type == "head" else pull_request.base.sha

            contents = repository.get_contents(file_path, ref=ref_sha)
            return contents.decoded_content.decode("utf-8")
        except GithubException as e:
            error_message = e.data.get("message", str(e)) if getattr(e, "data", None) else str(e)
            print(f"GitHub API error getting file content for {file_path}: {error_message}")
            return ""
        except Exception as e:
            print(f"Error getting file content for {file_path}: {str(e)}")
            return ""
