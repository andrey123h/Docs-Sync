import pytest
from github.GithubException import GithubException
from src.github_app.handlers.git_hub_client import GitHubClient


class TestGitHubClient:
    """Test suite for GitHubClient class"""

    @pytest.fixture
    def mock_github_instance(self, mocker):
        """Mock GitHub instance with repository and pull request"""
        mock_github = mocker.Mock()
        mock_repo = mocker.Mock()
        mock_pr = mocker.Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.get_pull.return_value = mock_pr
        return mock_github, mock_repo, mock_pr

    @pytest.fixture
    def client(self, mocker):
        """Create a GitHubClient instance with mocked auth for testing"""
        mock_auth = mocker.Mock()
        return GitHubClient(mock_auth)

    @pytest.mark.asyncio
    async def test_get_changed_python_files_success(self, mocker, mock_github_instance, client):
        """Test successful retrieval of changed Python files"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Mock file objects
        mock_files = [
            mocker.Mock(filename='src/main.py'),
            mocker.Mock(filename='tests/test_main.py'),
            mocker.Mock(filename='README.md'),
            mocker.Mock(filename='utils/helper.py')
        ]
        mock_pr.get_files.return_value = mock_files

        # Act
        result = await client.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        expected_files = ['src/main.py', 'tests/test_main.py', 'utils/helper.py']
        assert result == expected_files
        mock_github.get_repo.assert_called_once_with('owner/repo')
        mock_repo.get_pull.assert_called_once_with(1)
        mock_pr.get_files.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_changed_python_files_no_python_files(self, mocker, mock_github_instance, client):
        """Test when no Python files are changed"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_files = [
            mocker.Mock(filename='README.md'),
            mocker.Mock(filename='configure.json'),
            mocker.Mock(filename='Dockerfile')
        ]
        mock_pr.get_files.return_value = mock_files

        # Act
        result = await client.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_changed_python_files_empty_file_list(self, mocker, mock_github_instance, client):
        """Test when no files are changed"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github
        mock_pr.get_files.return_value = []

        # Act
        result = await client.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []

    @pytest.mark.asyncio
    async def test_get_changed_python_files_github_exception(self, mocker, capsys, client):
        """Test handling of GitHub API exceptions"""
        # Arrange
        client.auth.get_github_instance.side_effect = GithubException(
            status=404,
            data={'message': 'Not Found'}
        )

        # Act
        result = await client.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "GitHub API error getting changed files: Not Found" in captured.out

    @pytest.mark.asyncio
    async def test_get_changed_python_files_github_exception_no_data(self, mocker, capsys, client):
        """Test handling of GitHub API exceptions without data attribute"""
        # Arrange
        exception = GithubException(status=500, data=None)
        client.auth.get_github_instance.side_effect = exception

        # Act
        result = await client.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "GitHub API error getting changed files:" in captured.out

    @pytest.mark.asyncio
    async def test_get_changed_python_files_general_exception(self, mocker, capsys, client):
        """Test handling of general exceptions"""
        # Arrange
        client.auth.get_github_instance.side_effect = Exception("Connection error")

        # Act
        result = await client.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "Error getting changed files: Connection error" in captured.out

    @pytest.mark.asyncio
    async def test_get_changed_python_files_repo_not_found(self, mocker, mock_github_instance, capsys, client):
        """Test when repository is not found"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github
        mock_github.get_repo.side_effect = GithubException(
            status=404,
            data={'message': 'Repository not found'}
        )

        # Act
        result = await client.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "GitHub API error getting changed files: Repository not found" in captured.out

    @pytest.mark.asyncio
    async def test_get_changed_python_files_pr_not_found(self, mocker, mock_github_instance, capsys, client):
        """Test when pull request is not found"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github
        mock_repo.get_pull.side_effect = GithubException(
            status=404,
            data={'message': 'Pull request not found'}
        )

        # Act
        result = await client.get_changed_python_files(12345, 'owner', 'repo', 1)

        # Assert
        assert result == []
        captured = capsys.readouterr()
        assert "GitHub API error getting changed files: Pull request not found" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_success(self, mocker, mock_github_instance, client):
        """Test successful retrieval of file content from PR head commit"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Mock file content
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = b"def hello():\n    return 'Hello World'"
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/main.py')

        # Assert
        expected_content = "def hello():\n    return 'Hello World'"
        assert result == expected_content
        mock_github.get_repo.assert_called_once_with('owner/repo')
        mock_repo.get_pull.assert_called_once_with(1)
        mock_repo.get_contents.assert_called_once_with('src/main.py', ref='abc123')

    @pytest.mark.asyncio
    async def test_get_file_content_github_exception(self, mocker, mock_github_instance, capsys, client):
        """Test handling of GitHub API exceptions when fetching file content"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_repo.get_contents.side_effect = GithubException(
            status=404,
            data={'message': 'File not found'}
        )
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/main.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "GitHub API error getting file content for src/main.py: File not found" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_github_exception_no_data(self, mocker, mock_github_instance, capsys, client):
        """Test handling of GitHub API exceptions without data attribute when fetching file content"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        exception = GithubException(status=500, data=None)
        mock_repo.get_contents.side_effect = exception
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/main.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "GitHub API error getting file content for src/main.py:" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_general_exception(self, mocker, mock_github_instance, capsys, client):
        """Test handling of general exceptions when fetching file content"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_repo.get_contents.side_effect = Exception("Network error")
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/main.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "Error getting file content for src/main.py: Network error" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_auth_failure(self, mocker, capsys, client):
        """Test handling of authentication failures when fetching file content"""
        # Arrange
        client.auth.get_github_instance.side_effect = Exception("Authentication failed")

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/main.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "Error getting file content for src/main.py: Authentication failed" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_unicode_content(self, mocker, mock_github_instance, client):
        """Test successful retrieval of file content with unicode characters"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Mock file content with unicode
        unicode_content = "# Тест\ndef hello():\n    return 'Привет мир'"
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = unicode_content.encode('utf-8')
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/main.py')

        # Assert
        assert result == unicode_content

    @pytest.mark.asyncio
    async def test_get_file_content_empty_file(self, mocker, mock_github_instance, client):
        """Test successful retrieval of empty file content"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Mock empty file content
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = b""
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/empty.py')

        # Assert
        assert result == ""

    @pytest.mark.asyncio
    async def test_get_file_content_binary_file(self, mocker, mock_github_instance, capsys, client):
        """Test handling of binary file content (should handle gracefully)"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Mock binary file content (e.g., image)
        binary_content = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR'
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = binary_content
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'assets/logo.png')

        # Assert - Should return empty string when decode fails
        assert result == ""
        captured = capsys.readouterr()
        assert "Error getting file content for assets/logo.png:" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_large_file(self, mocker, mock_github_instance, client):
        """Test handling of large file content"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Mock large file content (simulating a large Python file)
        large_content = "# Large file\n" + "print('line')\n" * 10000
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = large_content.encode('utf-8')
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/large_file.py')

        # Assert
        assert result == large_content
        assert len(result) > 100000  # Verify it's actually large

    @pytest.mark.asyncio
    async def test_get_file_content_file_with_special_characters(self, mocker, mock_github_instance, client):
        """Test handling of file paths with special characters"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_contents = mocker.Mock()
        mock_contents.decoded_content = b"# File with special path"
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/файл_с_русскими_символами.py')

        # Assert
        assert result == "# File with special path"
        mock_repo.get_contents.assert_called_once_with('src/файл_с_русскими_символами.py', ref='abc123')

    @pytest.mark.asyncio
    async def test_get_file_content_nested_path(self, mocker, mock_github_instance, client):
        """Test handling of deeply nested file paths"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_contents = mocker.Mock()
        mock_contents.decoded_content = b"# Deeply nested file"
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        nested_path = 'src/very/deep/nested/folder/structure/file.py'
        result = await client.get_file_content(12345, 'owner', 'repo', 1, nested_path)

        # Assert
        assert result == "# Deeply nested file"
        mock_repo.get_contents.assert_called_once_with(nested_path, ref='abc123')

    @pytest.mark.asyncio
    async def test_get_file_content_different_encodings(self, mocker, mock_github_instance, client):
        """Test handling of files with different character encodings"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Test with various Unicode characters
        unicode_content = "# Файл с русскими символами\n# File with émojis 🐍🔥\n# 中文字符测试"
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = unicode_content.encode('utf-8')
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/unicode_test.py')

        # Assert
        assert result == unicode_content

    @pytest.mark.asyncio
    async def test_get_file_content_file_not_in_pr_head(self, mocker, mock_github_instance, capsys, client):
        """Test when file doesn't exist in the PR head commit"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_repo.get_contents.side_effect = GithubException(
            status=404,
            data={'message': 'File not found in this commit'}
        )
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/nonexistent.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "GitHub API error getting file content for src/nonexistent.py: File not found in this commit" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_rate_limit_exceeded(self, mocker, mock_github_instance, capsys, client):
        """Test handling of GitHub API rate limit"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_repo.get_contents.side_effect = GithubException(
            status=403,
            data={'message': 'API rate limit exceeded'}
        )
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/main.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "GitHub API error getting file content for src/main.py: API rate limit exceeded" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_invalid_sha(self, mocker, mock_github_instance, capsys, client):
        """Test when PR head SHA is invalid or malformed"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_repo.get_contents.side_effect = GithubException(
            status=422,
            data={'message': 'Invalid SHA'}
        )
        mock_pr.head.sha = "invalid_sha"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/main.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "GitHub API error getting file content for src/main.py: Invalid SHA" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_whitespace_only_file(self, mocker, mock_github_instance, client):
        """Test handling of files containing only whitespace"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # File with only whitespace
        whitespace_content = "   \n\t\n   \n"
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = whitespace_content.encode('utf-8')
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/whitespace.py')

        # Assert
        assert result == whitespace_content

    @pytest.mark.asyncio
    async def test_get_file_content_file_with_only_comments(self, mocker, mock_github_instance, client):
        """Test handling of Python files containing only comments"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # File with only comments
        comments_only = "# This is a comment\n# Another comment\n# TODO: Add implementation"
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = comments_only.encode('utf-8')
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/comments_only.py')

        # Assert
        assert result == comments_only

    @pytest.mark.asyncio
    async def test_get_file_content_repository_access_denied(self, mocker, capsys, client):
        """Test when access to repository is denied"""
        # Arrange
        mock_github = mocker.Mock()
        client.auth.get_github_instance.return_value = mock_github

        mock_github.get_repo.side_effect = GithubException(
            status=403,
            data={'message': 'Repository access denied'}
        )

        # Act
        result = await client.get_file_content(12345, 'owner', 'private_repo', 1, 'src/main.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "GitHub API error getting file content for src/main.py: Repository access denied" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_malformed_utf8(self, mocker, mock_github_instance, capsys, client):
        """Test handling of malformed UTF-8 content"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Mock malformed UTF-8 content
        malformed_content = b'\xff\xfe\x00\x00invalid utf-8'
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = malformed_content
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/malformed.py')

        # Assert
        assert result == ""
        captured = capsys.readouterr()
        assert "Error getting file content for src/malformed.py:" in captured.out

    @pytest.mark.asyncio
    async def test_get_file_content_very_long_filename(self, mocker, mock_github_instance, client):
        """Test handling of files with very long filenames"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        mock_contents = mocker.Mock()
        mock_contents.decoded_content = b"# File with very long name"
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        long_filename = 'src/' + 'very_long_' * 20 + 'filename.py'
        result = await client.get_file_content(12345, 'owner', 'repo', 1, long_filename)

        # Assert
        assert result == "# File with very long name"
        mock_repo.get_contents.assert_called_once_with(long_filename, ref='abc123')

    @pytest.mark.asyncio
    async def test_get_file_content_file_with_line_endings(self, mocker, mock_github_instance, client):
        """Test handling of files with different line endings (CRLF, LF)"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Content with mixed line endings
        mixed_endings_content = "# Line 1\r\n# Line 2\n# Line 3\r\n"
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = mixed_endings_content.encode('utf-8')
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/mixed_endings.py')

        # Assert
        assert result == mixed_endings_content

    @pytest.mark.asyncio
    async def test_get_file_content_file_with_tabs_and_spaces(self, mocker, mock_github_instance, client):
        """Test handling of files with mixed tabs and spaces"""
        # Arrange
        mock_github, mock_repo, mock_pr = mock_github_instance
        client.auth.get_github_instance.return_value = mock_github

        # Content with mixed indentation
        mixed_indentation = "def function():\n    if True:\n\t\treturn 'mixed'\n    else:\n\t\treturn 'indentation'"
        mock_contents = mocker.Mock()
        mock_contents.decoded_content = mixed_indentation.encode('utf-8')
        mock_repo.get_contents.return_value = mock_contents
        mock_pr.head.sha = "abc123"

        # Act
        result = await client.get_file_content(12345, 'owner', 'repo', 1, 'src/mixed_indent.py')

        # Assert
        assert result == mixed_indentation

    @pytest.mark.asyncio
    async def test_post_pr_comment_success(self, mocker, client):
        """Test successful posting of PR comment"""
        # Arrange
        mock_github = mocker.Mock()
        client.auth.get_github_instance.return_value = mock_github
        mock_repo = mocker.Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_issue = mocker.Mock()
        mock_repo.get_issue.return_value = mock_issue
        mock_comment = mocker.Mock()
        mock_comment.html_url = "https://github.com/owner/repo/pull/1#issuecomment-1"
        mock_issue.create_comment.return_value = mock_comment

        # Act
        result = await client.post_pr_comment(12345, 'owner', 'repo', 1, "Test comment")

        # Assert
        assert result == "https://github.com/owner/repo/pull/1#issuecomment-1"
        mock_github.get_repo.assert_called_once_with('owner/repo')
        mock_repo.get_issue.assert_called_once_with(1)
        mock_issue.create_comment.assert_called_once_with("Test comment")

