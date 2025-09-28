"""
Ticket-Master: AI-powered GitHub issue generator

A tool that uses AI to suggest GitHub issues with descriptions
based on the contents of a Git repository.
"""

__version__ = "0.1.0"
__author__ = "Ticket-Master Contributors"
__description__ = "AI-powered GitHub issue generator"

from .auth import Authentication, AuthenticationError, GitHubAuthError
from .branch import Branch
from .commit import Commit
from .data_scraper import DataScraper
from .database import Database, ServerDatabase, UserDatabase
from .issue import Issue
from .llm import LLM, LLMBackend, LLMProvider
from .ollama_tools import OllamaPromptProcessor, OllamaPromptValidator, create_ollama_processor
from .pipe import Pipe, PipelineStep, PipeStage
from .prompt import Prompt, PromptTemplate, PromptType
from .pull_request import PullRequest
from .repository import Repository

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
