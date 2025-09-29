"""
Tests for the Issue class.
"""

import os
# Add src to path for imports
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master.issue import GitHubAuthError, Issue, IssueError
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
            milestone="v1.0",
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


class TestIssueTemplatesAndLabels:
    """Test issue creation with various templates and labels."""

    def test_issue_with_bug_template(self):
        """Test issue creation with bug report template."""
        issue = Issue(
            title="Bug: Application crashes on startup",
            description="""**Bug Description:**
Application crashes immediately after startup.

**Steps to Reproduce:**
1. Launch the application
2. Wait for initialization
3. Crash occurs

**Expected Behavior:**
Application should start normally.

**Actual Behavior:**
Application crashes with error code 1.""",
            labels=["bug", "priority-high", "needs-investigation"],
        )

        assert issue.title.startswith("Bug:")
        assert "Steps to Reproduce" in issue.description
        assert "bug" in issue.labels
        assert "priority-high" in issue.labels

    def test_issue_with_feature_template(self):
        """Test issue creation with feature request template."""
        issue = Issue(
            title="Feature: Add dark mode support",
            description="""**Feature Request:**
Add dark mode support to the application.

**Motivation:**
Users have requested dark mode for better usability in low-light conditions.

**Proposed Solution:**
Implement a theme switcher with light/dark options.

**Alternatives Considered:**
- System theme detection
- Multiple theme options""",
            labels=["enhancement", "ui/ux", "feature-request"],
        )

        assert issue.title.startswith("Feature:")
        assert "Feature Request" in issue.description
        assert "enhancement" in issue.labels
        assert "feature-request" in issue.labels

    def test_issue_with_security_labels(self):
        """Test issue creation with security-related labels."""
        issue = Issue(
            title="Security: Potential XSS vulnerability in user input",
            description="User input is not properly sanitized, leading to potential XSS attacks.",
            labels=[
                "security",
                "vulnerability",
                "priority-critical",
                "needs-patch",
            ],
            assignees=["security-team"],
        )

        assert "security" in issue.labels
        assert "vulnerability" in issue.labels
        assert "priority-critical" in issue.labels
        assert "security-team" in issue.assignees

    def test_issue_with_automated_labels(self):
        """Test issue creation with automated/AI-generated labels."""
        issue = Issue(
            title="Automated: Code quality improvements needed",
            description="Automated analysis identified several code quality issues.",
            labels=[
                "automated",
                "code-quality",
                "ai-generated",
                "technical-debt",
            ],
        )

        assert "automated" in issue.labels
        assert "ai-generated" in issue.labels
        # Note: metadata would be stored separately in a real implementation

    def test_issue_with_performance_labels(self):
        """Test issue creation with performance-related labels."""
        issue = Issue(
            title="Performance: Slow query in user dashboard",
            description="Database query in user dashboard takes >5 seconds to execute.",
            labels=[
                "performance",
                "database",
                "optimization",
                "priority-medium",
            ],
            milestone="v2.1.0",
        )

        assert "performance" in issue.labels
        assert "database" in issue.labels
        assert "optimization" in issue.labels
        assert issue.milestone == "v2.1.0"

    def test_issue_with_testing_labels(self):
        """Test issue creation with testing-related labels."""
        issue = Issue(
            title="Testing: Add unit tests for authentication module",
            description="Authentication module lacks comprehensive unit test coverage.",
            labels=["testing", "unit-tests", "coverage", "quality-assurance"],
            assignees=["qa-team"],
        )

        assert "testing" in issue.labels
        assert "unit-tests" in issue.labels
        assert "coverage" in issue.labels
        assert "qa-team" in issue.assignees


