"""
Test module for pull request class: PullRequest.

This module provides comprehensive tests for pull request functionality
including PR operations, metadata handling, and representation.
"""

import sys
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from pull_request import PullRequest, PullRequestError


class TestPullRequest(unittest.TestCase):
    """Test PullRequest functionality."""

    def setUp(self):
        """Set up test pull request objects."""
        # Create mock GitHub pull request object
        self.mock_pr = Mock()
        self.mock_pr.number = 123
        self.mock_pr.title = "Test pull request"
        self.mock_pr.body = "This is a test pull request description"
        self.mock_pr.state = "open"
        self.mock_pr.user.name = "Test Author"
        self.mock_pr.user.login = "testuser"
        self.mock_pr.user.email = None
        self.mock_pr.draft = False
        self.mock_pr.commits = 5
        self.mock_pr.changed_files = 3
        self.mock_pr.additions = 100
        self.mock_pr.deletions = 20
        self.mock_pr.created_at = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_pr.updated_at = datetime(2023, 1, 2, 12, 0, 0)
        self.mock_pr.merged_at = None
        self.mock_pr.head.ref = "feature-branch"
        self.mock_pr.base.ref = "main"
        self.mock_pr.mergeable = True
        self.mock_pr.merged = False

    def test_init_valid_pr(self):
        """Test PullRequest initialization with valid PR object."""
        pr = PullRequest(self.mock_pr)

        self.assertEqual(pr.number, 123)
        self.assertEqual(pr.title, "Test pull request")
        self.assertEqual(
            pr.description, "This is a test pull request description"
        )
        self.assertEqual(pr.state, "open")
        self.assertEqual(pr.author["name"], "Test Author")
        self.assertEqual(pr.author["login"], "testuser")

    def test_init_invalid_pr(self):
        """Test PullRequest initialization with invalid PR object."""
        with self.assertRaises(PullRequestError):
            PullRequest(None)

    def test_is_mergeable(self):
        """Test pull request mergeability check."""
        pr = PullRequest(self.mock_pr)
        self.assertTrue(pr.mergeable)

        # Test non-mergeable PR
        self.mock_pr.mergeable = False
        pr_not_mergeable = PullRequest(self.mock_pr)
        self.assertFalse(pr_not_mergeable.mergeable)

    def test_is_merged(self):
        """Test pull request merged status."""
        pr = PullRequest(self.mock_pr)
        self.assertFalse(pr.merged)

        # Test merged PR
        self.mock_pr.merged = True
        pr_merged = PullRequest(self.mock_pr)
        self.assertTrue(pr_merged.merged)

    def test_get_branch_info(self):
        """Test getting branch information."""
        pr = PullRequest(self.mock_pr)

        self.assertEqual(pr.source_branch, "feature-branch")
        self.assertEqual(pr.target_branch, "main")

    def test_to_dict(self):
        """Test pull request dictionary representation."""
        pr = PullRequest(self.mock_pr)

        pr_dict = pr.to_dict()

        self.assertIn("number", pr_dict)
        self.assertIn("title", pr_dict)
        self.assertIn("description", pr_dict)
        self.assertIn("state", pr_dict)
        self.assertIn("author", pr_dict)
        self.assertIn("created_at", pr_dict)
        self.assertIn("updated_at", pr_dict)
        self.assertIn("source_branch", pr_dict)
        self.assertIn("target_branch", pr_dict)
        self.assertIn("mergeable", pr_dict)
        self.assertIn("merged", pr_dict)

        self.assertEqual(pr_dict["number"], 123)
        self.assertEqual(pr_dict["title"], "Test pull request")

    def test_str_representation(self):
        """Test string representation of pull request."""
        pr = PullRequest(self.mock_pr)

        str_repr = str(pr)
        self.assertIn("#123", str_repr)
        self.assertIn("Test pull request", str_repr)

    def test_repr_representation(self):
        """Test developer representation of pull request."""
        pr = PullRequest(self.mock_pr)

        repr_str = repr(pr)
        self.assertIn("PullRequest", repr_str)
        self.assertIn("123", repr_str)

    def test_equality(self):
        """Test pull request equality comparison."""
        pr1 = PullRequest(self.mock_pr)
        pr2 = PullRequest(self.mock_pr)

        # Same PR number should be equal
        self.assertEqual(pr1, pr2)

        # Different PR should not be equal
        mock_other = Mock()
        mock_other.number = 456
        mock_other.title = "Different PR"
        mock_other.body = "Different description"
        mock_other.state = "closed"
        mock_other.user.name = "Other Author"
        mock_other.user.login = "otheruser"
        mock_other.user.email = None
        mock_other.created_at = datetime(2023, 1, 3, 12, 0, 0)
        mock_other.updated_at = datetime(2023, 1, 4, 12, 0, 0)
        mock_other.draft = True
        mock_other.commits = 10
        mock_other.changed_files = 8
        mock_other.additions = 200
        mock_other.deletions = 50
        mock_other.head.ref = "other-branch"
        mock_other.base.ref = "develop"
        mock_other.mergeable = False
        mock_other.merged = True

        pr3 = PullRequest(mock_other)
        self.assertNotEqual(pr1, pr3)

    def test_get_commits(self):
        """Test getting commits from pull request."""
        # Mock commits
        mock_commit1 = Mock()
        mock_commit1.sha = "abc123"
        mock_commit1.commit.message = "First commit"
        mock_commit1.commit.author.name = "Author 1"
        mock_commit1.commit.author.email = "author1@example.com"
        mock_commit1.commit.author.date = datetime(2023, 1, 1, 10, 0, 0)

        mock_commit2 = Mock()
        mock_commit2.sha = "def456"
        mock_commit2.commit.message = "Second commit"
        mock_commit2.commit.author.name = "Author 2"
        mock_commit2.commit.author.email = "author2@example.com"
        mock_commit2.commit.author.date = datetime(2023, 1, 1, 11, 0, 0)

        self.mock_pr.get_commits.return_value = [mock_commit1, mock_commit2]

        pr = PullRequest(self.mock_pr)
        commits = pr.get_commits()

        self.assertEqual(len(commits), 2)
        self.assertEqual(commits[0].hash, "abc123")
        self.assertEqual(commits[0].message, "First commit")
        self.assertEqual(commits[1].hash, "def456")
        self.assertEqual(commits[1].message, "Second commit")

    def test_get_commits_error(self):
        """Test get_commits with error."""
        self.mock_pr.get_commits.side_effect = Exception("API Error")

        pr = PullRequest(self.mock_pr)

        with self.assertRaises(PullRequestError):
            pr.get_commits()

    def test_get_changed_files(self):
        """Test getting changed files from pull request."""
        # Mock file changes
        mock_file1 = Mock()
        mock_file1.filename = "file1.py"
        mock_file1.status = "modified"
        mock_file1.additions = 10
        mock_file1.deletions = 5
        mock_file1.changes = 15
        mock_file1.patch = "@@ -1,3 +1,4 @@\n+added line\n original line"

        mock_file2 = Mock()
        mock_file2.filename = "file2.py"
        mock_file2.status = "added"
        mock_file2.additions = 20
        mock_file2.deletions = 0
        mock_file2.changes = 20
        mock_file2.patch = "@@ -0,0 +1,5 @@\n+new file content"

        self.mock_pr.get_files.return_value = [mock_file1, mock_file2]

        pr = PullRequest(self.mock_pr)
        files = pr.get_changed_files()

        self.assertEqual(len(files), 2)
        self.assertEqual(files[0]["filename"], "file1.py")
        self.assertEqual(files[0]["status"], "modified")
        self.assertEqual(files[1]["filename"], "file2.py")
        self.assertEqual(files[1]["status"], "added")

    def test_get_changed_files_error(self):
        """Test get_changed_files with error."""
        self.mock_pr.get_files.side_effect = Exception("API Error")

        pr = PullRequest(self.mock_pr)

        with self.assertRaises(PullRequestError):
            pr.get_changed_files()

    def test_get_reviews(self):
        """Test getting reviews from pull request."""
        # Mock reviews
        mock_review1 = Mock()
        mock_review1.id = 1
        mock_review1.user.login = "reviewer1"
        mock_review1.user.name = "Reviewer One"
        mock_review1.state = "APPROVED"
        mock_review1.body = "Looks good!"
        mock_review1.submitted_at = datetime(2023, 1, 2, 10, 0, 0)

        mock_review2 = Mock()
        mock_review2.id = 2
        mock_review2.user.login = "reviewer2"
        mock_review2.user.name = "Reviewer Two"
        mock_review2.state = "CHANGES_REQUESTED"
        mock_review2.body = "Needs fixes"
        mock_review2.submitted_at = datetime(2023, 1, 2, 11, 0, 0)

        self.mock_pr.get_reviews.return_value = [mock_review1, mock_review2]

        pr = PullRequest(self.mock_pr)
        reviews = pr.get_reviews()

        self.assertEqual(len(reviews), 2)
        self.assertEqual(reviews[0]["reviewer"], "reviewer1")
        self.assertEqual(reviews[0]["state"], "APPROVED")
        self.assertEqual(reviews[1]["reviewer"], "reviewer2")
        self.assertEqual(reviews[1]["state"], "CHANGES_REQUESTED")

    def test_get_reviews_error(self):
        """Test get_reviews with error."""
        self.mock_pr.get_reviews.side_effect = Exception("API Error")

        pr = PullRequest(self.mock_pr)

        with self.assertRaises(PullRequestError):
            pr.get_reviews()

    def test_get_comments(self):
        """Test getting comments from pull request."""
        # Mock comments
        mock_comment1 = Mock()
        mock_comment1.id = 1
        mock_comment1.user.login = "commenter1"
        mock_comment1.user.name = "Commenter One"
        mock_comment1.body = "This is a comment"
        mock_comment1.created_at = datetime(2023, 1, 2, 10, 0, 0)
        mock_comment1.updated_at = datetime(2023, 1, 2, 10, 0, 0)

        mock_comment2 = Mock()
        mock_comment2.id = 2
        mock_comment2.user.login = "commenter2"
        mock_comment2.user.name = "Commenter Two"
        mock_comment2.body = "Another comment"
        mock_comment2.created_at = datetime(2023, 1, 2, 11, 0, 0)
        mock_comment2.updated_at = datetime(2023, 1, 2, 11, 30, 0)

        self.mock_pr.get_issue_comments.return_value = [
            mock_comment1,
            mock_comment2,
        ]

        pr = PullRequest(self.mock_pr)
        comments = pr.get_comments()

        self.assertEqual(len(comments), 2)
        self.assertEqual(comments[0]["author"], "commenter1")
        self.assertEqual(comments[0]["body"], "This is a comment")
        self.assertEqual(comments[1]["author"], "commenter2")
        self.assertEqual(comments[1]["body"], "Another comment")

    def test_get_comments_error(self):
        """Test get_comments with error."""
        self.mock_pr.get_issue_comments.side_effect = Exception("API Error")

        pr = PullRequest(self.mock_pr)

        with self.assertRaises(PullRequestError):
            pr.get_comments()

    def test_is_mergeable_true(self):
        """Test is_mergeable when PR is mergeable."""
        self.mock_pr.mergeable = True

        pr = PullRequest(self.mock_pr)

        self.assertTrue(pr.is_mergeable())

    def test_is_mergeable_false(self):
        """Test is_mergeable when PR is not mergeable."""
        self.mock_pr.mergeable = False

        pr = PullRequest(self.mock_pr)

        self.assertFalse(pr.is_mergeable())

    def test_is_mergeable_none(self):
        """Test is_mergeable when mergeable status is None."""
        self.mock_pr.mergeable = None

        pr = PullRequest(self.mock_pr)

        self.assertFalse(pr.is_mergeable())

    def test_is_approved_with_approvals(self):
        """Test is_approved when PR has approvals."""
        # Mock reviews with approvals
        mock_review1 = Mock()
        mock_review1.state = "APPROVED"
        mock_review2 = Mock()
        mock_review2.state = "COMMENTED"

        self.mock_pr.get_reviews.return_value = [mock_review1, mock_review2]

        pr = PullRequest(self.mock_pr)

        self.assertTrue(pr.is_approved())

    def test_is_approved_without_approvals(self):
        """Test is_approved when PR has no approvals."""
        # Mock reviews without approvals
        mock_review1 = Mock()
        mock_review1.state = "COMMENTED"
        mock_review2 = Mock()
        mock_review2.state = "CHANGES_REQUESTED"

        self.mock_pr.get_reviews.return_value = [mock_review1, mock_review2]

        pr = PullRequest(self.mock_pr)

        self.assertFalse(pr.is_approved())

    def test_is_approved_no_reviews(self):
        """Test is_approved when PR has no reviews."""
        self.mock_pr.get_reviews.return_value = []

        pr = PullRequest(self.mock_pr)

        self.assertFalse(pr.is_approved())

    def test_is_approved_error(self):
        """Test is_approved with error getting reviews."""
        self.mock_pr.get_reviews.side_effect = Exception("API Error")

        pr = PullRequest(self.mock_pr)

        self.assertFalse(pr.is_approved())


