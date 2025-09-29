"""
Tests for Git object classes: Commit, Branch, and PullRequest.

This module provides comprehensive tests for the newly implemented Git object classes
to ensure they work correctly and integrate properly with the existing codebase.
"""

import os
import shutil
# Add src to path for imports
import sys
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master_consolidated import Branch, BranchError
from ticket_master_consolidated import Commit, CommitError
from ticket_master_consolidated import PullRequest, PullRequestError
from ticket_master_consolidated import Repository, RepositoryError


class TestCommit:
    """Test cases for Commit class."""

    @pytest.fixture
    def mock_git_commit(self):
        """Create a mock GitPython Commit object."""
        mock_commit = Mock()
        mock_commit.hexsha = "abcdef1234567890abcdef1234567890abcdef12"
        mock_commit.author.name = "Test Author"
        mock_commit.author.email = "author@example.com"
        mock_commit.committer.name = "Test Committer"
        mock_commit.committer.email = "committer@example.com"
        mock_commit.message = "Test commit message\n\nDetailed description"
        mock_commit.summary = "Test commit message"
        mock_commit.committed_date = 1640995200  # 2022-01-01 00:00:00 UTC
        mock_commit.parents = []

        # Mock stats
        mock_commit.stats.total = {
            "insertions": 10,
            "deletions": 5,
            "files": 2,
        }
        mock_commit.stats.files = {"file1.py": {}, "file2.py": {}}

        return mock_commit

    def test_init_valid_commit(self, mock_git_commit):
        """Test Commit initialization with valid GitPython commit."""
        commit = Commit(mock_git_commit)

        assert commit.hash == "abcdef1234567890abcdef1234567890abcdef12"
        assert commit.short_hash == "abcdef12"
        assert commit.author["name"] == "Test Author"
        assert commit.author["email"] == "author@example.com"
        assert commit.message == "Test commit message\n\nDetailed description"
        assert commit.summary == "Test commit message"
        assert commit.files_changed == 2
        assert commit.insertions == 10
        assert commit.deletions == 5

    def test_init_invalid_commit(self):
        """Test Commit initialization with invalid input."""
        with pytest.raises(CommitError):
            Commit("not_a_commit")

    def test_is_merge_commit(self, mock_git_commit):
        """Test merge commit detection."""
        # Single parent - not a merge
        mock_git_commit.parents = [Mock()]
        commit = Commit(mock_git_commit)
        assert not commit.is_merge_commit()

        # Multiple parents - is a merge
        mock_git_commit.parents = [Mock(), Mock()]
        commit = Commit(mock_git_commit)
        assert commit.is_merge_commit()

    def test_get_parents(self, mock_git_commit):
        """Test getting parent commits."""
        parent1 = Mock()
        parent1.hexsha = "parent1hash"
        parent1.author.name = "Parent Author"
        parent1.author.email = "parent@example.com"
        parent1.committer.name = "Parent Committer"
        parent1.committer.email = "parent@example.com"
        parent1.message = "Parent commit"
        parent1.summary = "Parent commit"
        parent1.committed_date = 1640908800
        parent1.parents = []
        parent1.stats.total = {"insertions": 0, "deletions": 0, "files": 0}
        parent1.stats.files = {}

        mock_git_commit.parents = [parent1]
        commit = Commit(mock_git_commit)

        parents = commit.get_parents()
        assert len(parents) == 1
        assert isinstance(parents[0], Commit)
        assert parents[0].hash == "parent1hash"

    def test_to_dict(self, mock_git_commit):
        """Test converting commit to dictionary."""
        commit = Commit(mock_git_commit)
        commit_dict = commit.to_dict()

        assert (
            commit_dict["hash"] == "abcdef1234567890abcdef1234567890abcdef12"
        )
        assert commit_dict["short_hash"] == "abcdef12"
        assert commit_dict["author"]["name"] == "Test Author"
        assert (
            commit_dict["message"]
            == "Test commit message\n\nDetailed description"
        )
        assert commit_dict["files_changed"] == 2
        assert commit_dict["insertions"] == 10
        assert commit_dict["deletions"] == 5
        assert "date" in commit_dict

    def test_str_representation(self, mock_git_commit):
        """Test string representation of commit."""
        commit = Commit(mock_git_commit)
        assert str(commit) == "abcdef12: Test commit message"

    def test_repr_representation(self, mock_git_commit):
        """Test detailed string representation of commit."""
        commit = Commit(mock_git_commit)
        repr_str = repr(commit)
        assert "Commit(" in repr_str
        assert "abcdef12" in repr_str
        assert "Test Author" in repr_str

    def test_equality(self, mock_git_commit):
        """Test commit equality comparison."""
        commit1 = Commit(mock_git_commit)
        commit2 = Commit(mock_git_commit)

        assert commit1 == commit2

        # Different commit
        mock_git_commit2 = Mock()
        mock_git_commit2.hexsha = "different_hash"
        mock_git_commit2.author.name = "Test Author"
        mock_git_commit2.author.email = "author@example.com"
        mock_git_commit2.committer.name = "Test Committer"
        mock_git_commit2.committer.email = "committer@example.com"
        mock_git_commit2.message = "Different message"
        mock_git_commit2.summary = "Different message"
        mock_git_commit2.committed_date = 1640995200
        mock_git_commit2.parents = []
        mock_git_commit2.stats.total = {
            "insertions": 0,
            "deletions": 0,
            "files": 0,
        }
        mock_git_commit2.stats.files = {}

        commit3 = Commit(mock_git_commit2)
        assert commit1 != commit3


