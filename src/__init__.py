import subprocess
import sys

__version__ = "0.1.0"
__author__ = "Ticket-Master Contributors"
__description__ = "AI-powered GitHub issue generator"

# External package imports with fallback installation
try:
    import requests

except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

try:
    import sqlite3

except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlite3"])
    import sqlite3

try:
    import ollama

except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    import ollama

try:
    import git

except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "gitpython"]
    )
    import git

# Internal module imports
from auth import Authentication, AuthenticationError, GitHubAuthError
from branch import Branch
from commit import Commit
from data_scraper import DataScraper
from database import Database, ServerDatabase, UserDatabase
from issue import Issue
from llm import LLM, LLMBackend, LLMProvider
from ollama_tools import (OllamaPromptProcessor, OllamaPromptValidator,
                          create_ollama_processor)
from pipe import Pipe, PipelineStep, PipeStage
from prompt import Prompt, PromptTemplate, PromptType
from pull_request import PullRequest
from repository import Repository

__all__ = [
    "Repository",
    "Issue",
    "Authentication",
    "AuthenticationError",
    "GitHubAuthError",
    "Commit",
    "Branch",
    "PullRequest",
    "Database",
    "UserDatabase",
    "ServerDatabase",
    "LLM",
    "LLMProvider",
    "LLMBackend",
    "OllamaPromptProcessor",
    "OllamaPromptValidator",
    "create_ollama_processor",
    "Prompt",
    "PromptTemplate",
    "PromptType",
    "Pipe",
    "PipelineStep",
    "PipeStage",
    "DataScraper",
    "__version__",
]


# Note: The above import-with-fallback-installation pattern is not ideal for
# production code. It's recommended to manage dependencies using a requirements
# file or a dependency management tool like Poetry or Pipenv.

# TODO: refactor to use a proper dependency management tool

# TODO: refactor code into src/, models/, services/, utils/ etc. for better organization
# and maintainability.
# This will help in scaling the codebase as more features are added.
# For example, move GitHub-related code to services/github.py,
# LLM-related code to services/llm.py, etc.
# Also consider adding __init__.py files to make them proper packages.
# This will also help in writing targeted unit tests for each module.

# TODO: refactor so that mypy and pylint checks can be run without errors
# This will help in maintaining code quality and catching potential issues early.
