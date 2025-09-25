"""
Ticket-Master: AI-powered GitHub issue generator

A tool that uses AI to suggest GitHub issues with descriptions
based on the contents of a Git repository.
"""

__version__ = "0.1.0"
__author__ = "Ticket-Master Contributors"
__description__ = "AI-powered GitHub issue generator"

from .repository import Repository
from .issue import Issue
from .commit import Commit
from .branch import Branch
from .pull_request import PullRequest
from .database import Database, UserDatabase, ServerDatabase
from .llm import LLM, LLMProvider, LLMBackend
from .prompt import Prompt, PromptTemplate, PromptType
from .pipe import Pipe, PipelineStep, PipeStage
from .data_scraper import DataScraper

__all__ = [
    "Repository",
    "Issue",
    "Commit",
    "Branch",
    "PullRequest",
    "Database",
    "UserDatabase",
    "ServerDatabase",
    "LLM",
    "LLMProvider",
    "LLMBackend",
    "Prompt",
    "PromptTemplate",
    "PromptType",
    "Pipe",
    "PipelineStep",
    "PipeStage",
    "DataScraper",
    "__version__",
]