class TestBranch:
    """Test cases for Branch class."""

    @pytest.fixture
    def mock_git_branch(self):
        """Create a mock GitPython Head object."""
        mock_branch = Mock()
        mock_branch.name = "feature/test-branch"

        # Mock commit
        mock_commit = Mock()
        mock_commit.hexsha = "branch_commit_hash"
        mock_commit.author.name = "Branch Author"
        mock_commit.author.email = "branch@example.com"
        mock_commit.committer.name = "Branch Committer"
        mock_commit.committer.email = "branch@example.com"
        mock_commit.message = "Branch commit message"
        mock_commit.summary = "Branch commit message"
        mock_commit.committed_date = 1640995200
        mock_commit.parents = []
        mock_commit.stats.total = {"insertions": 5, "deletions": 2, "files": 1}
        mock_commit.stats.files = {"branch_file.py": {}}

        mock_branch.commit = mock_commit

        return mock_branch

    @pytest.fixture
    def mock_remote_branch(self):
        """Create a mock GitPython RemoteReference object."""
        mock_branch = Mock()
        mock_branch.name = "origin/main"
        mock_branch.__class__.__name__ = (
            "RemoteReference"  # For remote detection
        )

        # Mock commit
        mock_commit = Mock()
        mock_commit.hexsha = "remote_commit_hash"
        mock_commit.author.name = "Remote Author"
        mock_commit.author.email = "remote@example.com"
        mock_commit.committer.name = "Remote Committer"
        mock_commit.committer.email = "remote@example.com"
        mock_commit.message = "Remote commit message"
        mock_commit.summary = "Remote commit message"
        mock_commit.committed_date = 1640995200
        mock_commit.parents = []
        mock_commit.stats.total = {"insertions": 3, "deletions": 1, "files": 1}
        mock_commit.stats.files = {"remote_file.py": {}}

        mock_branch.commit = mock_commit

        return mock_branch

    def test_init_local_branch(self, mock_git_branch):
        """Test Branch initialization with local branch."""
        branch = Branch(mock_git_branch, is_active=True)

        assert branch.name == "feature/test-branch"
        assert branch.is_active is True
        assert branch.is_remote is False
        assert branch.remote_name is None
        assert branch.head_commit is not None
        assert branch.head_commit.hash == "branch_commit_hash"

    def test_init_remote_branch(self, mock_remote_branch):
        """Test Branch initialization with remote branch."""
        branch = Branch(mock_remote_branch, is_active=False)

        assert branch.name == "origin/main"
        assert branch.is_active is False
        assert branch.is_remote is True
        assert branch.remote_name == "origin"
        assert branch.head_commit is not None

    def test_init_invalid_branch(self):
        """Test Branch initialization with invalid input."""
        with pytest.raises(BranchError):
            Branch("not_a_branch")

    def test_get_last_activity(self, mock_git_branch):
        """Test getting last activity date."""
        branch = Branch(mock_git_branch, is_active=False)
        last_activity = branch.get_last_activity()

        assert last_activity is not None
        assert isinstance(last_activity, datetime)

    def test_to_dict(self, mock_git_branch):
        """Test converting branch to dictionary."""
        branch = Branch(mock_git_branch, is_active=True)
        branch_dict = branch.to_dict()

        assert branch_dict["name"] == "feature/test-branch"
        assert branch_dict["is_active"] is True
        assert branch_dict["is_remote"] is False
        assert branch_dict["remote_name"] is None
        assert "head_commit" in branch_dict
        assert "last_activity" in branch_dict

    def test_str_representation(self, mock_git_branch):
        """Test string representation of branch."""
        # Active branch
        branch = Branch(mock_git_branch, is_active=True)
        assert str(branch).startswith("* feature/test-branch")

        # Inactive branch
        branch = Branch(mock_git_branch, is_active=False)
        assert str(branch).startswith("  feature/test-branch")

    def test_repr_representation(self, mock_git_branch):
        """Test detailed string representation of branch."""
        branch = Branch(mock_git_branch, is_active=True)
        repr_str = repr(branch)
        assert "Branch(" in repr_str
        assert "feature/test-branch" in repr_str
        assert "is_active=True" in repr_str

    def test_equality(self, mock_git_branch):
        """Test branch equality comparison."""
        branch1 = Branch(mock_git_branch, is_active=True)
        branch2 = Branch(
            mock_git_branch, is_active=False
        )  # Different active status

        # Same name and remote status should be equal
        assert branch1 == branch2

        # Different branch
        mock_git_branch2 = Mock()
        mock_git_branch2.name = "different-branch"
        mock_git_branch2.commit = Mock()
        mock_git_branch2.commit.hexsha = "different_hash"
        mock_git_branch2.commit.author.name = "Author"
        mock_git_branch2.commit.author.email = "author@example.com"
        mock_git_branch2.commit.committer.name = "Committer"
        mock_git_branch2.commit.committer.email = "committer@example.com"
        mock_git_branch2.commit.message = "Message"
        mock_git_branch2.commit.summary = "Message"
        mock_git_branch2.commit.committed_date = 1640995200
        mock_git_branch2.commit.parents = []
        mock_git_branch2.commit.stats.total = {
            "insertions": 0,
            "deletions": 0,
            "files": 0,
        }
        mock_git_branch2.commit.stats.files = {}

        branch3 = Branch(mock_git_branch2, is_active=False)
        assert branch1 != branch3


