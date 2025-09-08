import unittest
from unittest.mock import MagicMock, patch
import asyncio
from github.GithubException import GithubException


class TestPullRequestHandler(unittest.TestCase):
    """Test cases for PullRequestHandler class"""

    def setUp(self):
        """Set up test fixtures"""
        # Use patch as context manager in setUp
        self.auth_patcher = patch("src.github_app.pull_request_handler.GitHubAuth", autospec=True)
        self.mock_auth_class = self.auth_patcher.start()
        self.mock_auth_instance = self.mock_auth_class.return_value

        # Import and create handler after patching
        from src.github_app.pull_request_handler import PullRequestHandler
        self.handler = PullRequestHandler()

        # Mock GitHub instance returned by get_github_instance
        self.mock_github = MagicMock()
        self.mock_auth_instance.get_github_instance.return_value = self.mock_github

        # Test data
        self.installation_id = 12345
        self.owner = "test-owner"
        self.repo = "test-repo"
        self.pr_number = 42

    def tearDown(self):
        """Clean up patches"""
        self.auth_patcher.stop()

    def test_get_changed_python_files_with_python_files(self):
        """Test retrieving Python files when PR has Python files"""
        mock_repo = MagicMock()
        self.mock_github.get_repo.return_value = mock_repo

        mock_pr = MagicMock()
        mock_repo.get_pull.return_value = mock_pr

        file1 = MagicMock(); file1.filename = "path/to/file1.py"
        file2 = MagicMock(); file2.filename = "path/to/file2.py"
        file3 = MagicMock(); file3.filename = "path/to/file3.txt"
        mock_pr.get_files.return_value = [file1, file2, file3]

        result = asyncio.run(self.handler.get_changed_python_files(
            self.installation_id, self.owner, self.repo, self.pr_number
        ))

        self.mock_github.get_repo.assert_called_once_with(f"{self.owner}/{self.repo}")
        mock_repo.get_pull.assert_called_once_with(self.pr_number)
        mock_pr.get_files.assert_called_once()

        self.assertEqual(result, ["path/to/file1.py", "path/to/file2.py"])

    def test_get_changed_python_files_no_python_files(self):
        mock_repo = MagicMock()
        self.mock_github.get_repo.return_value = mock_repo

        mock_pr = MagicMock()
        mock_repo.get_pull.return_value = mock_pr
        mock_pr.get_files.return_value = []

        result = asyncio.run(self.handler.get_changed_python_files(
            self.installation_id, self.owner, self.repo, self.pr_number
        ))

        self.assertEqual(result, [])

    def test_get_changed_python_files_github_exception(self):
        mock_repo = MagicMock()
        self.mock_github.get_repo.return_value = mock_repo

        github_error = GithubException(status=404, data={"message": "Not Found"}, headers={})
        mock_repo.get_pull.side_effect = github_error

        result = asyncio.run(self.handler.get_changed_python_files(
            self.installation_id, self.owner, self.repo, self.pr_number
        ))

        self.assertEqual(result, [])

    def test_get_changed_python_files_generic_exception(self):
        self.mock_github.get_repo.side_effect = Exception("Some unexpected error")

        result = asyncio.run(self.handler.get_changed_python_files(
            self.installation_id, self.owner, self.repo, self.pr_number
        ))

        self.assertEqual(result, [])


if __name__ == "__main__":
    unittest.main()
