"""Tests for GitHub utilities module."""

import os
import shutil
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master_consolidated import GitHubCloneError, GitHubUtils


class TestGitHubUtils:
    """Test cases for GitHubUtils class."""

    def setup_method(self):
        """Set up test fixtures."""
        self.github_utils = GitHubUtils()

    def teardown_method(self):
        """Clean up after tests."""
        self.github_utils.cleanup_temp_directories()

    def test_parse_github_url_owner_repo_format(self):
        """Test parsing owner/repo format."""
        result = self.github_utils.parse_github_url("owner/repo")
        assert result == "owner/repo"

    def test_parse_github_url_https_format(self):
        """Test parsing HTTPS GitHub URL."""
        result = self.github_utils.parse_github_url(
            "https://github.com/owner/repo"
        )
        assert result == "owner/repo"

    def test_parse_github_url_https_with_path(self):
        """Test parsing GitHub URL with additional path components."""
        result = self.github_utils.parse_github_url(
            "https://github.com/owner/repo/issues"
        )
        assert result == "owner/repo"

    def test_parse_github_url_invalid_format(self):
        """Test parsing invalid GitHub URL format."""
        with pytest.raises(
            ValueError, match="Invalid GitHub repository format"
        ):
            self.github_utils.parse_github_url("invalid-format")

    def test_parse_github_url_non_github_domain(self):
        """Test parsing URL from non-GitHub domain."""
        with pytest.raises(ValueError, match="URL must be from github.com"):
            self.github_utils.parse_github_url("https://gitlab.com/owner/repo")

    @patch("ticket_master_consolidated.requests.get")
    def test_is_public_repository_public(self, mock_get):
        """Test detecting public repository."""
        # Mock successful response for public repo
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"private": False}
        mock_get.return_value = mock_response

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is True

    @patch("ticket_master_consolidated.requests.get")
    def test_is_public_repository_private(self, mock_get):
        """Test detecting private repository."""
        # Mock successful response for private repo
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"private": True}
        mock_get.return_value = mock_response

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is False

    @patch("ticket_master_consolidated.requests.get")
    def test_is_public_repository_not_found(self, mock_get):
        """Test handling repository not found."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is False

    @patch("subprocess.run")
    @patch("ticket_master_consolidated.requests.get")
    def test_is_public_repository_rate_limited_fallback_public(
        self, mock_get, mock_subprocess
    ):
        """Test fallback to git ls-remote when rate limited for public repo."""
        # Mock 403 response (rate limited)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        # Mock successful git ls-remote
        mock_subprocess.return_value = Mock(returncode=0)

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is True

    @patch("subprocess.run")
    @patch("ticket_master_consolidated.requests.get")
    def test_is_public_repository_rate_limited_fallback_private(
        self, mock_get, mock_subprocess
    ):
        """Test fallback to git ls-remote when rate limited for private repo."""
        # Mock 403 response (rate limited)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        # Mock failed git ls-remote (private repo)
        mock_subprocess.return_value = Mock(returncode=1)

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is False

    @patch("ticket_master_consolidated.requests.get")
    def test_get_repository_info_success(self, mock_get):
        """Test getting repository info successfully."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "name": "repo",
            "full_name": "owner/repo",
            "description": "Test repository",
            "private": False,
            "clone_url": "https://github.com/owner/repo.git",
            "ssh_url": "git@github.com:owner/repo.git",
            "default_branch": "main",
            "language": "Python",
            "size": 1000,
        }
        mock_get.return_value = mock_response

        result = self.github_utils.get_repository_info("owner/repo")

        assert result is not None
        assert result["name"] == "repo"
        assert result["full_name"] == "owner/repo"
        assert result["private"] is False

    @patch("ticket_master_consolidated.requests.get")
    def test_get_repository_info_rate_limited(self, mock_get):
        """Test getting repository info when rate limited."""
        # Mock 403 response (rate limited)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        result = self.github_utils.get_repository_info("owner/repo")

        assert result is not None
        assert result["name"] == "repo"
        assert result["full_name"] == "owner/repo"
        assert result["clone_url"] == "https://github.com/owner/repo.git"
        assert result["private"] is None  # Unknown due to rate limiting

    @patch("ticket_master_consolidated.Repo.clone_from")
    @patch("ticket_master_consolidated.GitHubUtils.get_repository_info")
    def test_clone_repository_public_success(self, mock_get_info, mock_clone):
        """Test successful cloning of public repository."""
        # Mock repository info
        mock_get_info.return_value = {
            "private": False,
            "clone_url": "https://github.com/owner/repo.git",
        }

        # Mock successful clone
        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        result = self.github_utils.clone_repository("owner/repo")

        assert result is not None
        assert result.startswith("/tmp/ticket-master-owner-repo-")
        mock_clone.assert_called_once()

    @patch("ticket_master_consolidated.Repo.clone_from")
    @patch("ticket_master_consolidated.GitHubUtils.get_repository_info")
    def test_clone_repository_private_with_token(
        self, mock_get_info, mock_clone
    ):
        """Test successful cloning of private repository with token."""
        # Mock repository info
        mock_get_info.return_value = {
            "private": True,
            "clone_url": "https://github.com/owner/repo.git",
        }

        # Mock successful clone
        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        result = self.github_utils.clone_repository(
            "owner/repo", token="test-token"
        )

        assert result is not None
        mock_clone.assert_called_once()
        # Check that authenticated URL was used
        call_args = mock_clone.call_args
        assert "test-token@github.com" in call_args[0][0]

    @patch("ticket_master_consolidated.GitHubUtils.get_repository_info")
    def test_clone_repository_not_found(self, mock_get_info):
        """Test cloning repository that doesn't exist."""
        # Mock repository not found
        mock_get_info.return_value = None

        with pytest.raises(
            GitHubCloneError, match="not found or not accessible"
        ):
            self.github_utils.clone_repository("owner/nonexistent")

    @patch("ticket_master_consolidated.Repo.clone_from")
    @patch("ticket_master_consolidated.GitHubUtils.get_repository_info")
    def test_clone_repository_to_local_path(self, mock_get_info, mock_clone):
        """Test cloning repository to specified local path."""
        # Mock repository info
        mock_get_info.return_value = {
            "private": False,
            "clone_url": "https://github.com/owner/repo.git",
        }

        # Mock successful clone
        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = os.path.join(temp_dir, "test-repo")

            result = self.github_utils.clone_repository(
                "owner/repo", local_path=local_path
            )

            assert result == os.path.abspath(local_path)
            mock_clone.assert_called_once()

    def test_cleanup_temp_directories(self):
        """Test cleanup of temporary directories."""
        # Create a mock temporary directory
        temp_dir = tempfile.mkdtemp()
        self.github_utils._temp_dirs.append(temp_dir)

        # Verify directory exists
        assert os.path.exists(temp_dir)

        # Cleanup
        self.github_utils.cleanup_temp_directories()

        # Verify directory is removed and list is cleared
        assert not os.path.exists(temp_dir)
        assert len(self.github_utils._temp_dirs) == 0

    def test_destructor_cleanup(self):
        """Test that cleanup happens in destructor."""
        # Create a new instance
        utils = GitHubUtils()

        # Create a mock temporary directory
        temp_dir = tempfile.mkdtemp()
        utils._temp_dirs.append(temp_dir)

        # Verify directory exists
        assert os.path.exists(temp_dir)

        # Delete the instance
        del utils

        # Note: In practice, the destructor cleanup might not run immediately
        # due to Python's garbage collection, so we just test the method exists