class TestPullRequestError(unittest.TestCase):
    """Test PullRequestError exception."""

    def test_pull_request_error(self):
        """Test PullRequestError can be raised."""
        with self.assertRaises(PullRequestError):
            raise PullRequestError("Test error")

    def test_pull_request_error_message(self):
        """Test PullRequestError message."""
        error_msg = "Test error message"

        try:
            raise PullRequestError(error_msg)
        except PullRequestError as e:
            self.assertEqual(str(e), error_msg)


class TestPullRequestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions."""

    def setUp(self):
        """Set up test with minimal mock PR."""
        self.mock_pr = Mock()
        self.mock_pr.number = 123
        self.mock_pr.title = "Test PR"
        self.mock_pr.body = "Test body"
        self.mock_pr.state = "open"
        self.mock_pr.user.name = "Test User"
        self.mock_pr.user.login = "testuser"
        self.mock_pr.user.email = None
        self.mock_pr.draft = False
        self.mock_pr.commits = 1
        self.mock_pr.changed_files = 1
        self.mock_pr.additions = 10
        self.mock_pr.deletions = 5
        self.mock_pr.created_at = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_pr.updated_at = datetime(2023, 1, 1, 12, 0, 0)
        self.mock_pr.merged_at = None
        self.mock_pr.head.ref = "feature"
        self.mock_pr.base.ref = "main"
        self.mock_pr.mergeable = True
        self.mock_pr.merged = False

    def test_pr_with_email(self):
        """Test PR when user has email."""
        self.mock_pr.user.email = "test@example.com"

        pr = PullRequest(self.mock_pr)

        self.assertEqual(
            pr.author["email"], "test@example.com"
        )  # TODO: fix test because there is no author_email in PullRequest

    def test_pr_merged(self):
        """Test PR that is merged."""
        self.mock_pr.merged = True
        self.mock_pr.merged_at = datetime(2023, 1, 2, 12, 0, 0)

        pr = PullRequest(self.mock_pr)

        self.assertTrue(pr.merged)
        self.assertEqual(pr.merged_at, datetime(2023, 1, 2, 12, 0, 0))

    def test_pr_draft(self):
        """Test draft PR."""
        self.mock_pr.draft = True

        pr = PullRequest(self.mock_pr)

        self.assertTrue(
            pr.draft
        )  # TODO: fix test because there is no draft in PullRequest

    def test_pr_with_different_states(self):
        """Test PR with different states."""
        states = ["open", "closed", "merged"]

        for state in states:
            self.mock_pr.state = state
            pr = PullRequest(self.mock_pr)
            self.assertEqual(pr.state, state)


if __name__ == "__main__":
    unittest.main()
