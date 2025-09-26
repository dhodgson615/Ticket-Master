"""
Tests for the Authentication class.
"""

import os
# Add src to path for imports
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master.auth import (Authentication, AuthenticationError,
                                GitHubAuthError)


class TestAuthentication:
    """Test cases for Authentication class."""
    
    def test_init_with_token(self):
        """Test initialization with token."""
        auth = Authentication("test_token")
        assert auth.token == "test_token"
        assert auth.logger is not None
    
    def test_init_without_token(self):
        """Test initialization without token."""
        auth = Authentication()
        assert auth.token is None
        assert auth.logger is not None
    
    def test_get_token_from_instance(self):
        """Test get_token with instance token."""
        auth = Authentication("instance_token")
        token = auth.get_token()
        assert token == "instance_token"

    @patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"})
    def test_get_token_from_environment(self):
        """Test get_token from environment variable."""
        auth = Authentication()
        token = auth.get_token()
        assert token == "env_token"
    
    def test_get_token_instance_overrides_env(self):
        """Test that instance token overrides environment token."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            auth = Authentication("instance_token")
            token = auth.get_token()
            assert token == "instance_token"
    
    def test_get_token_no_token_available(self):
        """Test get_token when no token is available."""
        with patch.dict(os.environ, {}, clear=True):
            auth = Authentication()
            with pytest.raises(GitHubAuthError) as exc_info:
                auth.get_token()
            assert "GitHub token not provided" in str(exc_info.value)

    def test_str_representation_with_token(self):
        """Test string representation with token."""
        auth = Authentication("test_token")
        str_repr = str(auth)
        assert "Authentication(has_token=True)" == str_repr

    def test_str_representation_without_token(self):
        """Test string representation without token."""
        with patch.dict(os.environ, {}, clear=True):
            auth = Authentication()
            str_repr = str(auth)
            assert "Authentication(has_token=False)" == str_repr

    def test_str_representation_with_env_token(self):
        """Test string representation with environment token."""
        with patch.dict(os.environ, {"GITHUB_TOKEN": "env_token"}):
            auth = Authentication()
            str_repr = str(auth)
            assert "Authentication(has_token=True)" == str_repr

    def test_repr_representation(self):
        """Test repr representation."""
        with patch.dict(os.environ, {'GITHUB_TOKEN': 'env_token'}):
            auth = Authentication("instance_token")
            repr_str = repr(auth)
            expected = "Authentication(token_set=True, env_token_set=True, has_token=True)"
            assert repr_str == expected


class TestAuthenticationGitHubIntegration:
    """Test GitHub integration functionality."""
    
    @patch('ticket_master.auth.Github')
    def test_create_client_with_token(self, mock_github_class):
        """Test creating GitHub client with token."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
        
        auth = Authentication("test_token")
        client = auth.create_client()
        
        assert client is mock_github
        mock_github_class.assert_called_once()
        mock_github.get_user.assert_called_once()
    
    @patch('ticket_master.auth.Github')
    def test_create_client_token_parameter_overrides_instance(self, mock_github_class):
        """Test that token parameter overrides instance token."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
        
        auth = Authentication("instance_token")
        client = auth.create_client("override_token")
        
        assert client is mock_github
        mock_github_class.assert_called_once()
    
    @patch('ticket_master.auth.Github')
    def test_create_client_bad_credentials(self, mock_github_class):
        """Test creating GitHub client with bad credentials."""
        from github.GithubException import BadCredentialsException
        
        mock_github = MagicMock()
        mock_github.get_user.side_effect = BadCredentialsException(401, "Bad credentials")
        mock_github_class.return_value = mock_github
        
        auth = Authentication("bad_token")
        with pytest.raises(GitHubAuthError) as exc_info:
            auth.create_client()
        
        assert "Invalid GitHub credentials" in str(exc_info.value)
    
    def test_create_client_no_token(self):
        """Test creating GitHub client without token."""
        with patch.dict(os.environ, {}, clear=True):
            auth = Authentication()
            with pytest.raises(GitHubAuthError) as exc_info:
                auth.create_client()
            
            assert "GitHub token not provided" in str(exc_info.value)
    
    @patch('ticket_master.auth.Github')
    def test_is_authenticated_success(self, mock_github_class):
        """Test is_authenticated with valid credentials."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
        
        auth = Authentication("valid_token")
        result = auth.is_authenticated()
        
        assert result is True
    
    @patch('ticket_master.auth.Github')
    def test_is_authenticated_failure(self, mock_github_class):
        """Test is_authenticated with invalid credentials."""
        from github.GithubException import BadCredentialsException
        
        mock_github = MagicMock()
        mock_github.get_user.side_effect = BadCredentialsException(401, "Bad credentials")
        mock_github_class.return_value = mock_github
        
        auth = Authentication("invalid_token")
        result = auth.is_authenticated()
        
        assert result is False
    
    @patch('ticket_master.auth.Github')
    def test_get_user_info(self, mock_github_class):
        """Test getting user information."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        
        mock_user.login = "test_user"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.public_repos = 10
        mock_user.followers = 5
        mock_user.following = 3
        mock_user.created_at.isoformat.return_value = "2020-01-01T00:00:00"
        mock_user.updated_at.isoformat.return_value = "2023-01-01T00:00:00"
        
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
        
        auth = Authentication("valid_token")
        user_info = auth.get_user_info()
        
        expected = {
            "login": "test_user",
            "name": "Test User",
            "email": "test@example.com",
            "public_repos": 10,
            "followers": 5,
            "following": 3,
            "created_at": "2020-01-01T00:00:00",
            "updated_at": "2023-01-01T00:00:00",
        }
        
        assert user_info == expected
    
    @patch('ticket_master.auth.Github')
    def test_test_connection_success(self, mock_github_class):
        """Test successful connection test."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_rate_limit = MagicMock()
        mock_core = MagicMock()
        
        mock_user.login = "test_user"
        mock_user.name = "Test User"
        mock_user.email = "test@example.com"
        mock_user.public_repos = 10
        mock_user.followers = 5
        
        mock_core.limit = 5000
        mock_core.remaining = 4999
        mock_core.reset.isoformat.return_value = "2023-01-01T01:00:00"
        mock_rate_limit.core = mock_core
        
        mock_github.get_user.return_value = mock_user
        mock_github.get_rate_limit.return_value = mock_rate_limit
        mock_github_class.return_value = mock_github
        
        auth = Authentication("valid_token")
        result = auth.test_connection()
        
        assert result['authenticated'] is True
        assert result['user']['login'] == "test_user"
        assert result['rate_limit']['core']['limit'] == 5000
    
    @patch('ticket_master.auth.Github')
    def test_test_connection_failure(self, mock_github_class):
        """Test failed connection test."""
        from github.GithubException import BadCredentialsException
        
        mock_github = MagicMock()
        mock_github.get_user.side_effect = BadCredentialsException(401, "Bad credentials")
        mock_github_class.return_value = mock_github
        
        auth = Authentication("invalid_token")
        result = auth.test_connection()
        
        assert result['authenticated'] is False
        assert 'error' in result


class TestAuthenticationErrorHandling:
    """Test error handling in Authentication class."""
    
    def test_authentication_error_inheritance(self):
        """Test that AuthenticationError inherits from Exception."""
        error = AuthenticationError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"
    
    def test_github_auth_error_inheritance(self):
        """Test that GitHubAuthError inherits from AuthenticationError."""
        error = GitHubAuthError("auth error")
        assert isinstance(error, AuthenticationError)
        assert isinstance(error, Exception)
        assert str(error) == "auth error"


def test_basic_import():
    """Test that the Authentication class can be imported."""
    from ticket_master.auth import (Authentication, AuthenticationError,
                                    GitHubAuthError)

    assert Authentication is not None
    assert AuthenticationError is not None
    assert GitHubAuthError is not None


if __name__ == '__main__':
    pytest.main([__file__])