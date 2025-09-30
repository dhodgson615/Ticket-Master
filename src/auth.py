import logging
import os
import subprocess
import sys
from typing import Any, Dict, Optional

# Import with fallback installation
# TODO: Consider using a more robust dependency management approach
# such as poetry or pipenv for better handling of dependencies.
try:
    from github import Auth, Github
    from github.GithubException import BadCredentialsException

except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "PyGithub>=1.59.1"]
    )

    from github import Auth, Github
    from github.GithubException import BadCredentialsException


class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""

    pass


class GitHubAuthError(AuthenticationError):
    """Exception for GitHub authentication errors."""

    pass


class Authentication:
    """Handles GitHub authentication and client creation.

    This class provides methods to authenticate with GitHub using personal access tokens,
    validate credentials, and create authenticated GitHub client instances.

    Attributes:
        token: GitHub personal access token (if set)
        logger: Logger instance for this class
    """

    def __init__(self, token: Optional[str] = None) -> None:
        """Initialize Authentication with optional token.

        Args:
            token: GitHub personal access token (optional)
        """
        self.token = token
        self.logger = logging.getLogger(self.__class__.__name__)

    def get_token(self) -> str:
        """Get GitHub token from instance or environment variable.

        Returns:
            GitHub personal access token

        Raises:
            GitHubAuthError: If no token is available
        """
        token = self.token or os.getenv("GITHUB_TOKEN")

        if not token:
            raise GitHubAuthError(
                "GitHub token not provided. Set GITHUB_TOKEN environment variable "
                "or pass token parameter."
            )

        return token

    def create_client(self, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client.

        Args:
            token: GitHub personal access token (overrides instance token if provided)

        Returns:
            Authenticated GitHub client instance

        Raises:
            GitHubAuthError: If authentication fails or token is missing
        """
        # Use provided token, instance token, or environment variable
        auth_token = token or self.get_token()

        try:
            auth = Auth.Token(auth_token)
            github_client = Github(auth=auth)

            # Test authentication by getting user info
            user = github_client.get_user()
            self.logger.info(f"Authenticated as GitHub user: {user.login}")

            return github_client

        except BadCredentialsException as e:
            raise GitHubAuthError(f"Invalid GitHub credentials: {e}")

        except Exception as e:
            raise GitHubAuthError(f"Failed to authenticate with GitHub: {e}")

    def test_connection(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Test GitHub API connection and return user information.

        Args:
            token: GitHub personal access token (optional)

        Returns:
            Dictionary containing connection test results
        """
        try:
            github_client = self.create_client(token)
            user = github_client.get_user()
            rate_limit = github_client.get_rate_limit()

            return {
                "authenticated": True,
                "user": {
                    "login": user.login,
                    "name": user.name,
                    "email": user.email,
                    "public_repos": user.public_repos,
                    "followers": user.followers,
                },
                "rate_limit": {
                    "core": {
                        "limit": rate_limit.core.limit,
                        "remaining": rate_limit.core.remaining,
                        "reset": rate_limit.core.reset.isoformat(),
                    }
                },
            }

        except Exception as e:
            return {"authenticated": False, "error": str(e)}

    def is_authenticated(self, token: Optional[str] = None) -> bool:
        """Check if authentication is valid.

        Args:
            token: GitHub personal access token (optional)

        Returns:
            True if authentication is valid, False otherwise
        """
        try:
            github_client = self.create_client(token)
            github_client.get_user()
            return True

        except Exception:
            return False

    def get_user_info(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Get authenticated user information.

        Args:
            token: GitHub personal access token (optional)

        Returns:
            Dictionary containing user information

        Raises:
            GitHubAuthError: If authentication fails
        """
        github_client = self.create_client(token)
        user = github_client.get_user()

        return {
            "login": user.login,
            "name": user.name,
            "email": user.email,
            "public_repos": user.public_repos,
            "followers": user.followers,
            "following": user.following,
            "created_at": (
                user.created_at.isoformat() if user.created_at else None
            ),
            "updated_at": (
                user.updated_at.isoformat() if user.updated_at else None
            ),
        }

    def __str__(self) -> str:
        """String representation of the Authentication instance."""
        has_token = bool(self.token or os.getenv("GITHUB_TOKEN"))
        return f"Authentication(has_token={has_token})"

    def __repr__(self) -> str:
        """Developer representation of the Authentication instance."""
        has_token = bool(self.token or os.getenv("GITHUB_TOKEN"))

        return (
            f"Authentication(token_set={bool(self.token)}, "
            f"env_token_set={bool(os.getenv('GITHUB_TOKEN'))}, has_token={has_token})"
        )
