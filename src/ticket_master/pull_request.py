import logging
from typing import Any, Dict, List

try:
    from github import PullRequest as GitHubPullRequest

except ImportError:
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "PyGithub>=1.59.1"]
    )

    from github import PullRequest as GitHubPullRequest

from .commit import Commit


class PullRequestError(Exception):
    """Custom exception for pull request-related errors."""

    pass


class PullRequest:
    """Represents a GitHub pull request with associated metadata and operations.

    This class provides an object-oriented interface to GitHub pull requests,
    encapsulating PR information and providing methods for analysis.

    Attributes:
        number: Pull request number
        title: Pull request title
        description: Pull request description/body
        state: Pull request state (open, closed, merged)
        author: Author information
        created_at: Creation date
        updated_at: Last update date
        merged_at: Merge date (if merged)
        source_branch: Source branch name
        target_branch: Target branch name
        is_draft: Whether this is a draft PR
        mergeable: Whether the PR is mergeable
        commits_count: Number of commits in the PR
        changed_files_count: Number of files changed
        additions: Number of line additions
        deletions: Number of line deletions
        github_pr: Underlying PyGithub PullRequest object
        logger: Logger instance for this class
    """

    def __init__(self, github_pr: GitHubPullRequest) -> None:
        """Initialize PullRequest from a PyGithub PullRequest object.

        Args:
            github_pr: PyGithub PullRequest object to wrap

        Raises:
            PullRequestError: If github_pr is invalid
        """
        if not hasattr(github_pr, "number"):
            raise PullRequestError(
                "github_pr must be a PyGithub PullRequest object"
            )

        self.github_pr = github_pr
        self.logger = logging.getLogger(self.__class__.__name__)

        # Extract basic PR information
        self.number = github_pr.number
        self.title = github_pr.title
        self.description = github_pr.body or ""
        self.state = github_pr.state
        self.is_draft = github_pr.draft

        # Author information
        self.author = {
            "login": github_pr.user.login,
            "name": github_pr.user.name or github_pr.user.login,
            "email": github_pr.user.email,
            "avatar_url": github_pr.user.avatar_url,
        }

        # Dates
        self.created_at = github_pr.created_at
        self.updated_at = github_pr.updated_at
        self.merged_at = github_pr.merged_at

        # Branch information
        self.source_branch = github_pr.head.ref
        self.target_branch = github_pr.base.ref

        # PR statistics
        self.commits_count = github_pr.commits
        self.changed_files_count = github_pr.changed_files
        self.additions = github_pr.additions
        self.deletions = github_pr.deletions

        # Merge status
        self.mergeable = github_pr.mergeable
        self.merged = github_pr.merged

    def get_commits(self) -> List[Commit]:
        """Get commits associated with this pull request.

        Returns:
            List of Commit objects from this PR

        Raises:
            PullRequestError: If unable to retrieve commits
        """
        try:
            commits = []
            for github_commit in self.github_pr.get_commits():
                # Convert GitHub commit to git.Commit for our Commit class
                # Note: This is a simplified approach; in a full implementation,
                # you might want to fetch the actual git.Commit objects
                commit_dict = {
                    "sha": github_commit.sha,
                    "commit": github_commit.commit,
                    "author": github_commit.author,
                    "committer": github_commit.committer,
                }
                # For now, we'll create a minimal representation
                # In a full implementation, you'd want to integrate with the git repository
                commits.append(commit_dict)

            return commits

        except Exception as e:
            raise PullRequestError(
                f"Failed to get commits for PR #{self.number}: {e}"
            )

    def get_changed_files(self) -> List[Dict[str, Any]]:
        """Get files changed in this pull request.

        Returns:
            List of dictionaries containing file change information

        Raises:
            PullRequestError: If unable to retrieve changed files
        """
        try:
            changed_files = []
            for file in self.github_pr.get_files():
                file_info = {
                    "filename": file.filename,
                    "status": file.status,  # added, modified, removed, renamed
                    "additions": file.additions,
                    "deletions": file.deletions,
                    "changes": file.changes,
                    "patch": file.patch,
                    "previous_filename": getattr(
                        file, "previous_filename", None
                    ),
                }
                changed_files.append(file_info)

            return changed_files

        except Exception as e:
            raise PullRequestError(
                f"Failed to get changed files for PR #{self.number}: {e}"
            )

    def get_reviews(self) -> List[Dict[str, Any]]:
        """Get reviews for this pull request.

        Returns:
            List of dictionaries containing review information

        Raises:
            PullRequestError: If unable to retrieve reviews
        """
        try:
            reviews = []
            for review in self.github_pr.get_reviews():
                review_info = {
                    "id": review.id,
                    "user": {
                        "login": review.user.login,
                        "name": review.user.name or review.user.login,
                    },
                    "state": review.state,  # APPROVED, CHANGES_REQUESTED, COMMENTED
                    "body": review.body or "",
                    "submitted_at": review.submitted_at,
                }
                reviews.append(review_info)

            return reviews

        except Exception as e:
            raise PullRequestError(
                f"Failed to get reviews for PR #{self.number}: {e}"
            )

    def get_comments(self) -> List[Dict[str, Any]]:
        """Get comments for this pull request.

        Returns:
            List of dictionaries containing comment information

        Raises:
            PullRequestError: If unable to retrieve comments
        """
        try:
            comments = []

            # Get issue comments (general PR comments)
            for comment in self.github_pr.get_issue_comments():
                comment_info = {
                    "id": comment.id,
                    "type": "issue_comment",
                    "user": {
                        "login": comment.user.login,
                        "name": comment.user.name or comment.user.login,
                    },
                    "body": comment.body,
                    "created_at": comment.created_at,
                    "updated_at": comment.updated_at,
                }
                comments.append(comment_info)

            # Get review comments (inline code comments)
            for comment in self.github_pr.get_review_comments():
                comment_info = {
                    "id": comment.id,
                    "type": "review_comment",
                    "user": {
                        "login": comment.user.login,
                        "name": comment.user.name or comment.user.login,
                    },
                    "body": comment.body,
                    "path": comment.path,
                    "position": comment.position,
                    "line": comment.line,
                    "created_at": comment.created_at,
                    "updated_at": comment.updated_at,
                }
                comments.append(comment_info)

            return sorted(comments, key=lambda x: x["created_at"])

        except Exception as e:
            raise PullRequestError(
                f"Failed to get comments for PR #{self.number}: {e}"
            )

    def is_mergeable(self) -> bool:
        """Check if this pull request is mergeable.

        Returns:
            True if the PR can be merged
        """
        return self.mergeable is True and self.state == "open"

    def is_approved(self) -> bool:
        """Check if this pull request has been approved.

        Returns:
            True if the PR has at least one approval and no change requests

        Raises:
            PullRequestError: If unable to check approval status
        """
        try:
            reviews = self.get_reviews()

            # Get the latest review from each reviewer
            latest_reviews = {}
            for review in reviews:
                user_login = review["user"]["login"]
                if (
                    user_login not in latest_reviews
                    or review["submitted_at"]
                    > latest_reviews[user_login]["submitted_at"]
                ):
                    latest_reviews[user_login] = review

            # Check if there are any change requests
            has_changes_requested = any(
                review["state"] == "CHANGES_REQUESTED"
                for review in latest_reviews.values()
            )

            # Check if there are any approvals
            has_approval = any(
                review["state"] == "APPROVED"
                for review in latest_reviews.values()
            )

            return has_approval and not has_changes_requested

        except Exception as e:
            raise PullRequestError(
                f"Failed to check approval status for PR #{self.number}: {e}"
            )

    def to_dict(self) -> Dict[str, Any]:
        """Convert pull request to dictionary representation.

        Returns:
            Dictionary containing all pull request information
        """
        return {
            "number": self.number,
            "title": self.title,
            "description": self.description,
            "state": self.state,
            "is_draft": self.is_draft,
            "merged": self.merged,
            "author": self.author,
            "created_at": (
                self.created_at.isoformat() if self.created_at else None
            ),
            "updated_at": (
                self.updated_at.isoformat() if self.updated_at else None
            ),
            "merged_at": (
                self.merged_at.isoformat() if self.merged_at else None
            ),
            "source_branch": self.source_branch,
            "target_branch": self.target_branch,
            "commits_count": self.commits_count,
            "changed_files_count": self.changed_files_count,
            "additions": self.additions,
            "deletions": self.deletions,
            "mergeable": self.mergeable,
        }

    def __str__(self) -> str:
        """String representation of the pull request."""
        status = "MERGED" if self.merged else self.state.upper()
        return f"PR #{self.number} ({status}): {self.title}"

    def __repr__(self) -> str:
        """Detailed string representation of the pull request."""
        return (
            f"PullRequest(number={self.number}, title='{self.title[:50]}...', "
            f"state='{self.state}', author='{self.author['login']}')"
        )

    def __eq__(self, other) -> bool:
        """Check equality with another pull request."""
        if not isinstance(other, PullRequest):
            return False
        return self.number == other.number

    def __hash__(self) -> int:
        """Hash function for pull request objects."""
        return hash(self.number)
