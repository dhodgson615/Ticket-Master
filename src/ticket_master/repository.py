"""
Repository module for Git operations and analysis.

This module provides the Repository class for interacting with Git repositories,
extracting commit history, analyzing file changes, and preparing data for
issue generation.
"""

import logging
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import with fallback installation
try:
    import git
    from git import Repo, InvalidGitRepositoryError
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "GitPython>=3.1.40"]
    )
    import git
    from git import Repo, InvalidGitRepositoryError


from .commit import Commit
from .branch import Branch


class RepositoryError(Exception):
    """Custom exception for repository-related errors."""

    pass


class Repository:
    """Handles Git repository operations and analysis.

    This class provides methods to interact with Git repositories,
    extract commit history, analyze file changes, and prepare data
    for AI-powered issue generation.

    Attributes:
        path: Path to the Git repository
        repo: GitPython Repo object
        logger: Logger instance for this class
    """

    def __init__(self, path: str) -> None:
        """Initialize the Repository with a given path.

        Args:
            path: Path to the Git repository (local or remote)

        Raises:
            RepositoryError: If the path is not a valid Git repository
            FileNotFoundError: If the path does not exist
        """
        self.path = Path(path).resolve()
        self.logger = logging.getLogger(self.__class__.__name__)

        try:
            self.repo = Repo(str(self.path))
        except InvalidGitRepositoryError as e:
            raise RepositoryError(
                f"Invalid Git repository at {self.path}: {e}"
            )
        except Exception as e:
            raise RepositoryError(f"Failed to initialize repository: {e}")

        self.logger.info(f"Initialized repository at {self.path}")

    def get_commit_history(
        self, max_count: int = 50, branch: str = "HEAD"
    ) -> List[Dict[str, Any]]:
        """Get commit history from the repository.

        Args:
            max_count: Maximum number of commits to retrieve
            branch: Branch name or reference to get commits from

        Returns:
            List of dictionaries containing commit information

        Raises:
            RepositoryError: If unable to retrieve commit history
        """
        try:
            commits = []
            for commit in self.repo.iter_commits(branch, max_count=max_count):
                commit_info = {
                    "hash": commit.hexsha,
                    "short_hash": commit.hexsha[:8],
                    "author": {
                        "name": commit.author.name,
                        "email": commit.author.email,
                    },
                    "committer": {
                        "name": commit.committer.name,
                        "email": commit.committer.email,
                    },
                    "message": commit.message.strip(),
                    "summary": commit.summary,
                    "date": datetime.fromtimestamp(commit.committed_date),
                    "files_changed": len(commit.stats.files),
                    "insertions": commit.stats.total["insertions"],
                    "deletions": commit.stats.total["deletions"],
                }
                commits.append(commit_info)

            self.logger.info(f"Retrieved {len(commits)} commits from {branch}")
            return commits

        except Exception as e:
            raise RepositoryError(f"Failed to get commit history: {e}")

    def get_file_changes(
        self, commit_hash: Optional[str] = None, max_commits: int = 10
    ) -> Dict[str, Any]:
        """Get detailed file changes for analysis.

        Args:
            commit_hash: Specific commit to analyze (default: recent commits)
            max_commits: Number of recent commits to analyze if commit_hash is None

        Returns:
            Dictionary containing file change information

        Raises:
            RepositoryError: If unable to retrieve file changes
        """
        try:
            if commit_hash:
                commits = [self.repo.commit(commit_hash)]
            else:
                commits = list(
                    self.repo.iter_commits("HEAD", max_count=max_commits)
                )

            file_changes = {
                "modified_files": {},
                "new_files": [],
                "deleted_files": [],
                "renamed_files": [],
                "summary": {
                    "total_files": 0,
                    "total_insertions": 0,
                    "total_deletions": 0,
                },
            }

            for commit in commits:
                try:
                    # Get the diff for this commit
                    if commit.parents:
                        diffs = commit.parents[0].diff(commit)
                    else:
                        # First commit, compare against empty tree
                        diffs = commit.diff(git.NULL_TREE)

                    for diff in diffs:
                        file_path = diff.a_path or diff.b_path

                        if diff.change_type == "M":  # Modified
                            if file_path not in file_changes["modified_files"]:
                                file_changes["modified_files"][file_path] = {
                                    "changes": 0,
                                    "insertions": 0,
                                    "deletions": 0,
                                    "commits": [],
                                }
                            file_changes["modified_files"][file_path][
                                "changes"
                            ] += 1
                            file_changes["modified_files"][file_path][
                                "insertions"
                            ] += (diff.insertions or 0)
                            file_changes["modified_files"][file_path][
                                "deletions"
                            ] += (diff.deletions or 0)
                            file_changes["modified_files"][file_path][
                                "commits"
                            ].append(commit.hexsha[:8])

                        elif diff.change_type == "A":  # Added
                            if file_path not in file_changes["new_files"]:
                                file_changes["new_files"].append(file_path)

                        elif diff.change_type == "D":  # Deleted
                            if file_path not in file_changes["deleted_files"]:
                                file_changes["deleted_files"].append(file_path)

                        elif diff.change_type == "R":  # Renamed
                            rename_info = {
                                "old_path": diff.a_path,
                                "new_path": diff.b_path,
                                "similarity": (
                                    diff.rename_from
                                    if hasattr(diff, "rename_from")
                                    else None
                                ),
                            }
                            file_changes["renamed_files"].append(rename_info)

                    # Update summary
                    stats = commit.stats.total
                    file_changes["summary"]["total_insertions"] += stats.get(
                        "insertions", 0
                    )
                    file_changes["summary"]["total_deletions"] += stats.get(
                        "deletions", 0
                    )
                    file_changes["summary"]["total_files"] += stats.get(
                        "files", 0
                    )

                except Exception as commit_error:
                    self.logger.warning(
                        f"Error analyzing commit {commit.hexsha[:8]}: {commit_error}"
                    )
                    continue

            self.logger.info(
                f"Analyzed file changes across {len(commits)} commits"
            )
            return file_changes

        except Exception as e:
            raise RepositoryError(f"Failed to get file changes: {e}")

    def get_repository_info(self) -> Dict[str, Any]:
        """Get general repository information.

        Returns:
            Dictionary containing repository metadata

        Raises:
            RepositoryError: If unable to retrieve repository information
        """
        try:
            # Get basic repository info
            info = {
                "path": str(self.path),
                "name": self.path.name,
                "active_branch": (
                    self.repo.active_branch.name
                    if not self.repo.head.is_detached
                    else "detached"
                ),
                "total_commits": len(list(self.repo.iter_commits())),
                "remotes": [remote.name for remote in self.repo.remotes],
                "branches": [branch.name for branch in self.repo.branches],
                "tags": [tag.name for tag in self.repo.tags],
                "is_dirty": self.repo.is_dirty(),
                "untracked_files": self.repo.untracked_files,
            }

            # Get remote URL if available
            if self.repo.remotes:
                try:
                    origin = self.repo.remotes.origin
                    info["remote_url"] = (
                        list(origin.urls)[0] if origin.urls else None
                    )
                except AttributeError:
                    info["remote_url"] = None
            else:
                info["remote_url"] = None

            # Get recent activity
            try:
                latest_commit = next(iter(self.repo.iter_commits()))
                info["last_commit"] = {
                    "hash": latest_commit.hexsha[:8],
                    "message": latest_commit.summary,
                    "author": latest_commit.author.name,
                    "date": datetime.fromtimestamp(
                        latest_commit.committed_date
                    ).isoformat(),
                }
            except StopIteration:
                info["last_commit"] = None

            self.logger.info(f"Retrieved repository info for {info['name']}")
            return info

        except Exception as e:
            raise RepositoryError(f"Failed to get repository info: {e}")

    def get_file_content(
        self, file_path: str, commit_hash: Optional[str] = None
    ) -> Optional[str]:
        """Get content of a specific file.

        Args:
            file_path: Path to the file relative to repository root
            commit_hash: Specific commit to get file from (default: HEAD)

        Returns:
            File content as string, None if file doesn't exist

        Raises:
            RepositoryError: If unable to retrieve file content
        """
        try:
            if commit_hash:
                commit = self.repo.commit(commit_hash)
            else:
                commit = self.repo.head.commit

            try:
                blob = commit.tree[file_path]
                return blob.data_stream.read().decode("utf-8", errors="ignore")
            except KeyError:
                return None

        except Exception as e:
            raise RepositoryError(
                f"Failed to get file content for {file_path}: {e}"
            )

    def is_ignored(self, file_path: str) -> bool:
        """Check if a file path is ignored by .gitignore.

        Args:
            file_path: Path to check (relative to repository root)

        Returns:
            True if file is ignored, False otherwise
        """
        try:
            # Use git check-ignore command
            result = subprocess.run(
                ["git", "check-ignore", file_path],
                cwd=str(self.path),
                capture_output=True,
                text=True,
            )
            return result.returncode == 0
        except Exception:
            return False

    def get_commits(
        self, max_count: int = 50, branch: str = "HEAD"
    ) -> List[Commit]:
        """Get commit objects from the repository.

        Args:
            max_count: Maximum number of commits to retrieve
            branch: Branch name or reference to get commits from

        Returns:
            List of Commit objects

        Raises:
            RepositoryError: If unable to retrieve commits
        """
        try:
            commits = []
            for git_commit in self.repo.iter_commits(
                branch, max_count=max_count
            ):
                commits.append(Commit(git_commit))

            self.logger.info(
                f"Retrieved {len(commits)} Commit objects from {branch}"
            )
            return commits

        except Exception as e:
            raise RepositoryError(f"Failed to get commits: {e}")

    def get_branches(self, include_remote: bool = False) -> List[Branch]:
        """Get branch objects from the repository.

        Args:
            include_remote: Whether to include remote branches

        Returns:
            List of Branch objects

        Raises:
            RepositoryError: If unable to retrieve branches
        """
        try:
            branches = []
            active_branch_name = (
                self.repo.active_branch.name
                if not self.repo.head.is_detached
                else None
            )

            # Add local branches
            for git_branch in self.repo.branches:
                is_active = git_branch.name == active_branch_name
                branches.append(Branch(git_branch, self.repo, is_active))

            # Add remote branches if requested
            if include_remote:
                for remote in self.repo.remotes:
                    for git_branch in remote.refs:
                        branches.append(Branch(git_branch, self.repo, False))

            self.logger.info(
                f"Retrieved {len(branches)} Branch objects "
                f"({'with' if include_remote else 'without'} remotes)"
            )
            return branches

        except Exception as e:
            raise RepositoryError(f"Failed to get branches: {e}")

    def get_commit(self, commit_hash: str) -> Commit:
        """Get a specific commit object by hash.

        Args:
            commit_hash: Commit SHA, branch name, or tag name

        Returns:
            Commit object

        Raises:
            RepositoryError: If commit not found or unable to retrieve
        """
        try:
            git_commit = self.repo.commit(commit_hash)
            return Commit(git_commit)

        except Exception as e:
            raise RepositoryError(f"Failed to get commit {commit_hash}: {e}")

    def get_branch(self, branch_name: str) -> Branch:
        """Get a specific branch object by name.

        Args:
            branch_name: Name of the branch to retrieve

        Returns:
            Branch object

        Raises:
            RepositoryError: If branch not found or unable to retrieve
        """
        try:
            # Try local branch first
            for git_branch in self.repo.branches:
                if git_branch.name == branch_name:
                    active_branch_name = (
                        self.repo.active_branch.name
                        if not self.repo.head.is_detached
                        else None
                    )
                    is_active = git_branch.name == active_branch_name
                    return Branch(git_branch, self.repo, is_active)

            # Try remote branches
            for remote in self.repo.remotes:
                for git_branch in remote.refs:
                    if git_branch.name == branch_name:
                        return Branch(git_branch, self.repo, False)

            raise RepositoryError(f"Branch '{branch_name}' not found")

        except RepositoryError:
            raise
        except Exception as e:
            raise RepositoryError(f"Failed to get branch {branch_name}: {e}")

    def __str__(self) -> str:
        """String representation of the repository."""
        return f"Repository({self.path})"

    def __repr__(self) -> str:
        """Detailed string representation of the repository."""
        active_branch = (
            self.repo.active_branch.name
            if not self.repo.head.is_detached
            else "detached"
        )
        return (
            f"Repository(path='{self.path}', active_branch='{active_branch}')"
        )
