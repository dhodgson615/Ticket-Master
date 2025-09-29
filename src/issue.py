import logging
import os
import subprocess
import sys
from typing import Any, Dict, List, Optional

try:
    from github import Auth, Github
    from github.GithubException import (
        BadCredentialsException,
        GithubException,
        RateLimitExceededException,
    )

except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "PyGithub>=1.59.1"]
    )

    from github import Github
    from github.GithubException import (
        GithubException,
        RateLimitExceededException,
    )

try:
    from auth import Authentication as Authentication

except ImportError:
    from auth import Authentication as Authentication

try:
    from auth import GitHubAuthError as AuthGitHubAuthError

except ImportError:
    from auth import GitHubAuthError as AuthGitHubAuthError


class IssueError(Exception):
    """Custom exception for issue-related errors."""

    pass


class GitHubAuthError(IssueError):
    """Exception for GitHub authentication errors."""

    pass


class Issue:
    """Handles GitHub issue creation and management.

    This class provides methods to create, validate, and manage GitHub issues
    using the GitHub API with proper authentication and error handling.

    Attributes:
        title: Issue title
        description: Issue description/body
        labels: List of labels to apply to the issue
        assignees: List of assignees for the issue
        milestone: Milestone to assign the issue to
        logger: Logger instance for this class
    """

    def __init__(
        self,
        title: str,
        description: str,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        milestone: Optional[str] = None,
    ) -> None:
        """Initialize the Issue with title and description.

        Args:
            title: Issue title (required)
            description: Issue description/body (required)
            labels: List of labels to apply to the issue
            assignees: List of assignees for the issue
            milestone: Milestone to assign the issue to

        Raises:
            ValueError: If title or description is empty
        """
        if not title or not title.strip():
            raise ValueError("Issue title cannot be empty")

        if not description or not description.strip():
            raise ValueError("Issue description cannot be empty")

        self.title = title.strip()
        self.description = description.strip()
        self.labels = labels or []
        self.assignees = assignees or []
        self.milestone = milestone
        self.logger = logging.getLogger(self.__class__.__name__)

        # Validate title length (GitHub limit is 256 characters)
        if len(self.title) > 256:
            self.logger.warning(
                f"Title length ({len(self.title)}) exceeds GitHub limit (256)"
            )

            self.title = self.title[:253] + "..."

        self.logger.info(f"Created issue: {self.title[:50]}...")

    @classmethod
    def create_github_client(cls, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client.

        Args:
            token: GitHub personal access token (if None, uses environment variable)

        Returns:
            Authenticated GitHub client instance

        Raises:
            GitHubAuthError: If authentication fails or token is missing
        """

        if not token:
            token = os.getenv("GITHUB_TOKEN")

        if not token:
            raise GitHubAuthError(
                "GitHub token not provided. Set GITHUB_TOKEN environment variable "
                "or pass token parameter."
            )

        try:
            auth = Authentication(token)
            return auth.create_client()

        except AuthGitHubAuthError as e:
            # Re-raise as the expected GitHubAuthError for backward compatibility
            raise GitHubAuthError(str(e))

    def create_on_github(
        self, repo_name: str, token: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create the issue on GitHub.

        Args:
            repo_name: Repository name in format 'owner/repo'
            token: GitHub personal access token (optional)

        Returns:
            Dictionary containing created issue information

        Raises:
            IssueError: If issue creation fails
            GitHubAuthError: If authentication fails
        """
        try:
            github_client = self.create_github_client(token)
            repo = github_client.get_repo(repo_name)

            # Prepare issue data
            issue_kwargs = {"title": self.title, "body": self.description}

            # Add labels if specified
            if self.labels:
                # Validate labels exist in repository
                repo_labels = [label.name for label in repo.get_labels()]

                valid_labels = [
                    label for label in self.labels if label in repo_labels
                ]

                invalid_labels = [
                    label for label in self.labels if label not in repo_labels
                ]

                if invalid_labels:
                    self.logger.warning(
                        f"Invalid labels will be skipped: {invalid_labels}"
                    )

                if valid_labels:
                    issue_kwargs["labels"] = valid_labels

            # Add assignees if specified
            if self.assignees:
                # Note: GitHub API will validate assignees automatically
                issue_kwargs["assignees"] = self.assignees

            # Add milestone if specified
            if self.milestone:
                try:
                    milestones = repo.get_milestones()
                    milestone_obj = None

                    for ms in milestones:
                        if ms.title == self.milestone:
                            milestone_obj = ms
                            break

                    if milestone_obj:
                        issue_kwargs["milestone"] = milestone_obj

                    else:
                        self.logger.warning(
                            f"Milestone '{self.milestone}' not found in repository"
                        )

                except Exception as e:
                    self.logger.warning(f"Error setting milestone: {e}")

            # Create the issue
            created_issue = repo.create_issue(**issue_kwargs)

            issue_info = {
                "number": created_issue.number,
                "id": created_issue.id,
                "title": created_issue.title,
                "url": created_issue.html_url,
                "api_url": created_issue.url,
                "state": created_issue.state,
                "created_at": created_issue.created_at.isoformat(),
                "repository": repo_name,
                "labels": [label.name for label in created_issue.get_labels()],
                "assignees": [
                    assignee.login for assignee in created_issue.assignees
                ],
            }

            self.logger.info(
                f"Successfully created issue #{created_issue.number}: {self.title}"
            )

            return issue_info

        except RateLimitExceededException as e:
            raise IssueError(f"GitHub API rate limit exceeded: {e}")

        except GithubException as e:
            raise IssueError(f"GitHub API error: {e}")

        except Exception as e:
            raise IssueError(f"Failed to create issue: {e}")

    def validate_content(self) -> List[str]:
        """Validate issue content and return list of warnings.

        Returns:
            List of validation warnings (empty if all valid)
        """
        warnings = []

        # Check title length
        if len(self.title) > 256:
            warnings.append(
                f"Title length ({len(self.title)}) exceeds GitHub limit (256)"
            )

        # Check for empty or very short description
        if len(self.description) < 10:
            warnings.append(
                "Description is very short, consider adding more detail"
            )

        # Check for basic formatting
        if not any(char in self.description for char in ["\n", ".", "!", "?"]):
            warnings.append(
                "Description appears to be a single sentence without punctuation"
            )

        # Check for placeholder text
        placeholders = ["TODO", "FIXME", "TBD", "XXX", "[placeholder]"]
        if any(
            placeholder in self.title.upper()
            or placeholder in self.description.upper()
            for placeholder in placeholders
        ):
            warnings.append(
                "Content contains placeholder text that should be replaced"
            )

        # Check labels
        if self.labels:
            for label in self.labels:
                if not label.strip():
                    warnings.append("Empty label detected")

                elif len(label) > 50:
                    warnings.append(
                        f"Label '{label}' is very long (>50 characters)"
                    )

        return warnings

    def to_dict(self) -> Dict[str, Any]:
        """Convert issue to dictionary representation.

        Returns:
            Dictionary containing issue data
        """
        return {
            "title": self.title,
            "description": self.description,
            "labels": self.labels.copy(),
            "assignees": self.assignees.copy(),
            "milestone": self.milestone,
            "validation_warnings": self.validate_content(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Issue":
        """Create Issue instance from dictionary.

        Args:
            data: Dictionary containing issue data

        Returns:
            Issue instance

        Raises:
            ValueError: If required fields are missing
        """
        required_fields = ["title", "description"]
        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        return cls(
            title=data["title"],
            description=data["description"],
            labels=data.get("labels"),
            assignees=data.get("assignees"),
            milestone=data.get("milestone"),
        )

    def format_for_display(self) -> str:
        """Format issue for human-readable display.

        Returns:
            Formatted string representation
        """
        lines = [
            f"Title: {self.title}",
            f"Description:\n{self.description}",
        ]

        if self.labels:
            lines.append(f"Labels: {', '.join(self.labels)}")

        if self.assignees:
            lines.append(f"Assignees: {', '.join(self.assignees)}")

        if self.milestone:
            lines.append(f"Milestone: {self.milestone}")

        warnings = self.validate_content()
        if warnings:
            lines.append(f"Warnings: {'; '.join(warnings)}")

        return "\n".join(lines)

    def __str__(self) -> str:
        """String representation of the issue."""
        return (
            f"Issue(title='{self.title[:30]}...', labels={len(self.labels)})"
        )

    def __repr__(self) -> str:
        """Detailed string representation of the issue."""
        return (
            f"Issue(title='{self.title}', description_length={len(self.description)}, "
            f"labels={self.labels}, assignees={self.assignees}, milestone='{self.milestone}')"
        )

    @staticmethod
    def create_bulk_issues(
        issues: List["Issue"],
        repo_name: str,
        token: Optional[str] = None,
        rate_limit_delay: float = 1.0,
        batch_size: int = 10,
        stop_on_error: bool = False,
    ) -> Dict[str, Any]:
        """Create multiple issues on GitHub with rate limiting and error handling.

        Args:
            issues: List of Issue objects to create
            repo_name: GitHub repository name in format "owner/repo"
            token: GitHub personal access token (optional)
            rate_limit_delay: Delay between API calls in seconds
            batch_size: Number of issues to process in each batch
            stop_on_error: Whether to stop on first error or continue

        Returns:
            Dictionary containing bulk creation results
        """
        import time

        logger = logging.getLogger(f"{__name__}.bulk_create")

        if not issues:
            return {
                "success": True,
                "total_issues": 0,
                "created_issues": [],
                "failed_issues": [],
                "errors": [],
            }

        logger.info(
            f"Starting bulk creation of {len(issues)} issues for {repo_name}"
        )

        created_issues = []
        failed_issues = []
        errors = []

        # Process issues in batches
        for batch_start in range(0, len(issues), batch_size):
            batch_end = min(batch_start + batch_size, len(issues))
            batch = issues[batch_start:batch_end]

            logger.info(
                f"Processing batch {batch_start // batch_size + 1}: issues {batch_start + 1}-{batch_end}"
            )

            for i, issue in enumerate(batch):
                try:
                    # Add delay for rate limiting (except for first issue)
                    if batch_start + i > 0:
                        time.sleep(rate_limit_delay)

                    result = issue.create_on_github(repo_name, token)

                    created_issues.append(
                        {
                            "issue": issue,
                            "result": result,
                            "batch": batch_start // batch_size + 1,
                            "index": batch_start + i,
                        }
                    )

                    logger.info(
                        f"Successfully created issue {batch_start + i + 1}/{len(issues)}: {issue.title}"
                    )

                except Exception as e:
                    error_info = {
                        "issue": issue,
                        "error": str(e),
                        "batch": batch_start // batch_size + 1,
                        "index": batch_start + i,
                    }

                    failed_issues.append(error_info)
                    errors.append(
                        f"Issue {batch_start + i + 1} ({issue.title}): {e}"
                    )

                    logger.error(
                        f"Failed to create issue {batch_start + i + 1}/{len(issues)}: {e}"
                    )

                    if stop_on_error:
                        logger.error("Stopping bulk creation due to error")
                        break

            # Stop if we encountered an error and stop_on_error is True
            if stop_on_error and failed_issues:
                break

        success_rate = len(created_issues) / len(issues) if issues else 1.0

        result = {
            "success": len(failed_issues) == 0,
            "total_issues": len(issues),
            "created_count": len(created_issues),
            "failed_count": len(failed_issues),
            "success_rate": success_rate,
            "created_issues": created_issues,
            "failed_issues": failed_issues,
            "errors": errors,
            "rate_limit_delay": rate_limit_delay,
            "batch_size": batch_size,
        }

        logger.info(
            f"Bulk creation completed: {len(created_issues)}/{len(issues)} issues created "
            f"({success_rate:.1%} success rate)"
        )

        return result

    @staticmethod
    def create_issues_with_templates(
        repo_name: str,
        template_data: List[Dict[str, Any]],
        default_labels: Optional[List[str]] = None,
        default_assignees: Optional[List[str]] = None,
        token: Optional[str] = None,
        **bulk_options,
    ) -> Dict[str, Any]:
        """Create issues from template data with bulk processing.

        Args:
            repo_name: GitHub repository name in format "owner/repo"
            template_data: List of dictionaries containing issue template data
            default_labels: Default labels to apply to all issues
            default_assignees: Default assignees to apply to all issues
            token: GitHub personal access token (optional)
            **bulk_options: Additional options passed to create_bulk_issues

        Returns:
            Dictionary containing creation results
        """
        logger = logging.getLogger(f"{__name__}.template_create")

        if not template_data:
            return {
                "success": True,
                "total_issues": 0,
                "created_issues": [],
                "failed_issues": [],
                "errors": [],
            }

        logger.info(f"Creating {len(template_data)} issues from templates")

        # Convert template data to Issue objects
        issues = []
        creation_errors = []

        for i, data in enumerate(template_data):
            try:
                # Apply defaults
                labels = data.get("labels", [])
                if default_labels:
                    labels.extend(default_labels)

                assignees = data.get("assignees", [])
                if default_assignees:
                    assignees.extend(default_assignees)

                issue = Issue(
                    title=data.get("title", f"Issue {i + 1}"),
                    description=data.get("description", ""),
                    labels=list(set(labels)),  # Remove duplicates
                    assignees=list(set(assignees)),  # Remove duplicates
                    milestone=data.get("milestone"),
                )

                issues.append(issue)

            except Exception as e:
                error_msg = (
                    f"Failed to create Issue object from template {i + 1}: {e}"
                )

                creation_errors.append(error_msg)
                logger.error(error_msg)

        if not issues:
            return {
                "success": False,
                "total_issues": len(template_data),
                "created_issues": [],
                "failed_issues": template_data,
                "errors": creation_errors,
            }

        # Create issues using bulk creation
        result = Issue.create_bulk_issues(
            issues, repo_name, token, **bulk_options
        )

        # Add template creation errors to the result
        if creation_errors:
            result["errors"].extend(creation_errors)
            result["template_errors"] = creation_errors

        return result


def test_github_connection(token: Optional[str] = None) -> Dict[str, Any]:
    """Test GitHub API connection and return user information.

    Args:
        token: GitHub personal access token (optional)

    Returns:
        Dictionary containing connection test results

    Raises:
        GitHubAuthError: If authentication fails
    """
    try:
        auth = Authentication(token)
        return auth.test_connection()

    except Exception as e:
        return {"authenticated": False, "error": str(e)}
