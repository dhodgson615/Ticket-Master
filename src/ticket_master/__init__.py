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

__all__ = ["Repository", "Issue", "__version__"]
