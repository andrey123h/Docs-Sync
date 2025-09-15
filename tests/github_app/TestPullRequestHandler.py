import pytest
from github.GithubException import GithubException
from src.github_app.handlers.pull_request_handler import PullRequestHandler


class TestPullRequestHandler:
    """Test suite for PullRequestHandler class"""

    @pytest.fixture
    def mock_github_instance(self, mocker):
        """Mock GitHub instance with repository and pull request"""
        mock_github = mocker.Mock()
        mock_repo = mocker.Mock()
        mock_pr = mocker.Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        return mock_github, mock_repo, mock_pr

    @pytest.mark.asyncio
    async def test_get_changed_python_files_success(self, mocker, mock_github_instance):
        """Test successful retrieval of changed Python files"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.get_github_instance.return_value = mock_github
        mock_github_auth_class = mocker.patch('src.github_app.handlers.pull_request_handler.GitHubAuth')
        mock_github_auth_class.return_value = mock_auth_instance

        handler = PullRequestHandler()

        # Mock file objects
        mock_files = [
            mocker.Mock(filename='src/main.py'),
            mocker.Mock(filename='tests/test_main.py'),
            mocker.Mock(filename='README.md'),
            mocker.Mock(filename='utils/helper.py')
        ]
        mock_pr.get_files.return_value = mock_files

        # Act
        result = await handler.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        expected_files = ['src/main.py', 'tests/test_main.py', 'utils/helper.py']
        assert result == expected_files
        mock_github.get_repo.assert_called_once_with('owner/repo')
        mock_repo.get_pull.assert_called_once_with(1)
        mock_pr.get_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_changed_python_files_no_python_files(self, mocker, mock_github_instance):
        """Test when no Python files are changed"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.get_github_instance.return_value = mock_github
        mock_github_auth_class = mocker.patch('src.github_app.handlers.pull_request_handler.GitHubAuth')
        mock_github_auth_class.return_value = mock_auth_instance

        handler = PullRequestHandler()

        mock_files = [
            mocker.Mock(filename='README.md'),
            mocker.Mock(filename='configure.json'),
            mocker.Mock(filename='Dockerfile')
        ]
        mock_pr.get_files.return_value = mock_files

        # Act
        result = await handler.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_changed_python_files_empty_file_list(self, mocker, mock_github_instance):
        """Test when no files are changed"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.get_github_instance.return_value = mock_github
        mock_github_auth_class = mocker.patch('src.github_app.handlers.pull_request_handler.GitHubAuth')
        mock_github_auth_class.return_value = mock_auth_instance

        handler = PullRequestHandler()
        mock_pr.get_files.return_value = []

        # Act
        result = await handler.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_changed_python_files_github_exception(self, mocker, capsys):
        """Test handling of GitHub API exceptions"""
        # Arrange
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.get_github_instance.side_effect = GithubException(
            status=404,
            data={'message': 'Not Found'}
        )
        mock_github_auth_class = mocker.patch('src.github_app.handlers.pull_request_handler.GitHubAuth')
        mock_github_auth_class.return_value = mock_auth_instance

        handler = PullRequestHandler()

        # Act
        result = await handler.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "GitHub API error getting changed files: Not Found" in captured.out

    @pytest.mark.asyncio
    async def test_get_changed_python_files_github_exception_no_data(self, mocker, capsys):
        """Test handling of GitHub API exceptions without data attribute"""
        # Arrange
        mock_auth_instance = mocker.Mock()
        exception = GithubException(status=500, data=None)
        mock_auth_instance.get_github_instance.side_effect = exception
        mock_github_auth_class = mocker.patch('src.github_app.handlers.pull_request_handler.GitHubAuth')
        mock_github_auth_class.return_value = mock_auth_instance

        handler = PullRequestHandler()

        # Act
        result = await handler.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "GitHub API error getting changed files:" in captured.out

    @pytest.mark.asyncio
    async def test_get_changed_python_files_general_exception(self, mocker, capsys):
        """Test handling of general exceptions"""
        # Arrange
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.get_github_instance.side_effect = Exception("Connection error")
        mock_github_auth_class = mocker.patch('src.github_app.handlers.pull_request_handler.GitHubAuth')
        mock_github_auth_class.return_value = mock_auth_instance

        handler = PullRequestHandler()

        # Act
        result = await handler.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "Error getting changed files: Connection error" in captured.out

    @pytest.mark.asyncio
    async def test_get_changed_python_files_repo_not_found(self, mocker, mock_github_instance, capsys):
        """Test when repository is not found"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.get_github_instance.return_value = mock_github
        mock_github_auth_class = mocker.patch('src.github_app.handlers.pull_request_handler.GitHubAuth')
        mock_github_auth_class.return_value = mock_auth_instance

        handler = PullRequestHandler()
        mock_github.get_repo.side_effect = GithubException(
            status=404,
            data={'message': 'Repository not found'}
        )

        # Act
        result = await handler.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "GitHub API error getting changed files: Repository not found" in captured.out

    @pytest.mark.asyncio
    async def test_get_changed_python_files_pr_not_found(self, mocker, mock_github_instance, capsys):
        """Test when pull request is not found"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        mock_auth_instance = mocker.Mock()
        mock_auth_instance.get_github_instance.return_value = mock_github
        mock_github_auth_class = mocker.patch('src.github_app.handlers.pull_request_handler.GitHubAuth')
        mock_github_auth_class.return_value = mock_auth_instance

        handler = PullRequestHandler()
        mock_repo.get_pull.side_effect = GithubException(
            status=404,
            data={'message': 'Pull request not found'}
        )

        # Act
        result = await handler.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "GitHub API error getting changed files: Pull request not found" in captured.out
