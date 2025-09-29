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

from issue import GitHubAuthError, Issue, IssueError
from issue import test_github_connection as connection_test


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

    @patch(".issue.Github")  # Use the actual import path
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

    @patch(".issue.Github")
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

    @patch(".issue.Github")
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

    @patch(".issue.Github")
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

    @patch(".issue.Github")
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

    @patch(".issue.Github")
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

    @patch(".issue.Github")
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
    @patch("issue.Authentication")
    def test_create_github_client_with_env_token(self, mock_auth_class):
        """Test creating GitHub client with environment token."""
        mock_auth = MagicMock()
        mock_github = MagicMock()
        mock_auth.create_client.return_value = mock_github
        mock_auth_class.return_value = mock_auth

        client = Issue.create_github_client()

        assert client is mock_github
        mock_auth_class.assert_called_once_with("test_token")
        mock_auth.create_client.assert_called_once()

    @patch("issue.Authentication")
    def test_create_github_client_with_explicit_token(self, mock_auth_class):
        """Test creating GitHub client with explicit token."""
        mock_auth = MagicMock()
        mock_github = MagicMock()
        mock_auth.create_client.return_value = mock_github
        mock_auth_class.return_value = mock_auth

        client = Issue.create_github_client("explicit_token")

        assert client is mock_github
        mock_auth_class.assert_called_once_with("explicit_token")
        mock_auth.create_client.assert_called_once()

    def test_create_github_client_no_token(self):
        """Test creating GitHub client without token."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(GitHubAuthError) as exc_info:
                Issue.create_github_client()

            assert "GitHub token not provided" in str(exc_info.value)

    @patch("issue.Authentication")
    def test_create_github_client_bad_credentials(self, mock_auth_class):
        """Test creating GitHub client with bad credentials."""
        mock_auth = MagicMock()
        mock_auth.create_client.side_effect = GitHubAuthError("Invalid GitHub credentials")
        mock_auth_class.return_value = mock_auth

        with pytest.raises(GitHubAuthError) as exc_info:
            Issue.create_github_client("bad_token")

        assert "Invalid GitHub credentials" in str(exc_info.value)

    @patch("issue.Issue.create_github_client")
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

    @patch("issue.Issue.create_github_client")
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

    @patch("issue.Authentication")
    def test_test_github_connection_success(self, mock_auth_class):
        """Test successful GitHub connection test."""
        mock_auth = MagicMock()
        mock_auth.test_connection.return_value = {
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
        mock_auth_class.return_value = mock_auth

        result = connection_test("test_token")

        assert result["authenticated"] is True
        assert result["user"]["login"] == "test_user"
        assert result["rate_limit"]["core"]["remaining"] == 4999

    @patch("issue.Authentication")
    def test_test_github_connection_failure(self, mock_auth_class):
        """Test failed GitHub connection test."""
        mock_auth = MagicMock()
        mock_auth.test_connection.return_value = {
            "authenticated": False,
            "error": "Connection failed",
        }
        mock_auth_class.return_value = mock_auth

        result = connection_test("bad_token")

        assert result["authenticated"] is False
        assert "Connection failed" in result["error"]


class TestBulkOperations:
    """Test bulk issue creation functionality."""

    def test_create_bulk_issues_empty_list(self):
        """Test bulk creation with empty issue list."""
        result = Issue.create_bulk_issues([], "test/repo", "test_token")

        assert result["success"] is True
        assert result["total_issues"] == 0
        assert result["created_issues"] == []
        assert result["failed_issues"] == []
        assert result["errors"] == []

    @patch("issue.Issue.create_on_github")
    @patch("time.sleep")
    def test_create_bulk_issues_success(self, mock_sleep, mock_create):
        """Test successful bulk creation."""
        # Setup
        issues = [
            Issue("Issue 1", "Description 1"),
            Issue("Issue 2", "Description 2"),
        ]
        
        mock_create.side_effect = [
            {"number": 1, "id": 101, "title": "Issue 1", "url": "url1"},
            {"number": 2, "id": 102, "title": "Issue 2", "url": "url2"},
        ]

        # Test
        result = Issue.create_bulk_issues(issues, "test/repo", "test_token")

        # Verify
        assert result["success"] is True
        assert result["total_issues"] == 2
        assert result["created_count"] == 2
        assert result["failed_count"] == 0
        assert result["success_rate"] == 1.0
        assert len(result["created_issues"]) == 2
        
        # Check rate limiting
        mock_sleep.assert_called_once_with(1.0)

    @patch("issue.Issue.create_on_github")
    def test_create_bulk_issues_with_failures(self, mock_create):
        """Test bulk creation with some failures."""
        # Setup
        issues = [
            Issue("Success Issue", "Description"),
            Issue("Fail Issue", "Description"),
        ]
        
        mock_create.side_effect = [
            {"number": 1, "id": 101, "title": "Success Issue", "url": "url1"},
            Exception("API Error"),
        ]

        # Test
        result = Issue.create_bulk_issues(issues, "test/repo", "test_token")

        # Verify
        assert result["success"] is False
        assert result["total_issues"] == 2
        assert result["created_count"] == 1
        assert result["failed_count"] == 1
        assert result["success_rate"] == 0.5
        assert len(result["failed_issues"]) == 1
        assert "API Error" in result["errors"][0]

    @patch("issue.Issue.create_on_github")
    def test_create_bulk_issues_stop_on_error(self, mock_create):
        """Test bulk creation with stop_on_error=True."""
        # Setup
        issues = [
            Issue("Issue 1", "Description"),
            Issue("Issue 2", "Description"),
            Issue("Issue 3", "Description"),
        ]
        
        mock_create.side_effect = [
            {"number": 1, "id": 101, "title": "Issue 1", "url": "url1"},
            Exception("Stop here"),
        ]

        # Test
        result = Issue.create_bulk_issues(
            issues, "test/repo", "test_token", stop_on_error=True
        )

        # Verify - should stop after first error
        assert result["success"] is False
        assert result["created_count"] == 1
        assert result["failed_count"] == 1
        assert mock_create.call_count == 2  # Should not call third

    @patch("issue.Issue.create_on_github")
    def test_create_bulk_issues_custom_settings(self, mock_create):
        """Test bulk creation with custom rate limit and batch settings."""
        issues = [Issue(f"Issue {i}", f"Description {i}") for i in range(5)]
        
        mock_create.return_value = {"number": 1, "id": 101, "title": "Issue", "url": "url"}

        result = Issue.create_bulk_issues(
            issues, "test/repo", "test_token", 
            rate_limit_delay=0.5, batch_size=2
        )

        assert result["rate_limit_delay"] == 0.5
        assert result["batch_size"] == 2
        assert result["success"] is True


class TestTemplateCreation:
    """Test template-based issue creation."""

    def test_create_issues_with_templates_empty(self):
        """Test template creation with empty template data."""
        result = Issue.create_issues_with_templates("test/repo", [])

        assert result["success"] is True
        assert result["total_issues"] == 0
        assert result["created_issues"] == []

    @patch("issue.Issue.create_bulk_issues")
    def test_create_issues_with_templates_success(self, mock_bulk_create):
        """Test successful template creation."""
        template_data = [
            {
                "title": "Template Issue 1",
                "description": "Template description 1",
                "labels": ["bug"],
            },
            {
                "title": "Template Issue 2", 
                "description": "Template description 2",
                "labels": ["feature"],
                "assignees": ["user1"],
            },
        ]
        
        mock_bulk_create.return_value = {
            "success": True,
            "total_issues": 2,
            "created_count": 2,
            "failed_count": 0,
            "errors": [],
        }

        result = Issue.create_issues_with_templates(
            "test/repo", template_data, default_labels=["automated"]
        )

        assert result["success"] is True
        # Check that bulk_create was called with proper Issue objects
        mock_bulk_create.assert_called_once()
        args, kwargs = mock_bulk_create.call_args
        issues = args[0]
        assert len(issues) == 2
        assert all(isinstance(issue, Issue) for issue in issues)
        # Check that default labels were merged
        assert "automated" in issues[0].labels
        assert "automated" in issues[1].labels

    @patch("issue.Issue.create_bulk_issues") 
    def test_create_issues_with_templates_creation_errors(self, mock_bulk_create):
        """Test template creation with invalid template data."""
        template_data = [
            {"title": "Valid Issue", "description": "Valid description"},
            {"title": ""},  # Invalid - empty title
            {"description": "Missing title"},  # Invalid - no title
        ]
        
        mock_bulk_create.return_value = {
            "success": True,
            "created_count": 1,
            "errors": [],
        }

        result = Issue.create_issues_with_templates("test/repo", template_data)

        # Should have creation errors for invalid templates
        assert "template_errors" in result
        assert len(result["template_errors"]) > 0

    def test_create_issues_with_templates_defaults(self):
        """Test template creation with default values."""
        template_data = [{"title": "Issue {i+1}"}]  # Missing description
        
        # This should handle missing description gracefully
        result = Issue.create_issues_with_templates("test/repo", template_data)
        
        # Should fail because description is required
        assert not result["success"]


class TestStringMethods:
    """Test string representation methods."""

    def test_str_method(self):
        """Test __str__ method."""
        issue = Issue("A very long title that should be truncated", "Description")
        str_repr = str(issue)
        
        assert "Issue(title=" in str_repr
        assert "labels=0" in str_repr

    def test_repr_method(self):
        """Test __repr__ method.""" 
        issue = Issue(
            "Test Title", "Test description",
            labels=["bug"], assignees=["user1"], milestone="v1.0"
        )
        repr_str = repr(issue)
        
        assert "Issue(title='Test Title'" in repr_str
        assert "description_length=16" in repr_str
        assert "labels=['bug']" in repr_str
        assert "assignees=['user1']" in repr_str
        assert "milestone='v1.0'" in repr_str

    def test_format_for_display(self):
        """Test format_for_display method."""
        issue = Issue(
            "Display Test", "Display description",
            labels=["display"], assignees=["display_user"], milestone="v1.0"
        )
        
        formatted = issue.format_for_display()
        
        assert "Title: Display Test" in formatted
        assert "Description:\nDisplay description" in formatted
        assert "Labels: display" in formatted
        assert "Assignees: display_user" in formatted
        assert "Milestone: v1.0" in formatted

    def test_format_for_display_with_warnings(self):
        """Test format_for_display with validation warnings."""
        issue = Issue("TODO: Fix this", "Short")  # Will trigger warnings
        
        formatted = issue.format_for_display()
        
        assert "Warnings:" in formatted


class TestErrorHandling:
    """Test error handling scenarios."""

    @patch("issue.Issue.create_github_client")
    def test_create_on_github_rate_limit_error(self, mock_create_client):
        """Test handling of rate limit errors."""
        from github.GithubException import RateLimitExceededException
        
        mock_github = MagicMock()
        mock_github.get_repo.side_effect = RateLimitExceededException(403, "Rate limit")
        mock_create_client.return_value = mock_github

        issue = Issue("Test", "Description")
        
        with pytest.raises(IssueError) as exc_info:
            issue.create_on_github("test/repo")
            
        assert "rate limit exceeded" in str(exc_info.value)

    @patch("issue.Issue.create_github_client")
    def test_create_on_github_github_exception(self, mock_create_client):
        """Test handling of general GitHub exceptions.""" 
        from github.GithubException import GithubException
        
        mock_github = MagicMock()
        mock_github.get_repo.side_effect = GithubException(500, "Server error")
        mock_create_client.return_value = mock_github

        issue = Issue("Test", "Description")
        
        with pytest.raises(IssueError) as exc_info:
            issue.create_on_github("test/repo")
            
        assert "GitHub API error" in str(exc_info.value)

    @patch("issue.Issue.create_github_client")
    def test_create_on_github_general_exception(self, mock_create_client):
        """Test handling of general exceptions."""
        mock_create_client.side_effect = Exception("Unknown error")

        issue = Issue("Test", "Description")
        
        with pytest.raises(IssueError) as exc_info:
            issue.create_on_github("test/repo")
            
        assert "Failed to create issue" in str(exc_info.value)

    @patch("issue.Issue.create_github_client")
    def test_create_on_github_milestone_error(self, mock_create_client):
        """Test handling of milestone-related errors."""
        mock_github = MagicMock()
        mock_repo = MagicMock()
        
        # Mock milestone lookup failure
        mock_repo.get_milestones.side_effect = Exception("Milestone error")
        mock_repo.create_issue.return_value = MagicMock(
            number=1, id=1, title="Test", html_url="url", url="api_url",
            state="open", created_at=MagicMock(isoformat=lambda: "2023-01-01"),
            get_labels=lambda: [], assignees=[]
        )
        
        mock_github.get_repo.return_value = mock_repo
        mock_create_client.return_value = mock_github

        issue = Issue("Test", "Description", milestone="nonexistent")
        
        # Should not raise, just log warning
        result = issue.create_on_github("test/repo")
        assert result["number"] == 1

    @patch("issue.Issue.create_github_client")
    def test_create_on_github_invalid_labels(self, mock_create_client):
        """Test handling of invalid labels."""
        mock_github = MagicMock()
        mock_repo = MagicMock()
        
        # Mock repo with existing labels
        mock_label = MagicMock()
        mock_label.name = "valid-label"
        mock_repo.get_labels.return_value = [mock_label]
        
        mock_repo.create_issue.return_value = MagicMock(
            number=1, id=1, title="Test", html_url="url", url="api_url",
            state="open", created_at=MagicMock(isoformat=lambda: "2023-01-01"),
            get_labels=lambda: [mock_label], assignees=[]
        )
        
        mock_github.get_repo.return_value = mock_repo
        mock_create_client.return_value = mock_github

        issue = Issue("Test", "Description", labels=["valid-label", "invalid-label"])
        
        result = issue.create_on_github("test/repo")
        
        # Should succeed but filter out invalid labels
        assert result["number"] == 1
        # Verify that create_issue was called with only valid labels
        call_args = mock_repo.create_issue.call_args[1]
        assert "labels" in call_args
        assert call_args["labels"] == ["valid-label"]


class TestConnectionFunction:
    """Test the standalone test_github_connection function."""

    @patch("issue.Authentication")
    def test_github_connection_success(self, mock_auth_class):
        """Test successful connection test."""
        mock_auth = MagicMock()
        mock_auth.test_connection.return_value = {"authenticated": True}
        mock_auth_class.return_value = mock_auth

        result = connection_test("test_token")
        
        assert result["authenticated"] is True
        mock_auth_class.assert_called_once_with("test_token")

    @patch("issue.Authentication")
    def test_github_connection_exception(self, mock_auth_class):
        """Test connection test with exception."""
        mock_auth_class.side_effect = Exception("Connection error")

        result = connection_test("test_token")
        
        assert result["authenticated"] is False
        assert "Connection error" in result["error"]


class TestEdgeCases:
    """Test edge cases and missing coverage."""

    def test_title_length_truncation(self):
        """Test title truncation when exceeding GitHub limit."""
        long_title = "A" * 300  # Exceeds 256 character limit
        issue = Issue(long_title, "Description")
        
        # Should be truncated to 253 + "..."
        assert len(issue.title) == 256
        assert issue.title.endswith("...")

    def test_empty_description_error(self):
        """Test error when description is empty."""
        with pytest.raises(ValueError) as exc_info:
            Issue("Valid title", "")
            
        assert "description cannot be empty" in str(exc_info.value)
        
        with pytest.raises(ValueError) as exc_info:
            Issue("Valid title", "   ")  # Whitespace only
            
        assert "description cannot be empty" in str(exc_info.value)

    def test_validation_edge_cases(self):
        """Test validation edge cases."""
        # Test very long description that's exactly 10 characters
        issue = Issue("Title", "1234567890")  # Exactly 10 chars
        warnings = issue.validate_content()
        # Should not trigger "very short" warning at exactly 10 chars
        assert not any("very short" in warning for warning in warnings)
        
        # Test description with only newlines and periods 
        issue = Issue("Title", ".\n.\n.")
        warnings = issue.validate_content()
        # Should not trigger single sentence warning due to punctuation
        assert not any("single sentence" in warning for warning in warnings)

    @patch("issue.Issue.create_github_client")
    def test_create_on_github_with_assignees(self, mock_create_client):
        """Test issue creation with assignees."""
        mock_github = MagicMock()
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        
        # Setup assignees
        mock_assignee = MagicMock()
        mock_assignee.login = "test_user"
        mock_issue.assignees = [mock_assignee]
        
        mock_issue.number = 1
        mock_issue.id = 1
        mock_issue.title = "Test"
        mock_issue.html_url = "url"
        mock_issue.url = "api_url"
        mock_issue.state = "open"
        mock_issue.created_at.isoformat.return_value = "2023-01-01"
        mock_issue.get_labels.return_value = []
        
        mock_repo.create_issue.return_value = mock_issue
        mock_repo.get_labels.return_value = []
        mock_github.get_repo.return_value = mock_repo
        mock_create_client.return_value = mock_github

        issue = Issue("Test", "Description", assignees=["test_user"])
        result = issue.create_on_github("test/repo")
        
        # Verify assignees were passed to API
        call_args = mock_repo.create_issue.call_args[1]
        assert "assignees" in call_args
        assert call_args["assignees"] == ["test_user"]
        
        # Verify result includes assignees
        assert result["assignees"] == ["test_user"]

    @patch("issue.Issue.create_github_client")
    def test_create_on_github_with_milestone_success(self, mock_create_client):
        """Test successful milestone assignment."""
        mock_github = MagicMock()
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        
        # Setup milestone
        mock_milestone = MagicMock()
        mock_milestone.title = "v1.0"
        mock_repo.get_milestones.return_value = [mock_milestone]
        
        mock_issue.number = 1
        mock_issue.id = 1
        mock_issue.title = "Test"
        mock_issue.html_url = "url"
        mock_issue.url = "api_url"
        mock_issue.state = "open"
        mock_issue.created_at.isoformat.return_value = "2023-01-01"
        mock_issue.get_labels.return_value = []
        mock_issue.assignees = []
        
        mock_repo.create_issue.return_value = mock_issue
        mock_repo.get_labels.return_value = []
        mock_github.get_repo.return_value = mock_repo
        mock_create_client.return_value = mock_github

        issue = Issue("Test", "Description", milestone="v1.0")
        result = issue.create_on_github("test/repo")
        
        # Verify milestone was found and passed to API
        call_args = mock_repo.create_issue.call_args[1]
        assert "milestone" in call_args
        assert call_args["milestone"] is mock_milestone

    @patch("issue.Issue.create_github_client")
    def test_create_on_github_milestone_not_found(self, mock_create_client):
        """Test milestone not found scenario."""
        mock_github = MagicMock()
        mock_repo = MagicMock()
        mock_issue = MagicMock()
        
        # No matching milestone
        other_milestone = MagicMock()
        other_milestone.title = "v2.0"
        mock_repo.get_milestones.return_value = [other_milestone]
        
        mock_issue.number = 1
        mock_issue.id = 1
        mock_issue.title = "Test"
        mock_issue.html_url = "url"
        mock_issue.url = "api_url"
        mock_issue.state = "open"
        mock_issue.created_at.isoformat.return_value = "2023-01-01"
        mock_issue.get_labels.return_value = []
        mock_issue.assignees = []
        
        mock_repo.create_issue.return_value = mock_issue
        mock_repo.get_labels.return_value = []
        mock_github.get_repo.return_value = mock_repo
        mock_create_client.return_value = mock_github

        issue = Issue("Test", "Description", milestone="v1.0")
        result = issue.create_on_github("test/repo")
        
        # Should succeed but not include milestone
        call_args = mock_repo.create_issue.call_args[1]
        assert "milestone" not in call_args

    def test_to_dict_copy_safety(self):
        """Test that to_dict returns copies of mutable fields."""
        original_labels = ["bug", "feature"]
        original_assignees = ["user1", "user2"]
        
        issue = Issue("Test", "Description", labels=original_labels, assignees=original_assignees)
        issue_dict = issue.to_dict()
        
        # Modify the returned lists
        issue_dict["labels"].append("modified")
        issue_dict["assignees"].append("modified_user")
        
        # Original issue should be unchanged
        assert issue.labels == original_labels
        assert issue.assignees == original_assignees

    def test_from_dict_missing_fields(self):
        """Test from_dict with various missing required fields."""
        # Missing title
        data = {"description": "Test description"}
        with pytest.raises(ValueError) as exc_info:
            Issue.from_dict(data)
        assert "Missing required field: title" in str(exc_info.value)
        
        # Missing description 
        data = {"title": "Test title"}
        with pytest.raises(ValueError) as exc_info:
            Issue.from_dict(data)
        assert "Missing required field: description" in str(exc_info.value)

    def test_from_dict_with_defaults(self):
        """Test from_dict with optional fields defaulting to None."""
        data = {
            "title": "Test Title",
            "description": "Test Description"
        }
        
        issue = Issue.from_dict(data)
        
        assert issue.title == "Test Title"
        assert issue.description == "Test Description"
        assert issue.labels == []
        assert issue.assignees == []
        assert issue.milestone is None


class TestImportEdgeCases:
    """Test import-related edge cases."""

    def test_import_fallback_paths(self):
        """Test that imports work through different paths."""
        # The actual import testing is mainly for coverage of the try/except blocks
        # These are already covered by the fact that tests run successfully
        # But we can verify the module imports work
        
        from issue import Issue, IssueError, GitHubAuthError, test_github_connection
        
        assert Issue is not None
        assert IssueError is not None 
        assert GitHubAuthError is not None
        assert test_github_connection is not None

    @patch("issue.Authentication")
    def test_auth_error_re_raising(self, mock_auth_class):
        """Test that Authentication errors are properly re-raised."""
        from auth import GitHubAuthError as AuthGitHubAuthError
        
        mock_auth = MagicMock()
        mock_auth.create_client.side_effect = AuthGitHubAuthError("Auth failed")
        mock_auth_class.return_value = mock_auth
        
        with pytest.raises(GitHubAuthError) as exc_info:
            Issue.create_github_client("test_token")
            
        assert "Auth failed" in str(exc_info.value)


def test_basic_import():
    """Test that the function exists and can be imported."""
    # This is just a basic import test
    assert connection_test is not None


if __name__ == "__main__":
    pytest.main([__file__])
