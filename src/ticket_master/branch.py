"""
Branch module for Git branch operations and representation.

This module provides the Branch class for representing and working with
Git branches in an object-oriented way.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any

# Import with fallback installation
try:
    from git import Head as GitHead, RemoteReference
except ImportError:
    import subprocess
    import sys

    subprocess.check_call([sys.executable, "-m", "pip", "install", "GitPython>=3.1.40"])
    from git import Head as GitHead, RemoteReference

from .commit import Commit


class BranchError(Exception):
    """Custom exception for branch-related errors."""

    pass


class Branch:
    """Represents a Git branch with associated metadata and operations.

    This class provides an object-oriented interface to Git branches,
    encapsulating branch information and providing methods for analysis.

    Attributes:
        name: Branch name
        is_active: Whether this is the currently active branch
        is_remote: Whether this is a remote branch
        remote_name: Name of the remote (if remote branch)
        head_commit: Commit object representing the branch head
        git_branch: Underlying GitPython branch object
        logger: Logger instance for this class
    """

    def __init__(self, git_branch, repo_obj=None, is_active: bool = False) -> None:
        """Initialize Branch from a GitPython branch object.

        Args:
            git_branch: GitPython Head or RemoteReference object to wrap
            repo_obj: GitPython Repository object for additional operations
            is_active: Whether this is the currently active branch

        Raises:
            BranchError: If git_branch is invalid
        """
        if not hasattr(git_branch, "name"):
            raise BranchError(
                "git_branch must be a GitPython Head or RemoteReference object"
            )

        self.git_branch = git_branch
        self.repo_obj = repo_obj
        self.logger = logging.getLogger(self.__class__.__name__)

        # Extract basic branch information
        self.name = git_branch.name
        self.is_active = is_active

        # Check if it's a remote branch by checking class name or if name contains "/"
        class_name = getattr(git_branch.__class__, "__name__", "")
        self.is_remote = "RemoteReference" in class_name or (
            "/" in self.name and not self.name.startswith("feature/")
        )

        # Extract remote information for remote branches
        if self.is_remote:
            parts = self.name.split("/", 1)
            self.remote_name = parts[0] if len(parts) > 1 else None
        else:
            self.remote_name = None

        # Get head commit
        try:
            self.head_commit = Commit(git_branch.commit)
        except Exception as e:
            self.logger.warning(
                f"Could not get head commit for branch {self.name}: {e}"
            )
            self.head_commit = None

    def get_commits(self, max_count: int = 50) -> List[Commit]:
        """Get commits from this branch.

        Args:
            max_count: Maximum number of commits to retrieve

        Returns:
            List of Commit objects from this branch

        Raises:
            BranchError: If unable to retrieve commits
        """
        try:
            commits = []
            for git_commit in self.git_branch.commit.iter_items(
                max_count=max_count, skip=0
            ):
                commits.append(Commit(git_commit))
            return commits

        except Exception as e:
            raise BranchError(f"Failed to get commits for branch {self.name}: {e}")

    def get_ahead_behind_info(self, base_branch: "Branch") -> Dict[str, int]:
        """Get ahead/behind commit count compared to another branch.

        Args:
            base_branch: Branch to compare against

        Returns:
            Dictionary with 'ahead' and 'behind' commit counts

        Raises:
            BranchError: If unable to calculate ahead/behind info
        """
        if not self.repo_obj:
            raise BranchError("Repository object required for ahead/behind calculation")

        try:
            # Get the commits that are in this branch but not in base_branch (ahead)
            ahead_commits = list(
                self.repo_obj.iter_commits(f"{base_branch.name}..{self.name}")
            )

            # Get the commits that are in base_branch but not in this branch (behind)
            behind_commits = list(
                self.repo_obj.iter_commits(f"{self.name}..{base_branch.name}")
            )

            return {"ahead": len(ahead_commits), "behind": len(behind_commits)}

        except Exception as e:
            raise BranchError(
                f"Failed to calculate ahead/behind for {self.name} vs {base_branch.name}: {e}"
            )

    def get_last_activity(self) -> Optional[datetime]:
        """Get the date of the last activity on this branch.

        Returns:
            DateTime of the last commit, or None if unavailable
        """
        if self.head_commit:
            return self.head_commit.date
        return None

    def is_merged(self, target_branch: "Branch") -> bool:
        """Check if this branch is merged into the target branch.

        Args:
            target_branch: Branch to check if this branch is merged into

        Returns:
            True if this branch is merged into target_branch

        Raises:
            BranchError: If unable to determine merge status
        """
        if not self.repo_obj:
            raise BranchError("Repository object required for merge status check")

        try:
            # Check if there are any commits in this branch that are not in target_branch
            unique_commits = list(
                self.repo_obj.iter_commits(f"{target_branch.name}..{self.name}")
            )

            # If no unique commits, this branch is merged
            return len(unique_commits) == 0

        except Exception as e:
            raise BranchError(
                f"Failed to check merge status for {self.name} into {target_branch.name}: {e}"
            )

    def get_tracking_branch(self) -> Optional["Branch"]:
        """Get the remote tracking branch for this local branch.

        Returns:
            Branch object for the tracking branch, or None if not tracked
        """
        if self.is_remote or not hasattr(self.git_branch, "tracking_branch"):
            return None

        try:
            tracking = self.git_branch.tracking_branch()
            if tracking:
                return Branch(tracking, self.repo_obj, False)
            return None

        except Exception as e:
            self.logger.warning(f"Could not get tracking branch for {self.name}: {e}")
            return None

    def to_dict(self) -> Dict[str, Any]:
        """Convert branch to dictionary representation.

        Returns:
            Dictionary containing all branch information
        """
        result = {
            "name": self.name,
            "is_active": self.is_active,
            "is_remote": self.is_remote,
            "remote_name": self.remote_name,
            "last_activity": (
                self.get_last_activity().isoformat()
                if self.get_last_activity()
                else None
            ),
        }

        if self.head_commit:
            result["head_commit"] = self.head_commit.to_dict()

        return result

    def __str__(self) -> str:
        """String representation of the branch."""
        prefix = "* " if self.is_active else "  "
        remote_info = f" (remote: {self.remote_name})" if self.is_remote else ""
        return f"{prefix}{self.name}{remote_info}"

    def __repr__(self) -> str:
        """Detailed string representation of the branch."""
        return (
            f"Branch(name='{self.name}', is_active={self.is_active}, "
            f"is_remote={self.is_remote}, remote_name='{self.remote_name}')"
        )

    def __eq__(self, other) -> bool:
        """Check equality with another branch."""
        if not isinstance(other, Branch):
            return False
        return self.name == other.name and self.is_remote == other.is_remote

    def __hash__(self) -> int:
        """Hash function for branch objects."""
        return hash((self.name, self.is_remote))
