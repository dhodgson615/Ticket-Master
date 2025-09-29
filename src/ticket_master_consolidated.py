"""
Ticket-Master: AI-powered GitHub issue generator (Consolidated)

A tool that uses AI to suggest GitHub issues with descriptions
based on the contents of a Git repository.

This file contains all the consolidated source code in a single file
to simplify import dependencies.
"""

# Standard library imports
import json
import logging
import os
import sqlite3
import subprocess
import sys
import time
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Third-party imports
import yaml
import git
from git import InvalidGitRepositoryError, Repo
from github import Auth, Github
from github.GithubException import BadCredentialsException, GithubException, RateLimitExceededException
import requests
import ollama

# Version information
__version__ = "0.1.0"
__author__ = "Ticket-Master Contributors"
__description__ = "AI-powered GitHub issue generator"


# ==================== COLORS MODULE ====================

class Colors:
    """Global color constants using ANSI escape codes."""
    
    # Text colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"
    
    # Background colors
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"
    BG_MAGENTA = "\033[105m"
    BG_CYAN = "\033[106m"
    
    # Text styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    STRIKETHROUGH = "\033[9m"
    
    # Reset
    RESET = "\033[0m"
    END = "\033[0m"  # Alias for RESET

# Export individual color constants to maintain compatibility
RED = Colors.RED
GREEN = Colors.GREEN
YELLOW = Colors.YELLOW
BLUE = Colors.BLUE
MAGENTA = Colors.MAGENTA
CYAN = Colors.CYAN
WHITE = Colors.WHITE
GRAY = Colors.GRAY
BOLD = Colors.BOLD
DIM = Colors.DIM
ITALIC = Colors.ITALIC
UNDERLINE = Colors.UNDERLINE
RESET = Colors.RESET
END = Colors.END

# Global flag to control color output
_color_enabled = True

def supports_color() -> bool:
    """Check if terminal supports color output."""
    return (
        hasattr(sys.stdout, "isatty") and
        sys.stdout.isatty() and
        os.getenv("TERM", "").lower() != "dumb" and
        os.getenv("NO_COLOR", "").lower() not in ("1", "true", "yes")
    )

def is_color_enabled() -> bool:
    """Check if color output is enabled."""
    return _color_enabled and supports_color()

def enable_colors(enabled: bool = True) -> None:
    """Enable or disable color output."""
    global _color_enabled
    _color_enabled = enabled

def colorize(text: str, *color_codes: str) -> str:
    """Apply color codes to text."""
    if not is_color_enabled():
        return text
    
    color_prefix = "".join(color_codes)
    return f"{color_prefix}{text}{Colors.RESET}"

def print_colored(text: str, *color_codes: str, **kwargs: Any) -> None:
    """Print colored text to stdout."""
    colored_text = colorize(text, *color_codes)
    print(colored_text, **kwargs)

# Convenience functions for common color combinations
def success(text: str, bold: bool = False) -> str:
    """Format success message in green."""
    colors = [Colors.GREEN]
    if bold:
        colors.append(Colors.BOLD)
    return colorize(text, *colors)

def error(text: str, bold: bool = True) -> str:
    """Format error message in red."""
    colors = [Colors.RED]
    if bold:
        colors.append(Colors.BOLD)
    return colorize(text, *colors)

def warning(text: str, bold: bool = False) -> str:
    """Format warning message in yellow."""
    colors = [Colors.YELLOW]
    if bold:
        colors.append(Colors.BOLD)
    return colorize(text, *colors)

def info(text: str, bold: bool = False) -> str:
    """Format info message in blue."""
    colors = [Colors.BLUE]
    if bold:
        colors.append(Colors.BOLD)
    return colorize(text, *colors)

def header(text: str) -> str:
    """Format header in cyan and bold."""
    return colorize(text, Colors.CYAN, Colors.BOLD)

def highlight(text: str) -> str:
    """Format highlighted text in white and bold."""
    return colorize(text, Colors.WHITE, Colors.BOLD)

def dim(text: str) -> str:
    """Format dimmed text."""
    return colorize(text, Colors.DIM)

