"""
Tests for the Issue class.
"""

import pytest
import os
from unittest.mock import patch, MagicMock
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master.issue import Issue, IssueError, GitHubAuthError
from ticket_master.issue import test_github_connection as connection_test


class TestIssue:
    """Test cases for Issue class."""
    
    def test_init_valid_issue(self):
        """Test Issue initialization with valid parameters."""
        issue = Issue(
            title="Test Issue",
            description="This is a test issue description.",
            labels=["bug", "enhancement"],
            assignees=["user1", "user2"],
            milestone="v1.0"
        )
        
        assert issue.title == "Test Issue"
        assert issue.description == "This is a test issue description."
        assert issue.labels == ["bug", "enhancement"]
        assert issue.assignees == ["user1", "user2"]
        assert issue.milestone == "v1.0"
    
    def test_init_empty_title(self):
        """Test Issue initialization with empty title."""
        with pytest.raises(ValueError) as exc_info:
            Issue("", "Valid description")
        
        assert "title cannot be empty" in str(exc_info.value)
    
    def test_init_empty_description(self):
        """Test Issue initialization with empty description."""
        with pytest.raises(ValueError) as exc_info:
            Issue("Valid Title", "")
        
        assert "description cannot be empty" in str(exc_info.value)
    
    def test_init_whitespace_only_title(self):
        """Test Issue initialization with whitespace-only title."""
        with pytest.raises(ValueError):
            Issue("   ", "Valid description")
    
    def test_init_whitespace_only_description(self):
        """Test Issue initialization with whitespace-only description."""
        with pytest.raises(ValueError):
            Issue("Valid Title", "   ")
    
    def test_init_title_truncation(self):
        """Test that overly long titles are truncated."""
        long_title = "a" * 300  # Longer than GitHub's 256 character limit
        issue = Issue(long_title, "Valid description")
        
        assert len(issue.title) == 256
        assert issue.title.endswith("...")
    
    def test_init_default_values(self):
        """Test Issue initialization with default values."""
        issue = Issue("Test Title", "Test description")
        
        assert issue.labels == []
        assert issue.assignees == []
        assert issue.milestone is None
    
    def test_validate_content_valid_issue(self):
        """Test content validation for a valid issue."""
        issue = Issue(
            "Good title",
            "This is a comprehensive description with proper punctuation and formatting.\nIt has multiple lines and sufficient detail."
        )
        
        warnings = issue.validate_content()
        assert warnings == []
    
    def test_validate_content_short_description(self):
        """Test content validation with short description."""
        issue = Issue("Title", "Short")
        warnings = issue.validate_content()
        
        assert any("very short" in warning for warning in warnings)
    
    def test_validate_content_single_sentence(self):
        """Test content validation with single sentence description."""
        issue = Issue("Title", "This is a single sentence without formatting")
        warnings = issue.validate_content()
        
        assert any("single sentence" in warning for warning in warnings)
    
    def test_validate_content_placeholder_text(self):
        """Test content validation with placeholder text."""
        issue = Issue("TODO: Fix this", "This needs to be implemented. FIXME later.")
        warnings = issue.validate_content()
        
        assert any("placeholder text" in warning for warning in warnings)
    
    def test_validate_content_long_labels(self):
        """Test content validation with overly long labels."""
        long_label = "a" * 60
        issue = Issue("Title", "Description", labels=[long_label])
        warnings = issue.validate_content()
        
        assert any("very long" in warning for warning in warnings)
    
    def test_validate_content_empty_labels(self):
        """Test content validation with empty labels."""
        issue = Issue("Title", "Description", labels=["good-label", "", "another-label"])
        warnings = issue.validate_content()
        
        assert any("Empty label" in warning for warning in warnings)
    
    def test_to_dict(self):
        """Test converting issue to dictionary."""
        issue = Issue(
            "Test Title",
            "Test description",
            labels=["bug"],
            assignees=["user1"],
            milestone="v1.0"
        )
        
        issue_dict = issue.to_dict()
        
        assert issue_dict['title'] == "Test Title"
        assert issue_dict['description'] == "Test description"
        assert issue_dict['labels'] == ["bug"]
        assert issue_dict['assignees'] == ["user1"]
        assert issue_dict['milestone'] == "v1.0"
        assert 'validation_warnings' in issue_dict
    
    def test_from_dict(self):
        """Test creating issue from dictionary."""
        data = {
            'title': "Dict Title",
            'description': "Dict description",
            'labels': ["enhancement"],
            'assignees': ["user2"],
            'milestone': "v2.0"
        }
        
        issue = Issue.from_dict(data)
        
        assert issue.title == "Dict Title"
        assert issue.description == "Dict description"
        assert issue.labels == ["enhancement"]
        assert issue.assignees == ["user2"]
        assert issue.milestone == "v2.0"
    
    def test_from_dict_missing_required(self):
        """Test creating issue from dictionary with missing required fields."""
        data = {'title': "Only Title"}  # Missing description
        
        with pytest.raises(ValueError) as exc_info:
            Issue.from_dict(data)
        
        assert "Missing required field: description" in str(exc_info.value)
    
    def test_format_for_display(self):
        """Test formatting issue for display."""
        issue = Issue(
            "Display Title",
            "Display description",
            labels=["label1", "label2"],
            assignees=["user1"],
            milestone="v1.0"
        )
        
        formatted = issue.format_for_display()
        
        assert "Title: Display Title" in formatted
        assert "Description:\nDisplay description" in formatted
        assert "Labels: label1, label2" in formatted
        assert "Assignees: user1" in formatted
        assert "Milestone: v1.0" in formatted
    
    def test_str_representation(self):
        """Test string representation of Issue."""
        issue = Issue("String Test Title", "String test description", labels=["a", "b"])
        str_repr = str(issue)
        
        assert "Issue(" in str_repr
        assert "String Test Title" in str_repr
        assert "labels=2" in str_repr
    
    def test_repr_representation(self):
        """Test detailed string representation of Issue."""
        issue = Issue("Repr Title", "Repr description", labels=["test"])
        repr_str = repr(issue)
        
        assert "Issue(" in repr_str
        assert "title='Repr Title'" in repr_str
        assert "description_length=" in repr_str
        assert "labels=['test']" in repr_str