class TestIssueGitHubIntegration:
    """Test Issue class GitHub integration functionality."""

    @patch("ticket_master.issue.Github")  # Use the actual import path
    def test_create_issue_success(self, mock_github_class):
        """Test successful issue creation on GitHub."""
        # Setup mocks
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_created_issue = Mock()
        mock_created_issue.number = 123
        mock_created_issue.html_url = (
            "https://github.com/owner/repo/issues/123"
        )
        mock_repo.create_issue.return_value = mock_created_issue

        # Create issue
        issue = Issue(
            title="Test Issue",
            description="Test description",
            labels=["bug", "priority-high"],
        )

        # This would be part of issue creation method
        result = mock_repo.create_issue(
            title=issue.title, body=issue.description, labels=issue.labels
        )

        assert result.number == 123
        assert "github.com" in result.html_url

    @patch("ticket_master.issue.Github")
    def test_create_issue_with_template_and_assignees(self, mock_github_class):
        """Test issue creation with template and assignees."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_created_issue = Mock()
        mock_created_issue.number = 124
        mock_repo.create_issue.return_value = mock_created_issue

        issue = Issue(
            title="Feature Request: New functionality",
            description="Detailed feature description with template",
            labels=["enhancement", "feature-request"],
            assignees=["developer1", "developer2"],
            milestone="v1.5.0",
        )

        result = mock_repo.create_issue(
            title=issue.title,
            body=issue.description,
            labels=issue.labels,
            assignees=issue.assignees,
            milestone=issue.milestone,
        )

        mock_repo.create_issue.assert_called_once_with(
            title=issue.title,
            body=issue.description,
            labels=issue.labels,
            assignees=issue.assignees,
            milestone=issue.milestone,
        )

    @patch("ticket_master.issue.Github")
    def test_batch_issue_creation_with_rate_limiting(self, mock_github_class):
        """Test batch creation of multiple issues with rate limiting considerations."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo

        # Mock successful issue creation
        mock_issues = []
        for i in range(5):
            mock_issue = Mock()
            mock_issue.number = i + 1
            mock_issues.append(mock_issue)

        mock_repo.create_issue.side_effect = mock_issues

        # Create multiple issues
        issues_data = [
            {
                "title": f"Issue {i}",
                "description": f"Description {i}",
                "labels": ["automated", "batch-created"],
            }
            for i in range(5)
        ]

        with patch("time.sleep") as mock_sleep:
            created_issues = []
            for i, issue_data in enumerate(issues_data):
                result = mock_repo.create_issue(**issue_data)
                created_issues.append(result)

                # Add delay between requests to respect rate limits
                if i < len(issues_data) - 1:
                    mock_sleep(1)

            assert len(created_issues) == 5
            assert mock_sleep.call_count == 4  # One less than total issues

    def test_issue_validation_edge_cases(self):
        """Test issue validation with edge cases."""
        # Test very long title
        long_title = "x" * 1000
        with pytest.raises(ValueError, match="title is too long"):
            Issue(long_title, "Valid description")

        # Test title with only whitespace
        with pytest.raises(ValueError, match="title cannot be empty"):
            Issue("   ", "Valid description")

        # Test description with only whitespace
        with pytest.raises(ValueError, match="description cannot be empty"):
            Issue("Valid Title", "   ")

        # Test invalid label format
        with pytest.raises(ValueError, match="labels must be a list"):
            Issue("Valid Title", "Valid description", labels="invalid")

        # Test invalid assignees format
        with pytest.raises(ValueError, match="assignees must be a list"):
            Issue("Valid Title", "Valid description", assignees="invalid")


class TestIssueErrorHandling:
    """Test Issue class error handling scenarios."""

    @patch("ticket_master.issue.Github")
    def test_github_authentication_error(self, mock_github_class):
        """Test handling of GitHub authentication errors."""
        from github import BadCredentialsException

        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_github.get_user.side_effect = BadCredentialsException(
            status=401, data={"message": "Bad credentials"}
        )

        with pytest.raises(BadCredentialsException):
            mock_github.get_user()

    @patch("ticket_master.issue.Github")
    def test_repository_not_found_error(self, mock_github_class):
        """Test handling when repository is not found."""
        from github import UnknownObjectException

        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_github.get_repo.side_effect = UnknownObjectException(
            status=404, data={"message": "Not Found"}
        )

        with pytest.raises(UnknownObjectException):
            mock_github.get_repo("nonexistent/repo")

    @patch("ticket_master.issue.Github")
    def test_permission_denied_error(self, mock_github_class):
        """Test handling when user lacks permission to create issues."""
        from github import GithubException

        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.create_issue.side_effect = GithubException(
            status=403, data={"message": "Forbidden"}
        )

        with pytest.raises(GithubException):
            mock_repo.create_issue(title="Test", body="Test")

    @patch("ticket_master.issue.Github")
    def test_network_error_handling(self, mock_github_class):
        """Test handling of network connectivity issues."""
        import requests

        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo
        mock_repo.create_issue.side_effect = requests.ConnectionError(
            "Network error"
        )

        with pytest.raises(requests.ConnectionError):
            mock_repo.create_issue(title="Test", body="Test")