def progress_bar(current: int, total: int, width: int = 50, 
                 prefix: str = "", suffix: str = "") -> str:
    """Create a colored progress bar."""
    if total == 0:
        percentage = 100
    else:
        percentage = min(100, (current * 100) // total)
    
    filled_width = (width * percentage) // 100
    bar = '█' * filled_width + '░' * (width - filled_width)
    
    bar_colored = colorize(bar[:filled_width], Colors.GREEN) + colorize(bar[filled_width:], Colors.GRAY)
    
    return f"{prefix} {bar_colored} {percentage}% {suffix}"


# ==================== AUTHENTICATION MODULE ====================

class AuthenticationError(Exception):
    """Custom exception for authentication-related errors."""
    pass

class GitHubAuthError(AuthenticationError):
    """Exception for GitHub authentication errors."""
    pass

class Authentication:
    """Handles GitHub authentication and client creation."""
    
    def __init__(self, token: Optional[str] = None) -> None:
        """Initialize Authentication with optional token."""
        self.token = token
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def get_token(self) -> str:
        """Get GitHub token from instance or environment variable."""
        token = self.token or os.getenv("GITHUB_TOKEN")
        
        if not token:
            raise GitHubAuthError(
                "GitHub token not provided. Set GITHUB_TOKEN environment variable "
                "or pass token parameter."
            )
        
        return token
    
    def create_client(self, token: Optional[str] = None) -> Github:
        """Create authenticated GitHub client."""
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
            raise GitHubAuthError(f"Failed to create GitHub client: {e}")
    
    def validate_token(self, token: Optional[str] = None) -> Dict[str, Any]:
        """Validate GitHub token and return user information."""
        try:
            client = self.create_client(token)
            user = client.get_user()
            
            # Get rate limit information
            rate_limit = client.get_rate_limit()
            
            return {
                "valid": True,
                "user": {
                    "login": user.login,
                    "name": user.name,
                    "email": user.email,
                    "id": user.id,
                },
                "rate_limit": {
                    "core": {
                        "limit": rate_limit.core.limit,
                        "remaining": rate_limit.core.remaining,
                        "reset": rate_limit.core.reset,
                    },
                    "search": {
                        "limit": rate_limit.search.limit,
                        "remaining": rate_limit.search.remaining,
                        "reset": rate_limit.search.reset,
                    },
                },
            }
            
        except GitHubAuthError as e:
            return {"valid": False, "error": str(e)}
        except Exception as e:
            return {"valid": False, "error": f"Unexpected error: {e}"}


# ==================== REPOSITORY MODULE ====================

class RepositoryError(Exception):
    """Custom exception for repository-related errors."""
    pass

class CommitError(Exception):
    """Custom exception for commit-related errors."""
    pass

class Commit:
    """Represents a Git commit with associated metadata."""
    
    def __init__(self, commit_data: Dict[str, Any]) -> None:
        """Initialize Commit from commit data dictionary."""
        self.hash = commit_data.get("hash", "")
        self.short_hash = commit_data.get("short_hash", "")
        self.author = commit_data.get("author", {})
        self.committer = commit_data.get("committer", {})
        self.message = commit_data.get("message", "")
        self.summary = commit_data.get("summary", "")
        self.date = commit_data.get("date", datetime.now())
        self.files_changed = commit_data.get("files_changed", 0)
        self.insertions = commit_data.get("insertions", 0)
        self.deletions = commit_data.get("deletions", 0)

class BranchError(Exception):
    """Custom exception for branch-related errors."""
    pass

class Branch:
    """Represents a Git branch with associated metadata."""
    
    def __init__(self, name: str, is_active: bool = False, 
                 last_commit: Optional[str] = None) -> None:
        """Initialize Branch with name and metadata."""
        self.name = name
        self.is_active = is_active
        self.last_commit = last_commit

class PullRequestError(Exception):
    """Custom exception for pull request-related errors."""
    pass

class PullRequest:
    """Represents a GitHub pull request with associated metadata."""
    
    def __init__(self, pr_data: Dict[str, Any]) -> None:
        """Initialize PullRequest from PR data dictionary."""
        self.number = pr_data.get("number", 0)
        self.title = pr_data.get("title", "")
        self.body = pr_data.get("body", "")
        self.state = pr_data.get("state", "")
        self.author = pr_data.get("author", "")
        self.created_at = pr_data.get("created_at", datetime.now())
        self.updated_at = pr_data.get("updated_at", datetime.now())

class Repository:
    """Handles Git repository operations and analysis."""
    
    def __init__(self, path: str) -> None:
        """Initialize the Repository with a given path."""
        self.path = Path(path).resolve()
        self.logger = logging.getLogger(self.__class__.__name__)
        
        try:
            self.repo = Repo(str(self.path))
        except InvalidGitRepositoryError as e:
            raise RepositoryError(f"Invalid Git repository at {self.path}: {e}")
        except Exception as e:
            raise RepositoryError(f"Failed to initialize repository: {e}")
        
        self.logger.info(f"Initialized repository at {self.path}")
    
    def get_commit_history(self, max_count: int = 50, branch: str = "HEAD") -> List[Dict[str, Any]]:
        """Get commit history from the repository."""
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
                    "message": commit.message,
                    "summary": commit.summary,
                    "date": commit.committed_datetime,
                    "files_changed": len(commit.stats.files),
                    "insertions": commit.stats.total["insertions"],
                    "deletions": commit.stats.total["deletions"],
                }
                commits.append(commit_info)
            
            self.logger.info(f"Retrieved {len(commits)} commits from {branch}")
            return commits
            
        except Exception as e:
            raise RepositoryError(f"Failed to get commit history: {e}")
    
    def get_repository_info(self) -> Dict[str, Any]:
        """Get basic repository information."""
        try:
            active_branch = self.repo.active_branch.name
            remotes = [remote.name for remote in self.repo.remotes]
            
            # Try to get repository name from remote URL
            repo_name = self.path.name
            if remotes:
                try:
                    remote_url = self.repo.remotes[0].url
                    if "github.com" in remote_url:
                        # Extract repo name from GitHub URL
                        if remote_url.endswith(".git"):
                            remote_url = remote_url[:-4]
                        repo_name = remote_url.split("/")[-1]
                except Exception:
                    pass
            
            return {
                "name": repo_name,
                "path": str(self.path),
                "active_branch": active_branch,
                "remotes": remotes,
                "is_bare": self.repo.bare,
                "head_commit": self.repo.head.commit.hexsha[:8] if not self.repo.bare else None,
            }
            
        except Exception as e:
            raise RepositoryError(f"Failed to get repository info: {e}")
    
    def get_file_changes(self, max_commits: int = 50) -> Dict[str, Any]:
        """Analyze file changes across recent commits."""
        try:
            file_stats = {}
            new_files = []
            deleted_files = []
            renamed_files = []
            
            commits = list(self.repo.iter_commits("HEAD", max_count=max_commits))
            
            for commit in commits:
                # For the first commit, all files are new
                if not commit.parents:
                    continue
                
                parent = commit.parents[0]
                diffs = parent.diff(commit)
                
                for diff in diffs:
                    if diff.change_type == "A":  # Added
                        if diff.b_path:
                            new_files.append(diff.b_path)
                    elif diff.change_type == "D":  # Deleted
                        if diff.a_path:
                            deleted_files.append(diff.a_path)
                    elif diff.change_type == "R":  # Renamed
                        if diff.a_path and diff.b_path:
                            renamed_files.append((diff.a_path, diff.b_path))
                    elif diff.change_type == "M":  # Modified
                        if diff.b_path:
                            if diff.b_path not in file_stats:
                                file_stats[diff.b_path] = {
                                    "changes": 0,
                                    "insertions": 0,
                                    "deletions": 0,
                                }
                            
                            file_stats[diff.b_path]["changes"] += 1
                            
                            # Try to get line statistics
                            try:
                                if hasattr(diff, 'a_blob') and hasattr(diff, 'b_blob'):
                                    if diff.a_blob and diff.b_blob:
                                        # Simple line count difference
                                        a_lines = len(diff.a_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                                        b_lines = len(diff.b_blob.data_stream.read().decode('utf-8', errors='ignore').splitlines())
                                        
                                        if b_lines > a_lines:
                                            file_stats[diff.b_path]["insertions"] += b_lines - a_lines
                                        else:
                                            file_stats[diff.b_path]["deletions"] += a_lines - b_lines
                            except Exception:
                                pass
            
            # Calculate summary statistics
            total_insertions = sum(stats["insertions"] for stats in file_stats.values())
            total_deletions = sum(stats["deletions"] for stats in file_stats.values())
            
            return {
                "modified_files": file_stats,
                "new_files": list(set(new_files)),
                "deleted_files": list(set(deleted_files)),
                "renamed_files": renamed_files,
                "summary": {
                    "total_files": len(file_stats),
                    "total_insertions": total_insertions,
                    "total_deletions": total_deletions,
                },
            }
            
        except Exception as e:
            raise RepositoryError(f"Failed to analyze file changes: {e}")


# ==================== ISSUE MODULE ====================

class IssueError(Exception):
    """Custom exception for issue-related errors."""
    pass

class Issue:
    """Handles GitHub issue creation and management."""
    
    def __init__(self, title: str, description: str, labels: Optional[List[str]] = None,
                 assignees: Optional[List[str]] = None, milestone: Optional[str] = None) -> None:
        """Initialize the Issue with title and description."""
        if not title or not title.strip():
            raise ValueError("Issue title cannot be empty")
        
        if not description or not description.strip():
            raise ValueError("Issue description cannot be empty")
        
        self.title = title.strip()
        self.description = description.strip()
        self.labels = labels or []
        self.assignees = assignees or []
        self.milestone = milestone
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Validate title length (GitHub limit is 256 characters)
        if len(self.title) > 256:
            self.logger.warning(f"Title length ({len(self.title)}) exceeds GitHub limit (256)")
    
    @staticmethod
    def create_github_client(token: str) -> Github:
        """Create authenticated GitHub client."""
        try:
            auth = Authentication()
            return auth.create_client(token)
        except GitHubAuthError as e:
            raise GitHubAuthError(f"GitHub authentication failed: {e}")
    
    def validate_content(self) -> List[str]:
        """Validate issue content and return list of warnings."""
        warnings = []
        
        # Check title length
        if len(self.title) > 256:
            warnings.append(f"Title is too long ({len(self.title)}/256 characters)")
        
        if len(self.title) < 10:
            warnings.append("Title is very short (recommended minimum 10 characters)")
        
        # Check description length
        if len(self.description) < 20:
            warnings.append("Description is very short (recommended minimum 20 characters)")
        
        if len(self.description) > 65536:
            warnings.append(f"Description is very long ({len(self.description)}/65536 characters)")
        
        # Check for empty labels
        if not self.labels:
            warnings.append("No labels specified")
        
        return warnings
    
    def create_on_github(self, repository: str, token: str) -> Dict[str, Any]:
        """Create issue on GitHub repository."""
        try:
            github_client = self.create_github_client(token)
            repo = github_client.get_repo(repository)
            
            # Create the issue
            issue = repo.create_issue(
                title=self.title,
                body=self.description,
                labels=self.labels,
                assignees=self.assignees,
            )
            
            self.logger.info(f"Created issue #{issue.number}: {self.title}")
            
            return {
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
                "state": issue.state,
                "created_at": issue.created_at,
            }
            
        except Exception as e:
            raise IssueError(f"Failed to create GitHub issue: {e}")
    
    def format_for_display(self) -> str:
        """Format issue for console display."""
        formatted = f"Title: {self.title}\n"
        formatted += f"Description: {self.description[:100]}...\n" if len(self.description) > 100 else f"Description: {self.description}\n"
        if self.labels:
            formatted += f"Labels: {', '.join(self.labels)}\n"
        if self.assignees:
            formatted += f"Assignees: {', '.join(self.assignees)}\n"
        return formatted
    
    def __str__(self) -> str:
        """Return string representation of the issue."""
        return f"Issue: {self.title}"
    
    def __repr__(self) -> str:
        """Return detailed string representation of the issue."""
        return f"Issue(title='{self.title}', labels={self.labels}, assignees={self.assignees})"

def test_github_connection(token: str) -> Dict[str, Any]:
    """Test GitHub connection and return status information."""
    try:
        auth = Authentication()
        result = auth.validate_token(token)
        
        if result["valid"]:
            return {
                "authenticated": True,
                "user": result["user"],
                "rate_limit": result["rate_limit"],
                "error": None,
            }
        else:
            return {
                "authenticated": False,
                "user": None,
                "rate_limit": None,
                "error": result["error"],
            }
            
    except Exception as e:
        return {
            "authenticated": False,
            "user": None,
            "rate_limit": None,
            "error": str(e),
        }


# ==================== LLM MODULE ====================

class LLMError(Exception):
    """Custom exception for LLM-related errors."""
    pass

class LLMProviderError(Exception):
    """Custom exception for LLM provider-related errors."""
    pass

class LLMProvider(Enum):
    """Supported LLM providers."""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class LLMBackend(ABC):
    """Abstract base class for LLM backends."""
    
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM backend is available."""
        pass
    
    @abstractmethod
    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate response from the LLM."""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        pass

class OllamaBackend(LLMBackend):
    """Ollama LLM backend implementation."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize Ollama backend with configuration."""
        self.config = config
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 11434)
        self.model = config.get("model", "llama3.2")
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Try to create client
        try:
            self.client = ollama.Client(host=f"http://{self.host}:{self.port}")
        except Exception as e:
            self.logger.warning(f"Failed to create Ollama client: {e}")
            self.client = None
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        if not self.client:
            return False
        
        try:
            # Try to list models to test connection
            self.client.list()
            return True
        except Exception as e:
            self.logger.debug(f"Ollama not available: {e}")
            return False
    
    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate response using Ollama."""
        if not self.is_available():
            raise LLMError("Ollama backend is not available")
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": kwargs.get("temperature", 0.7),
                    "num_predict": kwargs.get("max_tokens", 2000),
                }
            )
            
            return {
                "response": response.get("response", ""),
                "model": self.model,
                "done": response.get("done", True),
            }
            
        except Exception as e:
            raise LLMError(f"Failed to generate response with Ollama: {e}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        if not self.is_available():
            return {"name": self.model, "status": "unavailable"}
        
        try:
            models = self.client.list()
            model_names = [model.get("name", "") for model in models.get("models", [])]
            
            if self.model in model_names:
                return {"name": self.model, "status": "available"}
            else:
                return {"name": self.model, "status": "not_found"}
                
        except Exception as e:
            return {"name": self.model, "status": "error", "error": str(e)}

class MockBackend(LLMBackend):
    """Mock LLM backend for testing and demonstration purposes."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize Mock backend."""
        super().__init__(config)
        self.model = config.get("model", "mock-model")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate mock response."""
        if "issue" in prompt.lower() and "json" in prompt.lower():
            return '[{"title": "Mock Issue", "description": "Mock description", "labels": ["mock"]}]'
        return "Mock response"

    def is_available(self) -> bool:
        """Mock backend is always available."""
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get mock model information."""
        return {"name": self.model, "provider": "mock", "status": "available"}

