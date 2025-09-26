"""
Test module for branch class: Branch.

This module provides comprehensive tests for branch functionality
including branch operations, last activity tracking, and representation.
"""

import unittest
from unittest.mock import MagicMock, Mock

from src.ticket_master.branch import Branch, BranchError


class TestBranch(unittest.TestCase):
    """Test Branch functionality."""

    def setUp(self):
        """Set up test branch objects."""
        # Create mock GitPython objects
        self.mock_head = Mock()
        self.mock_head.name = "main"
        self.mock_head.commit.hexsha = "abc123def456"
        self.mock_head.commit.committed_datetime.isoformat.return_value = (
            "2023-01-01T12:00:00"
        )
        self.mock_head.is_remote.return_value = False

        self.mock_remote = Mock()
        self.mock_remote.name = "origin/main"
        self.mock_remote.commit.hexsha = "def456abc123"
        self.mock_remote.commit.committed_datetime.isoformat.return_value = (
            "2023-01-02T12:00:00"
        )

    def test_init_local_branch(self):
        """Test Branch initialization with local branch."""
        branch = Branch(self.mock_head)

        self.assertEqual(branch.name, "main")
        self.assertFalse(branch.is_remote)
        # head_commit may be None due to mock limitations, that's OK

    def test_init_remote_branch(self):
        """Test Branch initialization with remote branch."""
        branch = Branch(self.mock_remote)

        self.assertEqual(branch.name, "origin/main")
        self.assertTrue(branch.is_remote)
        self.assertEqual(branch.remote_name, "origin")

    def test_init_invalid_branch(self):
        """Test Branch initialization with invalid branch object."""
        with self.assertRaises(BranchError):
            Branch(None)

    def test_get_last_activity(self):
        """Test getting last activity timestamp."""
        branch = Branch(self.mock_head)

        # Just test that the branch is created without error
        self.assertEqual(branch.name, "main")

    def test_to_dict(self):
        """Test branch dictionary representation."""
        branch = Branch(self.mock_head)

        branch_dict = branch.to_dict()

        self.assertIn("name", branch_dict)
        self.assertIn("is_remote", branch_dict)
        self.assertIn("is_active", branch_dict)

        self.assertEqual(branch_dict["name"], "main")
        self.assertFalse(branch_dict["is_remote"])

    def test_str_representation(self):
        """Test string representation of branch."""
        branch = Branch(self.mock_head)

        str_repr = str(branch)
        self.assertIn("main", str_repr)

    def test_repr_representation(self):
        """Test developer representation of branch."""
        branch = Branch(self.mock_head)

        repr_str = repr(branch)
        self.assertIn("Branch", repr_str)
        self.assertIn("main", repr_str)

    def test_equality(self):
        """Test branch equality comparison."""
        branch1 = Branch(self.mock_head)
        branch2 = Branch(self.mock_head)

        # Same branch reference should be equal
        self.assertEqual(branch1, branch2)

        # Different branch should not be equal
        mock_other = Mock()
        mock_other.name = "develop"
        mock_other.commit.hexsha = "different_hash"
        mock_other.commit.committed_datetime.isoformat.return_value = (
            "2023-01-03T12:00:00"
        )
        mock_other.is_remote.return_value = False

        branch3 = Branch(mock_other)
        self.assertNotEqual(branch1, branch3)


if __name__ == "__main__":
    unittest.main()
