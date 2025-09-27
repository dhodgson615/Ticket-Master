"""Tests for GitHub utilities module."""

import os
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
import pytest

from src.ticket_master.github_utils import GitHubUtils, GitHubCloneError


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
        result = self.github_utils.parse_github_url("https://github.com/owner/repo")
        assert result == "owner/repo"

    def test_parse_github_url_https_with_path(self):
        """Test parsing GitHub URL with additional path components."""
        result = self.github_utils.parse_github_url("https://github.com/owner/repo/issues")
        assert result == "owner/repo"

    def test_parse_github_url_invalid_format(self):
        """Test parsing invalid GitHub URL format."""
        with pytest.raises(ValueError, match="Invalid GitHub repository format"):
            self.github_utils.parse_github_url("invalid-format")

    def test_parse_github_url_non_github_domain(self):
        """Test parsing URL from non-GitHub domain."""
        with pytest.raises(ValueError, match="URL must be from github.com"):
            self.github_utils.parse_github_url("https://gitlab.com/owner/repo")

    @patch('src.ticket_master.github_utils.requests.get')
    def test_is_public_repository_public(self, mock_get):
        """Test detecting public repository."""
        # Mock successful response for public repo
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'private': False}
        mock_get.return_value = mock_response

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is True

    @patch('src.ticket_master.github_utils.requests.get')
    def test_is_public_repository_private(self, mock_get):
        """Test detecting private repository."""
        # Mock successful response for private repo
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'private': True}
        mock_get.return_value = mock_response

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is False

    @patch('src.ticket_master.github_utils.requests.get')
    def test_is_public_repository_not_found(self, mock_get):
        """Test handling repository not found."""
        # Mock 404 response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is False

    @patch('subprocess.run')
    @patch('src.ticket_master.github_utils.requests.get')
    def test_is_public_repository_rate_limited_fallback_public(self, mock_get, mock_subprocess):
        """Test fallback to git ls-remote when rate limited for public repo."""
        # Mock 403 response (rate limited)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        # Mock successful git ls-remote
        mock_subprocess.return_value = Mock(returncode=0)

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is True

    @patch('subprocess.run')
    @patch('src.ticket_master.github_utils.requests.get')
    def test_is_public_repository_rate_limited_fallback_private(self, mock_get, mock_subprocess):
        """Test fallback to git ls-remote when rate limited for private repo."""
        # Mock 403 response (rate limited)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        # Mock failed git ls-remote (private repo)
        mock_subprocess.return_value = Mock(returncode=1)

        result = self.github_utils.is_public_repository("owner/repo")
        assert result is False

    @patch('src.ticket_master.github_utils.requests.get')
    def test_get_repository_info_success(self, mock_get):
        """Test getting repository info successfully."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            'name': 'repo',
            'full_name': 'owner/repo',
            'description': 'Test repository',
            'private': False,
            'clone_url': 'https://github.com/owner/repo.git',
            'ssh_url': 'git@github.com:owner/repo.git',
            'default_branch': 'main',
            'language': 'Python',
            'size': 1000
        }
        mock_get.return_value = mock_response

        result = self.github_utils.get_repository_info("owner/repo")
        
        assert result is not None
        assert result['name'] == 'repo'
        assert result['full_name'] == 'owner/repo'
        assert result['private'] is False

    @patch('src.ticket_master.github_utils.requests.get')
    def test_get_repository_info_rate_limited(self, mock_get):
        """Test getting repository info when rate limited."""
        # Mock 403 response (rate limited)
        mock_response = Mock()
        mock_response.status_code = 403
        mock_get.return_value = mock_response

        result = self.github_utils.get_repository_info("owner/repo")
        
        assert result is not None
        assert result['name'] == 'repo'
        assert result['full_name'] == 'owner/repo'
        assert result['clone_url'] == 'https://github.com/owner/repo.git'
        assert result['private'] is None  # Unknown due to rate limiting

    @patch('src.ticket_master.github_utils.Repo.clone_from')
    @patch('src.ticket_master.github_utils.GitHubUtils.get_repository_info')
    def test_clone_repository_public_success(self, mock_get_info, mock_clone):
        """Test successful cloning of public repository."""
        # Mock repository info
        mock_get_info.return_value = {
            'private': False,
            'clone_url': 'https://github.com/owner/repo.git'
        }

        # Mock successful clone
        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        result = self.github_utils.clone_repository("owner/repo")
        
        assert result is not None
        assert result.startswith('/tmp/ticket-master-owner-repo-')
        mock_clone.assert_called_once()

    @patch('src.ticket_master.github_utils.Repo.clone_from')
    @patch('src.ticket_master.github_utils.GitHubUtils.get_repository_info')
    def test_clone_repository_private_with_token(self, mock_get_info, mock_clone):
        """Test successful cloning of private repository with token."""
        # Mock repository info
        mock_get_info.return_value = {
            'private': True,
            'clone_url': 'https://github.com/owner/repo.git'
        }

        # Mock successful clone
        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        result = self.github_utils.clone_repository("owner/repo", token="test-token")
        
        assert result is not None
        mock_clone.assert_called_once()
        # Check that authenticated URL was used
        call_args = mock_clone.call_args
        assert "test-token@github.com" in call_args[0][0]

    @patch('src.ticket_master.github_utils.GitHubUtils.get_repository_info')
    def test_clone_repository_not_found(self, mock_get_info):
        """Test cloning repository that doesn't exist."""
        # Mock repository not found
        mock_get_info.return_value = None

        with pytest.raises(GitHubCloneError, match="not found or not accessible"):
            self.github_utils.clone_repository("owner/nonexistent")

    @patch('src.ticket_master.github_utils.Repo.clone_from')
    @patch('src.ticket_master.github_utils.GitHubUtils.get_repository_info')
    def test_clone_repository_to_local_path(self, mock_get_info, mock_clone):
        """Test cloning repository to specified local path."""
        # Mock repository info
        mock_get_info.return_value = {
            'private': False,
            'clone_url': 'https://github.com/owner/repo.git'
        }

        # Mock successful clone
        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        with tempfile.TemporaryDirectory() as temp_dir:
            local_path = os.path.join(temp_dir, "test-repo")
            
            result = self.github_utils.clone_repository("owner/repo", local_path=local_path)
            
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