class HuggingFaceBackend(LLMBackend):
    """HuggingFace Transformers LLM backend implementation."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize HuggingFace backend."""
        super().__init__(config)
        self.model_name = config.get("model", "microsoft/DialoGPT-medium")
        self.device = config.get("device", "cpu")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using HuggingFace Transformers."""
        raise LLMProviderError("HuggingFace backend not fully implemented")

    def is_available(self) -> bool:
        """Check if HuggingFace backend is available."""
        return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get HuggingFace model information."""
        return {"name": self.model_name, "provider": "huggingface", "status": "not_implemented"}

class OpenAIBackend(LLMBackend):
    """OpenAI LLM backend implementation."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize OpenAI backend."""
        super().__init__(config)
        self.model = config.get("model", "gpt-3.5-turbo")
        self.api_key = config.get("api_key")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI."""
        raise LLMProviderError("OpenAI backend not fully implemented")

    def is_available(self) -> bool:
        """Check if OpenAI backend is available."""
        return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information."""
        return {"name": self.model, "provider": "openai", "status": "not_implemented"}

class LLM:
    """Main LLM interface that manages different backends."""
    
    def __init__(self, provider: str, config: Dict[str, Any]) -> None:
        """Initialize LLM with specified provider and configuration."""
        self.provider = provider
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Create appropriate backend
        if provider == "ollama":
            self.backend = OllamaBackend(config)
        else:
            raise LLMError(f"Unsupported LLM provider: {provider}")
    
    def is_available(self) -> bool:
        """Check if the LLM is available."""
        return self.backend.is_available()
    
    def generate(self, prompt: str, **kwargs: Any) -> Dict[str, Any]:
        """Generate response using the configured LLM."""
        return self.backend.generate(prompt, **kwargs)