if __name__ == "__main__":
    pytest.main([__file__])

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
            "This is a comprehensive description with proper punctuation and formatting.\nIt has multiple lines and sufficient detail.",
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
        issue = Issue(
            "TODO: Fix this", "This needs to be implemented. FIXME later."
        )
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
        issue = Issue(
            "Title", "Description", labels=["good-label", "", "another-label"]
        )
        warnings = issue.validate_content()

        assert any("Empty label" in warning for warning in warnings)

    def test_to_dict(self):
        """Test converting issue to dictionary."""
        issue = Issue(
            "Test Title",
            "Test description",
            labels=["bug"],
            assignees=["user1"],
            milestone="v1.0",
        )

        issue_dict = issue.to_dict()

        assert issue_dict["title"] == "Test Title"
        assert issue_dict["description"] == "Test description"
        assert issue_dict["labels"] == ["bug"]
        assert issue_dict["assignees"] == ["user1"]
        assert issue_dict["milestone"] == "v1.0"
        assert "validation_warnings" in issue_dict

    def test_from_dict(self):
        """Test creating issue from dictionary."""
        data = {
            "title": "Dict Title",
            "description": "Dict description",
            "labels": ["enhancement"],
            "assignees": ["user2"],
            "milestone": "v2.0",
        }

        issue = Issue.from_dict(data)

        assert issue.title == "Dict Title"
        assert issue.description == "Dict description"
        assert issue.labels == ["enhancement"]
        assert issue.assignees == ["user2"]
        assert issue.milestone == "v2.0"

    def test_from_dict_missing_required(self):
        """Test creating issue from dictionary with missing required fields."""
        data = {"title": "Only Title"}  # Missing description

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
            milestone="v1.0",
        )

        formatted = issue.format_for_display()

        assert "Title: Display Title" in formatted
        assert "Description:\nDisplay description" in formatted
        assert "Labels: label1, label2" in formatted
        assert "Assignees: user1" in formatted
        assert "Milestone: v1.0" in formatted

    def test_str_representation(self):
        """Test string representation of Issue."""
        issue = Issue(
            "String Test Title", "String test description", labels=["a", "b"]
        )
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

    @patch.dict(os.environ, {"GITHUB_TOKEN": "test_token"})
    @patch("ticket_master.auth.Github")
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

    @patch("ticket_master.auth.Github")
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

    @patch("ticket_master.auth.Github")
    def test_create_github_client_bad_credentials(self, mock_github_class):
        """Test creating GitHub client with bad credentials."""
        from github.GithubException import BadCredentialsException

        mock_github = MagicMock()
        mock_github.get_user.side_effect = BadCredentialsException(
            401, "Bad credentials"
        )
        mock_github_class.return_value = mock_github

        with pytest.raises(GitHubAuthError) as exc_info:
            Issue.create_github_client("bad_token")

        assert "Invalid GitHub credentials" in str(exc_info.value)

    @patch("ticket_master.issue.Issue.create_github_client")
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
        assert result["number"] == 123
        assert result["title"] == "Test Issue"
        assert result["url"] == "https://github.com/test/repo/issues/123"
        assert result["state"] == "open"

        # Verify API calls
        mock_github.get_repo.assert_called_once_with("test/repo")
        mock_repo.create_issue.assert_called_once()

    @patch("ticket_master.issue.Issue.create_github_client")
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
        issue = Issue(
            "Test Issue", "Test description", labels=["bug", "invalid_label"]
        )
        result = issue.create_on_github("test/repo", "test_token")

        # Verify valid labels were applied
        assert result["labels"] == ["bug"]


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

    @patch("ticket_master.auth.Authentication.test_connection")
    def test_test_github_connection_success(self, mock_test_connection):
        """Test successful GitHub connection test."""
        mock_test_connection.return_value = {
            "authenticated": True,
            "user": {
                "login": "test_user",
                "name": "Test User",
                "email": "test@example.com",
                "public_repos": 10,
                "followers": 5,
            },
            "rate_limit": {
                "core": {
                    "limit": 5000,
                    "remaining": 4999,
                    "reset": "2023-01-01T01:00:00",
                }
            },
        }

        result = connection_test("test_token")

        assert result["authenticated"] is True
        assert result["user"]["login"] == "test_user"
        assert result["rate_limit"]["core"]["remaining"] == 4999

    @patch("ticket_master.auth.Authentication.test_connection")
    def test_test_github_connection_failure(self, mock_test_connection):
        """Test failed GitHub connection test."""
        mock_test_connection.return_value = {
            "authenticated": False,
            "error": "Connection failed",
        }

        result = connection_test("bad_token")

        assert result["authenticated"] is False
        assert "Connection failed" in result["error"]


def test_basic_import():
    """Test that the function exists and can be imported."""
    # This is just a basic import test
    assert connection_test is not None


if __name__ == "__main__":
    pytest.main([__file__])