class TestPullRequest:
    """Test cases for PullRequest class."""

    @pytest.fixture
    def mock_github_pr(self):
        """Create a mock PyGithub PullRequest object."""
        mock_pr = Mock()
        mock_pr.number = 42
        mock_pr.title = "Test Pull Request"
        mock_pr.body = "This is a test pull request description"
        mock_pr.state = "open"
        mock_pr.draft = False
        mock_pr.merged = False
        mock_pr.mergeable = True

        # Mock user
        mock_pr.user.login = "testuser"
        mock_pr.user.name = "Test User"
        mock_pr.user.email = "test@example.com"
        mock_pr.user.avatar_url = "https://github.com/avatar.png"

        # Mock dates
        mock_pr.created_at = datetime(2022, 1, 1, 10, 0, 0)
        mock_pr.updated_at = datetime(2022, 1, 2, 15, 30, 0)
        mock_pr.merged_at = None

        # Mock branch info
        mock_pr.head.ref = "feature/test-branch"
        mock_pr.base.ref = "main"

        # Mock stats
        mock_pr.commits = 3
        mock_pr.changed_files = 5
        mock_pr.additions = 100
        mock_pr.deletions = 25

        return mock_pr

    def test_init_valid_pr(self, mock_github_pr):
        """Test PullRequest initialization with valid PyGithub PR."""
        pr = PullRequest(mock_github_pr)

        assert pr.number == 42
        assert pr.title == "Test Pull Request"
        assert pr.description == "This is a test pull request description"
        assert pr.state == "open"
        assert pr.is_draft is False
        assert pr.merged is False
        assert pr.author["login"] == "testuser"
        assert pr.source_branch == "feature/test-branch"
        assert pr.target_branch == "main"
        assert pr.commits_count == 3
        assert pr.changed_files_count == 5
        assert pr.additions == 100
        assert pr.deletions == 25

    def test_init_invalid_pr(self):
        """Test PullRequest initialization with invalid input."""
        with pytest.raises(PullRequestError):
            PullRequest("not_a_pr")

    def test_is_mergeable(self, mock_github_pr):
        """Test mergeable status check."""
        pr = PullRequest(mock_github_pr)
        assert pr.is_mergeable() is True

        # Test closed PR
        mock_github_pr.state = "closed"
        pr = PullRequest(mock_github_pr)
        assert pr.is_mergeable() is False

        # Test not mergeable
        mock_github_pr.state = "open"
        mock_github_pr.mergeable = False
        pr = PullRequest(mock_github_pr)
        assert pr.is_mergeable() is False

    def test_to_dict(self, mock_github_pr):
        """Test converting pull request to dictionary."""
        pr = PullRequest(mock_github_pr)
        pr_dict = pr.to_dict()

        assert pr_dict["number"] == 42
        assert pr_dict["title"] == "Test Pull Request"
        assert pr_dict["state"] == "open"
        assert pr_dict["source_branch"] == "feature/test-branch"
        assert pr_dict["target_branch"] == "main"
        assert pr_dict["commits_count"] == 3
        assert pr_dict["changed_files_count"] == 5
        assert pr_dict["additions"] == 100
        assert pr_dict["deletions"] == 25
        assert "author" in pr_dict
        assert "created_at" in pr_dict

    def test_str_representation(self, mock_github_pr):
        """Test string representation of pull request."""
        pr = PullRequest(mock_github_pr)
        assert str(pr) == "PR #42 (OPEN): Test Pull Request"

        # Test merged PR
        mock_github_pr.merged = True
        pr = PullRequest(mock_github_pr)
        assert str(pr) == "PR #42 (MERGED): Test Pull Request"

    def test_repr_representation(self, mock_github_pr):
        """Test detailed string representation of pull request."""
        pr = PullRequest(mock_github_pr)
        repr_str = repr(pr)
        assert "PullRequest(" in repr_str
        assert "number=42" in repr_str
        assert "testuser" in repr_str

    def test_equality(self, mock_github_pr):
        """Test pull request equality comparison."""
        pr1 = PullRequest(mock_github_pr)
        pr2 = PullRequest(mock_github_pr)

        assert pr1 == pr2

        # Different PR number
        mock_github_pr2 = Mock()
        mock_github_pr2.number = 43
        mock_github_pr2.title = "Different PR"
        mock_github_pr2.body = "Different description"
        mock_github_pr2.state = "open"
        mock_github_pr2.draft = False
        mock_github_pr2.merged = False
        mock_github_pr2.mergeable = True
        mock_github_pr2.user.login = "testuser"
        mock_github_pr2.user.name = "Test User"
        mock_github_pr2.user.email = "test@example.com"
        mock_github_pr2.user.avatar_url = "https://github.com/avatar.png"
        mock_github_pr2.created_at = datetime(2022, 1, 1, 10, 0, 0)
        mock_github_pr2.updated_at = datetime(2022, 1, 2, 15, 30, 0)
        mock_github_pr2.merged_at = None
        mock_github_pr2.head.ref = "feature/different-branch"
        mock_github_pr2.base.ref = "main"
        mock_github_pr2.commits = 2
        mock_github_pr2.changed_files = 3
        mock_github_pr2.additions = 50
        mock_github_pr2.deletions = 10

        pr3 = PullRequest(mock_github_pr2)
        assert pr1 != pr3