class TestIssueGitHubIntegration:
    """Test GitHub integration functionality."""
    
    @patch.dict(os.environ, {'GITHUB_TOKEN': 'test_token'})
    @patch('ticket_master.auth.Github')
    def test_create_github_client_with_env_token(self, mock_github_class):
        """Test creating GitHub client with environment token."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
        
        client = Issue.create_github_client()
        
        assert client is mock_github
        mock_github_class.assert_called_once()
        mock_github.get_user.assert_called_once()
    
    @patch('ticket_master.auth.Github')
    def test_create_github_client_with_explicit_token(self, mock_github_class):
        """Test creating GitHub client with explicit token."""
        mock_github = MagicMock()
        mock_user = MagicMock()
        mock_user.login = "test_user"
        mock_github.get_user.return_value = mock_user
        mock_github_class.return_value = mock_github
        
        client = Issue.create_github_client("explicit_token")
        
        assert client is mock_github
        mock_github_class.assert_called_once()
    
    def test_create_github_client_no_token(self):
        """Test creating GitHub client without token."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(GitHubAuthError) as exc_info:
                Issue.create_github_client()
            
            assert "GitHub token not provided" in str(exc_info.value)
    
    @patch('ticket_master.auth.Github')
    def test_create_github_client_bad_credentials(self, mock_github_class):
        """Test creating GitHub client with bad credentials."""
        from github.GithubException import BadCredentialsException
        
        mock_github = MagicMock()
        mock_github.get_user.side_effect = BadCredentialsException(401, "Bad credentials")
        mock_github_class.return_value = mock_github
        
        with pytest.raises(GitHubAuthError) as exc_info:
            Issue.create_github_client("bad_token")
        
        assert "Invalid GitHub credentials" in str(exc_info.value)
    
    @patch('ticket_master.issue.Issue.create_github_client')
    def test_create_on_github_success(self, mock_create_client):
        """Test successful issue creation on GitHub."""
        # Setup mocks
        mock_github = MagicMock()
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        
        mock_issue.number = 123
        mock_issue.id = 456
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "https://github.com/test/repo/issues/123"
        mock_issue.url = "https://api.github.com/repos/test/repo/issues/123"
        mock_issue.state = "open"
        mock_issue.created_at.isoformat.return_value = "2023-01-01T00:00:00"
        mock_issue.get_labels.return_value = []
        mock_issue.assignees = []
        
        mock_repo.create_issue.return_value = mock_issue
        mock_repo.get_labels.return_value = []
        mock_github.get_repo.return_value = mock_repo
        mock_create_client.return_value = mock_github
        
        # Create and test issue
        issue = Issue("Test Issue", "Test description")
        result = issue.create_on_github("test/repo", "test_token")
        
        # Verify results
        assert result['number'] == 123
        assert result['title'] == "Test Issue"
        assert result['url'] == "https://github.com/test/repo/issues/123"
        assert result['state'] == "open"
        
        # Verify API calls
        mock_github.get_repo.assert_called_once_with("test/repo")
        mock_repo.create_issue.assert_called_once()
    
    @patch('ticket_master.issue.Issue.create_github_client')
    def test_create_on_github_with_labels(self, mock_create_client):
        """Test issue creation with labels."""
        # Setup mocks
        mock_github = MagicMock()
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        mock_label = MagicMock()
        mock_label.name = "bug"
        
        mock_issue.number = 123
        mock_issue.id = 456
        mock_issue.title = "Test Issue"
        mock_issue.html_url = "https://github.com/test/repo/issues/123"
        mock_issue.url = "https://api.github.com/repos/test/repo/issues/123"
        mock_issue.state = "open"
        mock_issue.created_at.isoformat.return_value = "2023-01-01T00:00:00"
        mock_issue.get_labels.return_value = [mock_label]
        mock_issue.assignees = []
        
        mock_repo.create_issue.return_value = mock_issue
        mock_repo.get_labels.return_value = [mock_label]
        mock_github.get_repo.return_value = mock_repo
        mock_create_client.return_value = mock_github
        
        # Create issue with labels
        issue = Issue("Test Issue", "Test description", labels=["bug", "invalid_label"])
        result = issue.create_on_github("test/repo", "test_token")
        
        # Verify valid labels were applied
        assert result['labels'] == ["bug"]


