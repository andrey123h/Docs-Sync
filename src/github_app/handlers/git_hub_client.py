from typing import List
from fastapi import HTTPException
from github.GithubException import GithubException
from github_app.security.auth import GitHubAuth


class GitHubClient:
    """ interactions with the GitHub API. """

    def __init__(self, auth: GitHubAuth):
        self.auth = auth

    async def get_changed_python_files(
        self, installation_id: int, owner: str, repo: str, pr_number: int
    ) -> List[str]:
        """
               Get all changed Python files in a pull request.
               Retrieves the list of files modified in a specific pull request and filters to return only Python files.
               """
        try:
            github = self.auth.get_github_instance(installation_id)
            repository = github.get_repo(f"{owner}/{repo}")
            pull_request = repository.get_pull(pr_number)

            return [
                file.filename for file in pull_request.get_files()
                if file.filename.endswith(".py")
            ]
        except Exception as e:
            print(f"Error getting changed files: {str(e)}")
            return []

    async def post_pr_comment(
        self, installation_id: int, owner: str, repo: str, pr_number: int, body: str
    ) -> str:
        """
            Post a comment to a pull request.
               Creates a new comment on the specified pull request with the provided content.
               """
        try:
            github = self.auth.get_github_instance(installation_id)
            repository = github.get_repo(f"{owner}/{repo}")
            issue = repository.get_issue(pr_number)
            comment = issue.create_comment(body)
            return comment.html_url


        except Exception as e:
            print(f"Error getting changed files: {str(e)}")
            return ""

    async def get_file_content(
        self, installation_id: int, owner: str, repo: str, pr_number: int, file_path: str, ref_type: str = "head"
    ) -> str:
        """
        Fetch raw content of a file from a pull request base or head commit.

        Retrieves the content of a specific file at the state it exists in
        either the base commit (target branch) or head commit (PR branch).
        """
        try:
            github = self.auth.get_github_instance(installation_id)
            repository = github.get_repo(f"{owner}/{repo}")
            pull_request = repository.get_pull(pr_number)

            # Resolve the correct commit SHA based on ref_type. Default to head.
            ref_sha = pull_request.head.sha if ref_type == "head" else pull_request.base.sha

            contents = repository.get_contents(file_path, ref=ref_sha)
            return contents.decoded_content.decode("utf-8")

        except Exception as e:
            print(f"Error getting file content for {file_path}: {str(e)}")
            return ""