# ==================== PROMPT MODULE ====================

class PromptError(Exception):
    """Custom exception for prompt-related errors."""
    pass

class PromptType(Enum):
    """Types of prompts supported by the system."""
    ISSUE_GENERATION = "issue_generation"
    CODE_ANALYSIS = "code_analysis"
    DOCUMENTATION = "documentation"
    TESTING = "testing"

class PromptTemplate:
    """Template for generating prompts with variable substitution."""
    
    def __init__(self, name: str, prompt_type: PromptType, 
                 template: str, variables: List[str]) -> None:
        """Initialize prompt template."""
        self.name = name
        self.prompt_type = prompt_type
        self.template = template
        self.variables = variables
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def render(self, provider: str, **kwargs: Any) -> str:
        """Render the template with provided variables."""
        try:
            # Ensure all required variables are provided
            missing_vars = [var for var in self.variables if var not in kwargs]
            if missing_vars:
                raise ValueError(f"Missing required variables: {missing_vars}")
            
            # Format the template
            rendered = self.template.format(**kwargs)
            
            # Add provider-specific formatting if needed
            if provider == "ollama":
                # Ollama typically works well with structured prompts
                rendered = f"System: You are a helpful assistant that generates GitHub issues.\n\n{rendered}"
            
            return rendered
            
        except Exception as e:
            raise ValueError(f"Failed to render template {self.name}: {e}")

