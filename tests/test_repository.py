"""
Tests for the Repository class.
"""

import os
import shutil
# Add src to path for imports
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master_consolidated import Repository, RepositoryError


class TestRepository:
    """Test cases for Repository class."""

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

        yield str(repo_path)

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_init_valid_repository(self, temp_git_repo):
        """Test Repository initialization with valid Git repository."""
        repo = Repository(temp_git_repo)
        assert repo.path == Path(temp_git_repo).resolve()
        assert repo.repo is not None

    def test_init_invalid_repository(self):
        """Test Repository initialization with invalid path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            non_git_path = Path(temp_dir) / "not_a_repo"
            non_git_path.mkdir()

            with pytest.raises(RepositoryError):
                Repository(str(non_git_path))

    def test_init_nonexistent_path(self):
        """Test Repository initialization with nonexistent path."""
        with pytest.raises(RepositoryError):
            Repository("/nonexistent/path")

    def test_get_commit_history(self, temp_git_repo):
        """Test getting commit history."""
        repo = Repository(temp_git_repo)
        commits = repo.get_commit_history(max_count=10)

        assert isinstance(commits, list)
        assert len(commits) >= 1  # At least the initial commit

        # Check commit structure
        commit = commits[0]
        required_keys = [
            "hash",
            "short_hash",
            "author",
            "committer",
            "message",
            "summary",
            "date",
        ]
        for key in required_keys:
            assert key in commit

        assert len(commit["short_hash"]) == 8
        assert commit["author"]["name"] == "Test User"
        assert commit["author"]["email"] == "test@example.com"

    def test_get_repository_info(self, temp_git_repo):
        """Test getting repository information."""
        repo = Repository(temp_git_repo)
        info = repo.get_repository_info()

        assert isinstance(info, dict)
        required_keys = [
            "path",
            "name",
            "active_branch",
            "total_commits",
            "branches",
            "is_dirty",
        ]
        for key in required_keys:
            assert key in info

        assert info["name"] == "test_repo"
        assert info["total_commits"] >= 1
        assert isinstance(info["branches"], list)

    def test_get_file_changes(self, temp_git_repo):
        """Test getting file changes."""
        repo = Repository(temp_git_repo)
        changes = repo.get_file_changes(max_commits=5)

        assert isinstance(changes, dict)
        required_keys = [
            "modified_files",
            "new_files",
            "deleted_files",
            "renamed_files",
            "summary",
        ]
        for key in required_keys:
            assert key in changes

        assert isinstance(changes["summary"], dict)
        summary_keys = ["total_files", "total_insertions", "total_deletions"]
        for key in summary_keys:
            assert key in changes["summary"]

    def test_get_file_content_existing(self, temp_git_repo):
        """Test getting content of existing file."""
        repo = Repository(temp_git_repo)
        content = repo.get_file_content("README.md")

        assert content is not None
        assert "# Test Repository" in content

    def test_get_file_content_nonexistent(self, temp_git_repo):
        """Test getting content of nonexistent file."""
        repo = Repository(temp_git_repo)
        content = repo.get_file_content("nonexistent.txt")

        assert content is None

    def test_is_ignored(self, temp_git_repo):
        """Test checking if file is ignored."""
        repo = Repository(temp_git_repo)

        # Create .gitignore
        gitignore_path = repo.path / ".gitignore"
        gitignore_path.write_text("*.pyc\n__pycache__/\n")

        # Test ignored file
        assert repo.is_ignored("test.pyc") == True

        # Test non-ignored file
        assert repo.is_ignored("README.md") == False

    def test_str_representation(self, temp_git_repo):
        """Test string representation of Repository."""
        repo = Repository(temp_git_repo)
        str_repr = str(repo)

        assert "Repository(" in str_repr
        assert str(repo.path) in str_repr

    def test_repr_representation(self, temp_git_repo):
        """Test detailed string representation of Repository."""
        repo = Repository(temp_git_repo)
        repr_str = repr(repo)

        assert "Repository(" in repr_str
        assert "path=" in repr_str
        assert "active_branch=" in repr_str


class TestRepositoryErrorHandling:
    """Test error handling in Repository class."""

    def test_repository_error_inheritance(self):
        """Test that RepositoryError inherits from Exception."""
        error = RepositoryError("test error")
        assert isinstance(error, Exception)
        assert str(error) == "test error"

    @patch("repository.Repo")
    def test_init_with_git_exception(self, mock_repo):
        """Test Repository initialization when Git operations fail."""
        mock_repo.side_effect = Exception("Git error")

        with pytest.raises(RepositoryError) as exc_info:
            Repository("/some/path")

        assert "Failed to initialize repository" in str(exc_info.value)

    @pytest.fixture
    def temp_git_repo_for_error_tests(self):
        """Create a temporary Git repository for error testing."""
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

        yield str(repo_path)

        # Cleanup
        shutil.rmtree(temp_dir)

    def test_commit_history_with_invalid_branch(
        self, temp_git_repo_for_error_tests
    ):
        """Test getting commit history with invalid branch."""
        repo = Repository(temp_git_repo_for_error_tests)

        with pytest.raises(RepositoryError):
            repo.get_commit_history(branch="nonexistent-branch")

    @patch("repository.subprocess.run")
    def test_is_ignored_with_subprocess_error(
        self, mock_run, temp_git_repo_for_error_tests
    ):
        """Test is_ignored method when subprocess fails."""
        mock_run.side_effect = Exception("Subprocess error")

        repo = Repository(temp_git_repo_for_error_tests)
        result = repo.is_ignored("test.txt")

        # Should return False when subprocess fails
        assert result == False


if __name__ == "__main__":
    pytest.main([__file__])
