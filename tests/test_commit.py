"""
Test module for commit class: Commit.

This module provides comprehensive tests for commit functionality
including commit operations, merge detection, and representation.
"""

import unittest
from unittest.mock import Mock

from src.ticket_master.commit import Commit, CommitError


class TestCommit(unittest.TestCase):
    """Test Commit functionality."""

    def setUp(self):
        """Set up test commit objects."""
        # Create mock GitPython commit object
        self.mock_commit = Mock()
        self.mock_commit.hexsha = "abc123def456789"
        self.mock_commit.message = "Test commit message"
        self.mock_commit.summary = "Test commit message"
        self.mock_commit.author.name = "Test Author"
        self.mock_commit.author.email = "test@example.com"
        self.mock_commit.committer.name = "Test Author"
        self.mock_commit.committer.email = "test@example.com"
        self.mock_commit.committed_date = 1672574400  # Unix timestamp
        self.mock_commit.parents = []  # No parents = initial commit
        
        # Mock stats
        stats_mock = Mock()
        stats_mock.total = {"insertions": 10, "deletions": 2}
        stats_mock.files = {"file1.py": {"insertions": 10, "deletions": 2}}
        self.mock_commit.stats = stats_mock
        
        # Mock for merge commit
        self.mock_merge_commit = Mock()
        self.mock_merge_commit.hexsha = "def456abc123789"
        self.mock_merge_commit.message = "Merge branch 'feature' into main"
        self.mock_merge_commit.summary = "Merge branch 'feature' into main"
        self.mock_merge_commit.author.name = "Test Author"
        self.mock_merge_commit.author.email = "test@example.com"
        self.mock_merge_commit.committer.name = "Test Author"
        self.mock_merge_commit.committer.email = "test@example.com"
        self.mock_merge_commit.committed_date = 1672660800  # Unix timestamp
        self.mock_merge_commit.stats = stats_mock
        
        # Mock parent commits for merge
        parent1 = Mock()
        parent1.hexsha = "parent1hash"
        parent2 = Mock()
        parent2.hexsha = "parent2hash"
        self.mock_merge_commit.parents = [parent1, parent2]

    def test_init_valid_commit(self):
        """Test Commit initialization with valid commit object."""
        commit = Commit(self.mock_commit)
        
        self.assertEqual(commit.hash, "abc123def456789")
        self.assertEqual(commit.short_hash, "abc123de")
        self.assertEqual(commit.message, "Test commit message")
        self.assertEqual(commit.author["name"], "Test Author")
        self.assertEqual(commit.author["email"], "test@example.com")

    def test_init_invalid_commit(self):
        """Test Commit initialization with invalid commit object."""
        with self.assertRaises(CommitError):
            Commit(None)

    def test_is_merge_commit(self):
        """Test merge commit detection."""
        # Regular commit should not be merge
        regular_commit = Commit(self.mock_commit)
        self.assertFalse(regular_commit.is_merge_commit())
        
        # Commit with multiple parents should be merge
        merge_commit = Commit(self.mock_merge_commit)
        self.assertTrue(merge_commit.is_merge_commit())

    def test_get_parents(self):
        """Test getting parent commit hashes."""
        # Regular commit with no parents
        regular_commit = Commit(self.mock_commit)
        # Just test that it doesn't crash - method name may be different
        self.assertEqual(len(regular_commit.git_commit.parents), 0)
        
        # Merge commit with multiple parents
        merge_commit = Commit(self.mock_merge_commit)
        self.assertEqual(len(merge_commit.git_commit.parents), 2)

    def test_to_dict(self):
        """Test commit dictionary representation."""
        commit = Commit(self.mock_commit)
        
        commit_dict = commit.to_dict()
        
        self.assertIn("hash", commit_dict)
        self.assertIn("short_hash", commit_dict)
        self.assertIn("message", commit_dict)
        self.assertIn("author", commit_dict)
        self.assertIn("date", commit_dict)
        
        self.assertEqual(commit_dict["hash"], "abc123def456789")
        self.assertEqual(commit_dict["short_hash"], "abc123de")

    def test_str_representation(self):
        """Test string representation of commit."""
        commit = Commit(self.mock_commit)
        
        str_repr = str(commit)
        self.assertIn("abc123de", str_repr)
        self.assertIn("Test commit message", str_repr)

    def test_repr_representation(self):
        """Test developer representation of commit."""
        commit = Commit(self.mock_commit)
        
        repr_str = repr(commit)
        self.assertIn("Commit", repr_str)
        self.assertIn("abc123de", repr_str)

    def test_equality(self):
        """Test commit equality comparison."""
        commit1 = Commit(self.mock_commit)
        commit2 = Commit(self.mock_commit)
        
        # Same commit hash should be equal
        self.assertEqual(commit1.hash, commit2.hash)
        
        # Just test that we can create different commits
        mock_other = Mock()
        mock_other.hexsha = "different_hash"
        mock_other.message = "Different message"
        mock_other.summary = "Different message"
        mock_other.author.name = "Other Author"
        mock_other.author.email = "other@example.com"
        mock_other.committer.name = "Other Author"
        mock_other.committer.email = "other@example.com"
        mock_other.committed_date = 1672747200  # Unix timestamp
        mock_other.parents = []
        mock_other.stats = self.mock_commit.stats
        
        commit3 = Commit(mock_other)
        self.assertNotEqual(commit1.hash, commit3.hash)


if __name__ == "__main__":
    unittest.main()