class Prompt:
    """Manages prompt templates and generation."""
    
    def __init__(self) -> None:
        """Initialize the Prompt manager."""
        self.templates: Dict[str, PromptTemplate] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_template(self, template: PromptTemplate) -> None:
        """Add a template to the manager."""
        self.templates[template.name] = template
        self.logger.debug(f"Added template: {template.name}")
    
    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name."""
        return self.templates.get(name)
    
    def create_builtin_templates(self) -> None:
        """Create built-in templates."""
        # Basic issue generation template
        issue_template = PromptTemplate(
            name="basic_issue_generation",
            prompt_type=PromptType.ISSUE_GENERATION,
            template="""
Generate {num_issues} GitHub issues based on the following repository analysis:

Repository: {repo_path}
Commits analyzed: {commit_count}
Files modified: {modified_files_count}
New files: {new_files_count}

Recent changes:
{recent_changes}

File changes summary:
{file_changes_summary}

Please generate practical GitHub issues that would be valuable for this project.
Each issue should have:
- A clear, descriptive title
- A detailed description explaining the problem or enhancement
- Appropriate labels
- Estimated effort or complexity

Return the response as a JSON array of objects with the following structure:
[
  {{
    "title": "Issue title",
    "description": "Detailed description of the issue",
    "labels": ["label1", "label2"],
    "assignees": []
  }}
]

