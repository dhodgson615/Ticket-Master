import logging
import os
import shutil
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urlparse

# TODO: Consider using a more robust dependency management approach
# such as poetry or pipenv for better handling of dependencies.
try:
    from git import GitCommandError, Repo

except ImportError:
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "GitPython>=3.1.40"]
    )

    from git import GitCommandError, Repo

try:
    import requests

except ImportError:
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "requests>=2.31.0"]
    )

    import requests


class GitHubCloneError(Exception):
    """Exception raised when GitHub repository cloning fails."""

    pass


class GitHubUtils:
    """Utilities for handling GitHub repositories."""

    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
        self._temp_dirs = []  # Track temporary directories for cleanup

    def is_public_repository(self, github_repo: str) -> bool:
        """Check if a GitHub repository is public.

        Args:
            github_repo: Repository in format "owner/repo"

        Returns:
            True if repository is public, False otherwise
        """
        try:
            # Make a simple GET request to GitHub API without authentication
            url = f"https://api.github.com/repos/{github_repo}"
            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Ticket-Master/0.1.0",
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                repo_data = response.json()
                return not repo_data.get("private", True)

            elif response.status_code == 404:
                # Repository not found or private
                return False

            elif response.status_code == 403:
                # Rate limited - try cloning approach as fallback
                self.logger.info(
                    f"GitHub API rate limited, attempting to clone {github_repo} to test public access"
                )

                try:
                    # Try to clone without authentication to test if it's public
                    clone_url = f"https://github.com/{github_repo}.git"
                    import subprocess

                    result = subprocess.run(
                        ["git", "ls-remote", clone_url],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )

                    return result.returncode == 0

                except Exception as e:
                    self.logger.warning(
                        f"Could not determine repository visibility via clone test: {e}"
                    )

                    return False

            else:
                self.logger.warning(
                    f"Unexpected response code {response.status_code} when checking repository visibility"
                )

                return False

        except Exception as e:
            self.logger.warning(f"Error checking repository visibility: {e}")
            return False

    def get_repository_info(
        self, github_repo: str
    ) -> Optional[Dict[str, Any]]:
        """Get basic repository information without authentication.

        Args:
            github_repo: Repository in format "owner/repo"

        Returns:
            Dictionary with repository info, or None if not accessible
        """
        try:
            url = f"https://api.github.com/repos/{github_repo}"

            headers = {
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Ticket-Master/0.1.0",
            }

            response = requests.get(url, headers=headers, timeout=10)

            if response.status_code == 200:
                repo_data = response.json()
                return {
                    "name": repo_data.get("name"),
                    "full_name": repo_data.get("full_name"),
                    "description": repo_data.get("description"),
                    "private": repo_data.get("private", True),
                    "clone_url": repo_data.get("clone_url"),
                    "ssh_url": repo_data.get("ssh_url"),
                    "default_branch": repo_data.get("default_branch", "main"),
                    "language": repo_data.get("language"),
                    "size": repo_data.get("size", 0),
                }

            elif response.status_code == 403:
                # Rate limited - return minimal info and let clone attempt determine accessibility
                self.logger.info(
                    "GitHub API rate limited, will attempt direct clone"
                )

                return {
                    "name": github_repo.split("/")[-1],
                    "full_name": github_repo,
                    "description": None,
                    "private": None,  # Unknown due to rate limiting
                    "clone_url": f"https://github.com/{github_repo}.git",
                    "ssh_url": f"git@github.com:{github_repo}.git",
                    "default_branch": "main",
                    "language": None,
                    "size": 0,
                }

            else:
                return None

        except Exception as e:
            self.logger.warning(f"Error getting repository info: {e}")
            return None

    def parse_github_url(self, github_input: str) -> str:
        """Parse various GitHub URL formats to extract owner/repo.

        Args:
            github_input: GitHub URL or owner/repo string

        Returns:
            Repository in "owner/repo" format

        Raises:
            ValueError: If input format is invalid
        """
        # If it's already in owner/repo format, validate and return
        if "/" in github_input and not github_input.startswith(
            ("http://", "https://")
        ):
            parts = github_input.strip().split("/")

            if len(parts) == 2 and all(part.strip() for part in parts):
                return f"{parts[0]}/{parts[1]}"

        # Parse URL formats
        if github_input.startswith(("http://", "https://")):
            parsed = urlparse(github_input)

            if parsed.netloc.lower() not in ("github.com", "www.github.com"):
                raise ValueError(
                    f"URL must be from github.com, got: {parsed.netloc}"
                )

            path_parts = [part for part in parsed.path.split("/") if part]

            if len(path_parts) >= 2:
                return f"{path_parts[0]}/{path_parts[1]}"

        raise ValueError(
            f"Invalid GitHub repository format: {github_input}. "
            "Expected formats: 'owner/repo' or 'https://github.com/owner/repo'"
        )

    def clone_repository(
        self,
        github_repo: str,
        local_path: Optional[str] = None,
        token: Optional[str] = None,
    ) -> str:
        """Clone a GitHub repository to local filesystem.

        Args:
            github_repo: Repository in format "owner/repo"
            local_path: Optional local path to clone to. If None, uses temp directory
            token: Optional GitHub token for private repositories

        Returns:
            Path to cloned repository

        Raises:
            GitHubCloneError: If cloning fails
        """
        try:
            # Get repository info to determine clone URL
            repo_info = self.get_repository_info(github_repo)

            if not repo_info:
                raise GitHubCloneError(
                    f"Repository {github_repo} not found or not accessible"
                )

            # Determine clone URL based on whether we have a token and repo is private
            if token and repo_info["private"]:
                # Use authenticated HTTPS URL for private repos
                clone_url = f"https://{token}@github.com/{github_repo}.git"

            else:
                # Use public HTTPS URL
                clone_url = repo_info["clone_url"]

            # Determine target directory
            if local_path:
                target_path = Path(local_path).resolve()
                target_path.mkdir(parents=True, exist_ok=True)

            else:
                # Create temporary directory
                temp_dir = tempfile.mkdtemp(
                    prefix=f"ticket-master-{github_repo.replace('/', '-')}-"
                )

                target_path = Path(temp_dir)
                self._temp_dirs.append(temp_dir)
                self.logger.info(f"Created temporary directory: {target_path}")

            self.logger.info(f"Cloning {github_repo} to {target_path}")

            # Clone the repository
            repo = Repo.clone_from(
                clone_url, target_path, depth=50
            )  # Shallow clone for performance

            self.logger.info(f"Successfully cloned {github_repo}")
            return str(target_path)

        except GitCommandError as e:
            if "Authentication failed" in str(
                e
            ) or "could not read Username" in str(e):
                raise GitHubCloneError(
                    f"Authentication failed for {github_repo}. "
                    "Repository may be private and require GITHUB_TOKEN."
                )

            else:
                raise GitHubCloneError(f"Failed to clone {github_repo}: {e}")

        except Exception as e:
            raise GitHubCloneError(
                f"Unexpected error cloning {github_repo}: {e}"
            )

    def cleanup_temp_directories(self):
        """Clean up any temporary directories created during cloning."""
        for temp_dir in self._temp_dirs:
            try:
                if os.path.exists(temp_dir):
                    shutil.rmtree(temp_dir)

                    self.logger.debug(
                        f"Cleaned up temporary directory: {temp_dir}"
                    )

            except Exception as e:
                self.logger.warning(
                    f"Failed to cleanup temporary directory {temp_dir}: {e}"
                )

        self._temp_dirs.clear()

    def __del__(self):
        """Cleanup on deletion."""
        try:
            self.cleanup_temp_directories()

        except Exception:
            pass  # Ignore errors during cleanup in destructor
