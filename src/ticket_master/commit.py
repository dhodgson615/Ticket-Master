"""
Commit module for Git commit operations and representation.

This module provides the Commit class for representing and working with
Git commits in an object-oriented way.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import with fallback installation
try:
    from git import Commit as GitCommit, NULL_TREE
except ImportError:
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "GitPython>=3.1.40"]
    )
    from git import Commit as GitCommit, NULL_TREE


class CommitError(Exception):
    """Custom exception for commit-related errors."""

    pass


class Commit:
    """Represents a Git commit with associated metadata and operations.

    This class provides an object-oriented interface to Git commits,
    encapsulating commit information and providing methods for analysis.

    Attributes:
        hash: Full commit hash (SHA)
        short_hash: Abbreviated commit hash
        author: Author information (name and email)
        committer: Committer information (name and email)
        message: Full commit message
        summary: First line of commit message
        date: Commit date as datetime object
        files_changed: Number of files changed in this commit
        insertions: Number of lines inserted
        deletions: Number of lines deleted
        git_commit: Underlying GitPython Commit object
        logger: Logger instance for this class
    """

    def __init__(self, git_commit: GitCommit) -> None:
        """Initialize Commit from a GitPython Commit object.

        Args:
            git_commit: GitPython Commit object to wrap

        Raises:
            CommitError: If git_commit is invalid
        """
        if not hasattr(git_commit, "hexsha"):
            raise CommitError("git_commit must be a GitPython Commit object")

        self.git_commit = git_commit
        self.logger = logging.getLogger(self.__class__.__name__)

        # Extract basic commit information
        self.hash = git_commit.hexsha
        self.short_hash = git_commit.hexsha[:8]
        self.author = {
            "name": git_commit.author.name,
            "email": git_commit.author.email,
        }
        self.committer = {
            "name": git_commit.committer.name,
            "email": git_commit.committer.email,
        }
        self.message = git_commit.message.strip()
        self.summary = git_commit.summary
        self.date = datetime.fromtimestamp(git_commit.committed_date)

        # Extract statistics
        try:
            stats = git_commit.stats.total
            self.files_changed = len(git_commit.stats.files)
            self.insertions = stats.get("insertions", 0)
            self.deletions = stats.get("deletions", 0)
        except Exception as e:
            self.logger.warning(
                f"Could not get stats for commit {self.short_hash}: {e}"
            )
            self.files_changed = 0
            self.insertions = 0
            self.deletions = 0

    def get_changed_files(self) -> List[str]:
        """Get list of files changed in this commit.

        Returns:
            List of file paths that were modified in this commit

        Raises:
            CommitError: If unable to retrieve file changes
        """
        try:
            if self.git_commit.parents:
                # Compare with parent commit
                diffs = self.git_commit.parents[0].diff(self.git_commit)
            else:
                # First commit, compare against empty tree
                diffs = self.git_commit.diff(NULL_TREE)

            changed_files = []
            for diff in diffs:
                file_path = diff.a_path or diff.b_path
                if file_path:
                    changed_files.append(file_path)

            return changed_files

        except Exception as e:
            raise CommitError(
                f"Failed to get changed files for commit {self.short_hash}: {e}"
            )

    def get_file_diff(self, file_path: str) -> Optional[str]:
        """Get the diff for a specific file in this commit.

        Args:
            file_path: Path to the file to get diff for

        Returns:
            String containing the diff, or None if file not changed

        Raises:
            CommitError: If unable to retrieve diff
        """
        try:
            if self.git_commit.parents:
                diffs = self.git_commit.parents[0].diff(
                    self.git_commit, paths=[file_path]
                )
            else:
                diffs = self.git_commit.diff(NULL_TREE, paths=[file_path])

            if diffs:
                return diffs[0].diff.decode("utf-8") if diffs[0].diff else None

            return None

        except Exception as e:
            raise CommitError(
                f"Failed to get diff for file {file_path} in commit {self.short_hash}: {e}"
            )

    def is_merge_commit(self) -> bool:
        """Check if this commit is a merge commit.

        Returns:
            True if this is a merge commit (has multiple parents)
        """
        return len(self.git_commit.parents) > 1

    def get_parents(self) -> List["Commit"]:
        """Get parent commits of this commit.

        Returns:
            List of Commit objects representing parent commits
        """
        return [Commit(parent) for parent in self.git_commit.parents]

    def to_dict(self) -> Dict[str, Any]:
        """Convert commit to dictionary representation.

        Returns:
            Dictionary containing all commit information
        """
        return {
            "hash": self.hash,
            "short_hash": self.short_hash,
            "author": self.author,
            "committer": self.committer,
            "message": self.message,
            "summary": self.summary,
            "date": self.date.isoformat(),
            "files_changed": self.files_changed,
            "insertions": self.insertions,
            "deletions": self.deletions,
            "is_merge": self.is_merge_commit(),
        }

    def __str__(self) -> str:
        """String representation of the commit."""
        return f"{self.short_hash}: {self.summary}"

    def __repr__(self) -> str:
        """Detailed string representation of the commit."""
        return (
            f"Commit(hash='{self.short_hash}', author='{self.author['name']}', "
            f"date='{self.date.strftime('%Y-%m-%d %H:%M:%S')}', "
            f"files_changed={self.files_changed})"
        )

    def __eq__(self, other) -> bool:
        """Check equality with another commit."""
        if not isinstance(other, Commit):
            return False
        return self.hash == other.hash

    def __hash__(self) -> int:
        """Hash function for commit objects."""
        return hash(self.hash)