Focus on issues that would genuinely improve the project, such as:
- Bug fixes for common problems
- Code quality improvements
- Documentation updates
- Testing enhancements
- Performance optimizations
- Feature additions based on recent activity
""",
            variables=[
                "repo_path", "commit_count", "modified_files_count", 
                "new_files_count", "num_issues", "recent_changes", 
                "file_changes_summary"
            ]
        )
        
        self.add_template(issue_template)
        self.logger.info("Created built-in templates")


# ==================== DATA SCRAPER MODULE ====================

class DataScraperError(Exception):
    """Custom exception for data scraper-related errors."""
    pass

class DataScraper:
    """Scrapes and analyzes repository data for issue generation."""
    
    def __init__(self, repository: Repository) -> None:
        """Initialize DataScraper with a repository."""
        self.repository = repository
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def scrape_file_patterns(self, max_files: int = 100) -> Dict[str, Any]:
        """Analyze file patterns in the repository."""
        try:
            repo_path = self.repository.path
            patterns = {
                "source_files": [],
                "config_files": [],
                "documentation_files": [],
                "test_files": [],
                "other_files": [],
            }
            
            # Define file extensions for categorization
            source_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.h', '.cs', '.rb', '.go', '.rs', '.php'}
            config_extensions = {'.json', '.yaml', '.yml', '.toml', '.ini', '.cfg', '.conf'}
            doc_extensions = {'.md', '.rst', '.txt', '.adoc', '.tex'}
            test_patterns = {'test_', '_test', '.test.', 'spec_', '_spec', '.spec.'}
            
            file_count = 0
            for file_path in repo_path.rglob('*'):
                if file_count >= max_files:
                    break
                
                if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                    file_count += 1
                    relative_path = file_path.relative_to(repo_path)
                    file_info = {
                        "path": str(relative_path),
                        "size": file_path.stat().st_size,
                        "extension": file_path.suffix.lower(),
                    }
                    
                    # Categorize file
                    if any(pattern in file_path.name.lower() for pattern in test_patterns):
                        patterns["test_files"].append(file_info)
                    elif file_path.suffix.lower() in source_extensions:
                        patterns["source_files"].append(file_info)
                    elif file_path.suffix.lower() in config_extensions:
                        patterns["config_files"].append(file_info)
                    elif file_path.suffix.lower() in doc_extensions:
                        patterns["documentation_files"].append(file_info)
                    else:
                        patterns["other_files"].append(file_info)
            
            self.logger.info(f"Analyzed {file_count} files")
            return patterns
            
        except Exception as e:
            raise Exception(f"Failed to scrape file patterns: {e}")


# ==================== GITHUB UTILS MODULE ====================

class GitHubCloneError(Exception):
    """Exception for GitHub cloning errors."""
    pass

class GitHubUtils:
    """Utility class for GitHub operations."""
    
    def __init__(self) -> None:
        """Initialize GitHubUtils."""
        self.logger = logging.getLogger(self.__class__.__name__)
        self.temp_directories: List[Path] = []
    
    def parse_github_url(self, url_or_repo: str) -> str:
        """Parse GitHub URL or repository string to extract owner/repo format."""
        # Remove common prefixes and suffixes
        cleaned = url_or_repo.strip()
        
        if cleaned.startswith("https://github.com/"):
            cleaned = cleaned[19:]  # Remove "https://github.com/"
        elif cleaned.startswith("http://github.com/"):
            cleaned = cleaned[18:]  # Remove "http://github.com/"
        elif cleaned.startswith("git@github.com:"):
            cleaned = cleaned[15:]  # Remove "git@github.com:"
        
        if cleaned.endswith(".git"):
            cleaned = cleaned[:-4]  # Remove ".git"
        
        # Validate format
        parts = cleaned.split("/")
        if len(parts) != 2:
            raise ValueError(f"Invalid GitHub repository format: {url_or_repo}. Expected format: 'owner/repo'")
        
        owner, repo = parts
        if not owner or not repo:
            raise ValueError(f"Invalid GitHub repository format: {url_or_repo}. Both owner and repo must be non-empty")
        
        return f"{owner}/{repo}"
    
    def is_public_repository(self, repo: str) -> bool:
        """Check if a GitHub repository is public."""
        try:
            url = f"https://api.github.com/repos/{repo}"
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return not data.get("private", True)
            elif response.status_code == 404:
                return False  # Repository not found or private
            else:
                self.logger.warning(f"Unexpected response checking repository visibility: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.warning(f"Failed to check repository visibility: {e}")
            return False
    
    def clone_repository(self, repo: str, token: Optional[str] = None, 
                        target_dir: Optional[str] = None) -> str:
        """Clone a GitHub repository to a temporary directory."""
        try:
            import tempfile
            import shutil
            
            # Create target directory
            if target_dir:
                temp_dir = Path(target_dir)
                temp_dir.mkdir(parents=True, exist_ok=True)
            else:
                temp_dir = Path(tempfile.mkdtemp(prefix="ticket-master-"))
            
            self.temp_directories.append(temp_dir)
            
            # Construct clone URL
            if token:
                clone_url = f"https://{token}@github.com/{repo}.git"
            else:
                clone_url = f"https://github.com/{repo}.git"
            
            # Clone the repository
            repo_name = repo.split("/")[1]
            repo_path = temp_dir / repo_name
            
            self.logger.info(f"Cloning {repo} to {repo_path}")
            
            # Use git command directly for better error handling
            import subprocess
            result = subprocess.run(
                ["git", "clone", "--depth", "50", clone_url, str(repo_path)],
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode != 0:
                raise GitHubCloneError(f"Git clone failed: {result.stderr}")
            
            self.logger.info(f"Successfully cloned {repo}")
            return str(repo_path)
            
        except subprocess.TimeoutExpired:
            raise GitHubCloneError("Clone operation timed out")
        except Exception as e:
            raise GitHubCloneError(f"Failed to clone repository {repo}: {e}")
    
    def cleanup_temp_directories(self) -> None:
        """Clean up temporary directories created during cloning."""
        import shutil
        
        for temp_dir in self.temp_directories:
            try:
                if temp_dir.exists():
                    shutil.rmtree(temp_dir)
                    self.logger.debug(f"Cleaned up temporary directory: {temp_dir}")
            except Exception as e:
                self.logger.warning(f"Failed to clean up {temp_dir}: {e}")
        
        self.temp_directories.clear()


# ==================== DATABASE MODULE ====================

class DatabaseError(Exception):
    """Custom exception for database-related errors."""
    pass

class Database:
    """Base database class for Ticket-Master."""
    
    def __init__(self, db_path: str) -> None:
        """Initialize database connection."""
        self.db_path = db_path
        self.logger = logging.getLogger(self.__class__.__name__)
        self.connection = None
        self._init_database()
    
    def _init_database(self) -> None:
        """Initialize database connection and create tables."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.row_factory = sqlite3.Row
            self._create_tables()
            self.logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            raise Exception(f"Failed to initialize database: {e}")
    
    def _create_tables(self) -> None:
        """Create database tables."""
        pass  # To be implemented by subclasses
    
    def close(self) -> None:
        """Close database connection."""
        if self.connection:
            self.connection.close()
            self.connection = None

