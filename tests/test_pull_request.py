"""
Test module for pull request class: PullRequest.

This module provides comprehensive tests for pull request functionality
including PR operations, metadata handling, and representation.
"""

import unittest
from datetime import datetime
from unittest.mock import Mock

from src.ticket_master.pull_request import PullRequest, PullRequestError


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


if __name__ == "__main__":
    unittest.main()