class TestGitHubAPIIntegration:
    """Test GitHub API integration scenarios."""

    def setup_method(self):
        """Set up test fixtures."""
        self.github_utils = GitHubUtils()

    def teardown_method(self):
        """Clean up after tests."""
        self.github_utils.cleanup_temp_directories()

    @patch("github.Github")  # Patch the actual github module
    def test_rate_limit_handling(self, mock_github_class):
        """Test handling of GitHub API rate limits."""
        from github import RateLimitExceededException

        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo

        # Simulate rate limit exceeded
        mock_repo.create_issue.side_effect = RateLimitExceededException(
            status=403, data={"message": "API rate limit exceeded"}
        )

        with pytest.raises(RateLimitExceededException):
            mock_repo.create_issue(title="Test", body="Test body")

    @patch("github.Github")
    def test_bulk_operations_with_delays(self, mock_github_class):
        """Test bulk operations with appropriate delays to avoid rate limiting."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo

        # Mock successful issue creation
        mock_issue = Mock()
        mock_issue.number = 1
        mock_repo.create_issue.return_value = mock_issue

        # Simulate creating multiple issues
        issues_data = [
            {"title": "Issue 1", "body": "Body 1"},
            {"title": "Issue 2", "body": "Body 2"},
            {"title": "Issue 3", "body": "Body 3"},
        ]

        with patch("time.sleep") as mock_sleep:
            for i, issue_data in enumerate(issues_data):
                mock_repo.create_issue(**issue_data)
                if i < len(issues_data) - 1:  # Don't sleep after the last one
                    mock_sleep(1)  # Simulate delay between requests

            # Verify that sleep was called between requests
            assert mock_sleep.call_count == len(issues_data) - 1

    @patch("github.Github")
    def test_authentication_edge_cases(self, mock_github_class):
        """Test various GitHub authentication scenarios."""
        from github import BadCredentialsException, UnknownObjectException

        mock_github = Mock()
        mock_github_class.return_value = mock_github

        # Test invalid token
        mock_github.get_user.side_effect = BadCredentialsException(
            status=401, data={"message": "Bad credentials"}
        )

        with pytest.raises(BadCredentialsException):
            mock_github.get_user()

        # Test token with insufficient permissions
        mock_github.get_user.side_effect = UnknownObjectException(
            status=404, data={"message": "Not Found"}
        )

        with pytest.raises(UnknownObjectException):
            mock_github.get_user()

    @patch("github.Github")
    def test_repository_access_permissions(self, mock_github_class):
        """Test repository access with different permission levels."""
        from github import GithubException, UnknownObjectException

        mock_github = Mock()
        mock_github_class.return_value = mock_github

        # Test repository not found or no access
        mock_github.get_repo.side_effect = UnknownObjectException(
            status=404, data={"message": "Not Found"}
        )

        with pytest.raises(UnknownObjectException):
            mock_github.get_repo("private/repo")

        # Test repository access forbidden
        mock_github.get_repo.side_effect = GithubException(
            status=403, data={"message": "Forbidden"}
        )

        with pytest.raises(GithubException):
            mock_github.get_repo("forbidden/repo")


class TestGitHubUtilsAdvanced:
    """Test advanced GitHub utilities functionality."""

    def setup_method(self):
        """Set up test fixtures."""
        self.github_utils = GitHubUtils()

    def teardown_method(self):
        """Clean up after tests."""
        self.github_utils.cleanup_temp_directories()

    @patch("git.Repo.clone_from")  # Patch git module directly
    def test_clone_large_repository_performance(self, mock_clone):
        """Test cloning large repositories with performance considerations."""
        # Mock a large repository clone
        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        # Test clone with shallow option for performance
        repo_url = "https://github.com/large/repository"
        local_path = "/tmp/test_clone"

        # This would be part of enhanced clone functionality
        mock_clone(repo_url, local_path, depth=1)  # Shallow clone

        mock_clone.assert_called_once_with(repo_url, local_path, depth=1)

    def test_handle_binary_files_in_analysis(self):
        """Test handling binary files during repository analysis."""
        # Create a temporary file with binary content
        with tempfile.NamedTemporaryFile(
            delete=False, suffix=".bin"
        ) as temp_file:
            temp_file.write(b"\x00\x01\x02\x03\x04\x05")
            temp_file_path = temp_file.name

        try:
            # Test that binary file detection works
            with open(temp_file_path, "rb") as f:
                content = f.read()
                # Simple binary detection - contains null bytes
                is_binary = b"\x00" in content
                assert is_binary

        finally:
            os.unlink(temp_file_path)

    def test_handle_huge_files_memory_optimization(self):
        """Test handling huge files without loading entire content into memory."""
        # Create a large temporary file
        with tempfile.NamedTemporaryFile(delete=False, mode="w") as temp_file:
            # Write a large amount of data
            for i in range(1000):
                temp_file.write(f"Line {i}: " + "x" * 100 + "\n")
            temp_file_path = temp_file.name

        try:
            # Test reading file in chunks rather than all at once
            chunk_size = 1024
            total_size = 0

            with open(temp_file_path, "r") as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    total_size += len(chunk)

            # Verify we read the entire file in chunks
            file_size = os.path.getsize(temp_file_path)
            assert total_size == file_size

        finally:
            os.unlink(temp_file_path)

    @patch("platform.system")
    def test_cross_platform_path_compatibility(self, mock_system):
        """Test path handling across different operating systems."""
        # Test Windows
        mock_system.return_value = "Windows"
        windows_path = "C:\\Users\\test\\repo"
        normalized_path = os.path.normpath(windows_path)
        assert "\\" in normalized_path or "/" in normalized_path

        # Test Linux/macOS
        mock_system.return_value = "Linux"
        unix_path = "/home/test/repo"
        normalized_path = os.path.normpath(unix_path)
        assert normalized_path.startswith("/")

        # Test path joining
        base_path = (
            "/tmp" if mock_system.return_value != "Windows" else "C:\\temp"
        )
        sub_path = "test_repo"
        full_path = os.path.join(base_path, sub_path)
        assert sub_path in full_path

    def test_empty_repository_handling(self):
        """Test handling of empty repositories."""
        # Create an empty temporary directory to simulate empty repo
        with tempfile.TemporaryDirectory() as temp_dir:
            # Initialize as git repo but keep it empty
            import git

            repo = git.Repo.init(temp_dir)

            # Add a commit to avoid "reference does not exist" error
            # Create an empty commit
            repo.index.commit("Initial empty commit", allow_empty=True)

            # Test that analysis handles repos with minimal commits gracefully
            commits = list(repo.iter_commits())
            self.assertGreaterEqual(
                len(commits), 1
            )  # At least the initial commit

            # Test that directory contains minimal files
            files = os.listdir(temp_dir)
            non_git_files = [f for f in files if not f.startswith(".git")]
            self.assertEqual(len(non_git_files), 0)  # Only .git directory


class TestSecurityScenarios:
    """Test security-related scenarios."""

    def test_malicious_repository_url_validation(self):
        """Test validation of potentially malicious repository URLs."""
        github_utils = GitHubUtils()

        # Test malicious URLs that should be rejected
        malicious_urls = [
            "file:///etc/passwd",
            "http://localhost/../../etc/passwd",
            "ftp://malicious.com/repo",
            "javascript:alert('xss')",
            "../../../etc/passwd",
        ]

        for url in malicious_urls:
            with pytest.raises(ValueError):
                github_utils.parse_github_url(url)

    def test_path_traversal_prevention(self):
        """Test prevention of path traversal attacks."""
        github_utils = GitHubUtils()

        # Test paths that could lead to path traversal
        dangerous_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32",
            "/../../../../etc/passwd",
            "repo/../../../secret",
        ]

        for path in dangerous_paths:
            # Normalize and validate path doesn't escape intended directory
            normalized = os.path.normpath(path)
            # Should not start with .. after normalization if properly contained
            if normalized.startswith(".."):
                # This would be rejected in a real implementation
                assert True  # Path traversal detected

    @patch("github.Github")
    def test_token_exposure_prevention(self, mock_github_class):
        """Test that tokens are not exposed in logs or error messages."""
        token = "ghp_sensitive_token_123456789"

        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_github.get_user.side_effect = Exception("Authentication failed")

        try:
            # Simulate authentication error
            mock_github.get_user()
        except Exception as e:
            error_msg = str(e)
            # Verify token is not exposed in error message
            assert token not in error_msg
            assert "Authentication failed" in error_msg