class TestRepositoryIntegration:
    """Test cases for Repository integration with Git object classes."""

    @pytest.fixture
    def temp_git_repo(self):
        """Create a temporary Git repository for testing."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir) / "test_repo"
        repo_path.mkdir()

        # Initialize git repo
        os.system(f"cd {repo_path} && git init")
        os.system(
            f"cd {repo_path} && git config user.email 'test@example.com'"
        )
        os.system(f"cd {repo_path} && git config user.name 'Test User'")

        # Create initial commit
        test_file = repo_path / "README.md"
        test_file.write_text("# Test Repository")
        os.system(f"cd {repo_path} && git add README.md")
        os.system(f"cd {repo_path} && git commit -m 'Initial commit'")

        # Create a feature branch
        os.system(f"cd {repo_path} && git checkout -b feature/test")
        test_file2 = repo_path / "test.txt"
        test_file2.write_text("Test content")
        os.system(f"cd {repo_path} && git add test.txt")
        os.system(f"cd {repo_path} && git commit -m 'Add test file'")
        os.system(f"cd {repo_path} && git checkout master")

        yield str(repo_path)

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_repository_get_commits(self, temp_git_repo):
        """Test Repository.get_commits() returns Commit objects."""
        repo = Repository(temp_git_repo)
        commits = repo.get_commits(max_count=10)

        assert isinstance(commits, list)
        assert len(commits) > 0
        assert all(isinstance(commit, Commit) for commit in commits)

        # Test first commit
        first_commit = commits[0]
        assert hasattr(first_commit, "hash")
        assert hasattr(first_commit, "message")
        assert hasattr(first_commit, "author")

    def test_repository_get_branches(self, temp_git_repo):
        """Test Repository.get_branches() returns Branch objects."""
        repo = Repository(temp_git_repo)
        branches = repo.get_branches()

        assert isinstance(branches, list)
        assert len(branches) >= 2  # main and feature/test
        assert all(isinstance(branch, Branch) for branch in branches)

        # Check that we have master branch (default in older Git versions)
        branch_names = [branch.name for branch in branches]
        assert "master" in branch_names
        assert "feature/test" in branch_names

        # Check that one branch is active
        active_branches = [branch for branch in branches if branch.is_active]
        assert len(active_branches) == 1

    def test_repository_get_commit(self, temp_git_repo):
        """Test Repository.get_commit() returns specific Commit object."""
        repo = Repository(temp_git_repo)
        commits = repo.get_commits(max_count=1)
        first_commit_hash = commits[0].hash

        # Get the same commit by hash
        commit = repo.get_commit(first_commit_hash)
        assert isinstance(commit, Commit)
        assert commit.hash == first_commit_hash

    def test_repository_get_branch(self, temp_git_repo):
        """Test Repository.get_branch() returns specific Branch object."""
        repo = Repository(temp_git_repo)

        # Get master branch (default in older Git versions)
        master_branch = repo.get_branch("master")
        assert isinstance(master_branch, Branch)
        assert master_branch.name == "master"

        # Get feature branch
        feature_branch = repo.get_branch("feature/test")
        assert isinstance(feature_branch, Branch)
        assert feature_branch.name == "feature/test"

    def test_repository_get_branch_not_found(self, temp_git_repo):
        """Test Repository.get_branch() raises error for non-existent branch."""
        repo = Repository(temp_git_repo)

        with pytest.raises(RepositoryError):
            repo.get_branch("non-existent-branch")


if __name__ == "__main__":
    pytest.main([__file__])