class TestIssueErrorHandling:
    """Test error handling in Issue class."""
    
    def test_issue_error_inheritance(self):
        """Test that IssueError inherits from Exception."""
        error = IssueError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"
    
    def test_github_auth_error_inheritance(self):
        """Test that GitHubAuthError inherits from IssueError."""
        error = GitHubAuthError("auth error")
        assert isinstance(error, IssueError)
        assert isinstance(error, Exception)
        assert str(error) == "auth error"


class TestGitHubConnection:
    """Test GitHub connection testing functionality."""
    
    @patch('ticket_master.auth.Authentication.test_connection')
    def test_test_github_connection_success(self, mock_test_connection):
        """Test successful GitHub connection test."""
        mock_test_connection.return_value = {
            'authenticated': True,
            'user': {
                'login': 'test_user',
                'name': 'Test User',
                'email': 'test@example.com',
                'public_repos': 10,
                'followers': 5,
            },
            'rate_limit': {
                'core': {
                    'limit': 5000,
                    'remaining': 4999,
                    'reset': '2023-01-01T01:00:00',
                }
            },
        }
        
        result = connection_test("test_token")
        
        assert result['authenticated'] is True
        assert result['user']['login'] == "test_user"
        assert result['rate_limit']['core']['remaining'] == 4999
    
    @patch('ticket_master.auth.Authentication.test_connection')
    def test_test_github_connection_failure(self, mock_test_connection):
        """Test failed GitHub connection test."""
        mock_test_connection.return_value = {
            'authenticated': False,
            'error': 'Connection failed'
        }
        
        result = connection_test("bad_token")
        
        assert result['authenticated'] is False
        assert "Connection failed" in result['error']


def test_basic_import():
    """Test that the function exists and can be imported."""
    # This is just a basic import test
    assert connection_test is not None


if __name__ == '__main__':
    pytest.main([__file__])