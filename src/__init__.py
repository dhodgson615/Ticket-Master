"""
Ticket-Master: AI-powered GitHub issue generator

A tool that uses AI to suggest GitHub issues with descriptions
based on the contents of a Git repository.
"""

import subprocess
import sys

__version__ = "0.1.0"
__author__ = "Ticket-Master Contributors"
__description__ = "AI-powered GitHub issue generator"

# Import with fallback installation pattern
try:
    from auth import Authentication as Authentication, AuthenticationError as AuthenticationError, GitHubAuthError as GitHubAuthError
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    from auth import Authentication as Authentication, AuthenticationError as AuthenticationError, GitHubAuthError as GitHubAuthError

try:
    from branch import Branch as Branch
except ImportError:
    from branch import Branch as Branch

try:
    from commit import Commit as Commit
except ImportError:
    from commit import Commit as Commit

try:
    from data_scraper import DataScraper as DataScraper
except ImportError:
    from data_scraper import DataScraper as DataScraper

try:
    from database import Database as Database, ServerDatabase as ServerDatabase, UserDatabase as UserDatabase
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlite3"])
    from database import Database as Database, ServerDatabase as ServerDatabase, UserDatabase as UserDatabase

try:
    from issue import Issue as Issue
except ImportError:
    from issue import Issue as Issue

try:
    from llm import LLM as LLM, LLMBackend as LLMBackend, LLMProvider as LLMProvider
except ImportError:
    from llm import LLM as LLM, LLMBackend as LLMBackend, LLMProvider as LLMProvider

try:
    from ollama_tools import OllamaPromptProcessor as OllamaPromptProcessor, OllamaPromptValidator as OllamaPromptValidator, create_ollama_processor as create_ollama_processor
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    from ollama_tools import OllamaPromptProcessor as OllamaPromptProcessor, OllamaPromptValidator as OllamaPromptValidator, create_ollama_processor as create_ollama_processor

try:
    from pipe import Pipe as Pipe, PipelineStep as PipelineStep, PipeStage as PipeStage
except ImportError:
    from pipe import Pipe as Pipe, PipelineStep as PipelineStep, PipeStage as PipeStage

try:
    from prompt import Prompt as Prompt, PromptTemplate as PromptTemplate, PromptType as PromptType
except ImportError:
    from prompt import Prompt as Prompt, PromptTemplate as PromptTemplate, PromptType as PromptType

try:
    from pull_request import PullRequest as PullRequest
except ImportError:
    from pull_request import PullRequest as PullRequest

try:
    from repository import Repository as Repository
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "gitpython"])
    from repository import Repository as Repository

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