class UserDatabase(Database):
    """Database for user-related data."""
    
    def _create_tables(self) -> None:
        """Create user tables."""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT,
                github_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()

class ServerDatabase(Database):
    """Database for server configuration and state."""
    
    def _create_tables(self) -> None:
        """Create server tables."""
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS server_config (
                key TEXT PRIMARY KEY,
                value TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()


# ==================== PIPELINE MODULE ====================

class PipeError(Exception):
    """Custom exception for pipeline-related errors."""
    pass

class PipeExecutionError(PipeError):
    """Custom exception for pipeline execution errors."""
    pass

class PipeValidationError(PipeError):
    """Custom exception for pipeline validation errors."""
    pass

class PipeStage(Enum):
    """Pipeline execution stages."""
    ANALYSIS = "analysis"
    GENERATION = "generation"
    VALIDATION = "validation"
    CREATION = "creation"

class PipelineStep:
    """Represents a single step in the pipeline."""
    
    def __init__(self, name: str, stage: PipeStage, 
                 function: Any, dependencies: List[str] = None) -> None:
        """Initialize pipeline step."""
        self.name = name
        self.stage = stage
        self.function = function
        self.dependencies = dependencies or []
        self.completed = False
        self.result = None
        self.error = None

class Pipe:
    """Pipeline for orchestrating the issue generation process."""
    
    def __init__(self) -> None:
        """Initialize the pipeline."""
        self.steps: Dict[str, PipelineStep] = {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def add_step(self, step: PipelineStep) -> None:
        """Add a step to the pipeline."""
        self.steps[step.name] = step
        self.logger.debug(f"Added pipeline step: {step.name}")
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the pipeline."""
        results = {}
        
        # Execute steps in dependency order
        executed = set()
        
        def execute_step(step_name: str) -> None:
            if step_name in executed:
                return
            
            step = self.steps[step_name]
            
            # Execute dependencies first
            for dep in step.dependencies:
                if dep not in executed:
                    execute_step(dep)
            
            try:
                self.logger.info(f"Executing pipeline step: {step_name}")
                step.result = step.function(context, results)
                step.completed = True
                results[step_name] = step.result
                executed.add(step_name)
                self.logger.info(f"Completed pipeline step: {step_name}")
                
            except Exception as e:
                step.error = str(e)
                self.logger.error(f"Pipeline step {step_name} failed: {e}")
                raise
        
        # Execute all steps
        for step_name in self.steps:
            execute_step(step_name)
        
        return results


# ==================== OLLAMA TOOLS MODULE ====================

class OllamaToolsError(Exception):
    """Custom exception for Ollama tools-related errors."""
    pass

class OllamaPromptValidator:
    """Validates prompts for Ollama-specific requirements."""
    
    def __init__(self) -> None:
        """Initialize the validator."""
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_prompt(self, prompt: str) -> Dict[str, Any]:
        """Validate a prompt for Ollama."""
        issues = []
        warnings = []
        
        # Check prompt length
        if len(prompt) > 32000:
            issues.append("Prompt is too long for Ollama (>32k characters)")
        elif len(prompt) > 16000:
            warnings.append("Prompt is quite long, may impact performance")
        
        # Check for proper structure
        if not prompt.strip():
            issues.append("Prompt is empty")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
        }

class OllamaPromptProcessor:
    """Processes prompts and generates responses using Ollama."""
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the processor."""
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
        self.validator = OllamaPromptValidator()
        
        # Initialize Ollama client
        try:
            host = config.get("host", "localhost")
            port = config.get("port", 11434)
            self.client = ollama.Client(host=f"http://{host}:{port}")
            self.model = config.get("model", "llama3.2")
        except Exception as e:
            self.logger.error(f"Failed to initialize Ollama client: {e}")
            self.client = None
    
    def generate_issues_from_analysis(self, analysis: Dict[str, Any], 
                                    max_issues: int = 5) -> List[Dict[str, Any]]:
        """Generate issues from repository analysis using Ollama."""
        if not self.client:
            raise Exception("Ollama client not available")
        
        try:
            # Create prompt from analysis
            prompt = self._create_issue_prompt(analysis, max_issues)
            
            # Validate prompt
            validation = self.validator.validate_prompt(prompt)
            if not validation["valid"]:
                raise Exception(f"Invalid prompt: {validation['issues']}")
            
            # Generate response
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                stream=False,
                options={
                    "temperature": self.config.get("temperature", 0.7),
                    "num_predict": 2000,
                }
            )
            
            # Parse response
            issues = self._parse_issues_response(response.get("response", ""))
            
            self.logger.info(f"Generated {len(issues)} issues using Ollama")
            return issues
            
        except Exception as e:
            raise Exception(f"Failed to generate issues with Ollama: {e}")
    
    def _create_issue_prompt(self, analysis: Dict[str, Any], max_issues: int) -> str:
        """Create a prompt for issue generation."""
        repo_info = analysis.get("repository_info", {})
        summary = analysis.get("analysis_summary", {})
        commits = analysis.get("commits", [])
        
        prompt = f"""
You are a helpful assistant that generates practical GitHub issues based on repository analysis.

Repository: {repo_info.get('name', 'Unknown')}
Commits analyzed: {summary.get('commit_count', 0)}
Files modified: {summary.get('files_modified', 0)}
Files added: {summary.get('files_added', 0)}
Total changes: +{summary.get('total_insertions', 0)}/-{summary.get('total_deletions', 0)} lines

Recent commit messages:
"""
        
        for commit in commits[:5]:
            prompt += f"- {commit.get('short_hash', '')}: {commit.get('summary', '')}\n"
        
        prompt += f"""
Generate {max_issues} practical GitHub issues that would improve this project.

Return ONLY a JSON array with this exact structure:
[
  {{
    "title": "Clear, actionable issue title",
    "description": "Detailed description explaining the issue and proposed solution",
    "labels": ["enhancement", "automated"]
  }}
]

Focus on realistic improvements like code quality, documentation, testing, or bug fixes.
"""
        
        return prompt
    
    def _parse_issues_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the Ollama response to extract issues."""
        try:
            # Clean the response
            cleaned = response.strip()
            
            # Remove markdown formatting if present
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            
            cleaned = cleaned.strip()
            
            # Parse JSON
            issues = json.loads(cleaned)
            
            # Ensure it's a list
            if not isinstance(issues, list):
                issues = [issues] if issues else []
            
            # Validate and clean each issue
            valid_issues = []
            for issue in issues:
                if isinstance(issue, dict) and "title" in issue and "description" in issue:
                    valid_issues.append({
                        "title": str(issue["title"]).strip(),
                        "description": str(issue["description"]).strip(),
                        "labels": issue.get("labels", ["automated"]),
                        "assignees": issue.get("assignees", []),
                    })
            
            return valid_issues
            
        except Exception as e:
            self.logger.error(f"Failed to parse Ollama response: {e}")
            return []

def create_ollama_processor(config: Dict[str, Any]) -> OllamaPromptProcessor:
    """Create and return an Ollama prompt processor."""
    return OllamaPromptProcessor(config)


# Export list for the consolidated module
__all__ = [
    "Repository", "Issue", "Authentication", "AuthenticationError", "GitHubAuthError",
    "Commit", "Branch", "PullRequest", "Database", "UserDatabase", "ServerDatabase",
    "LLM", "LLMProvider", "LLMBackend", "OllamaPromptProcessor", "OllamaPromptValidator",
    "create_ollama_processor", "Prompt", "PromptTemplate", "PromptType", "Pipe",
    "PipelineStep", "PipeStage", "DataScraper", "GitHubUtils", "GitHubCloneError",
    "__version__", "__author__", "__description__", "test_github_connection",
    # Color functions
    "colorize", "success", "error", "warning", "info", "header", "highlight", "dim", 
    "progress_bar", "print_colored", "supports_color", "enable_colors", "is_color_enabled",
    # Color constants  
    "RED", "GREEN", "YELLOW", "BLUE", "MAGENTA", "CYAN", "WHITE", "GRAY", "BOLD", 
    "DIM", "ITALIC", "UNDERLINE", "RESET", "END", "Colors", "RepositoryError", "IssueError", "LLMError"
]