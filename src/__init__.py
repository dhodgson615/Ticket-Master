import subprocess
import sys

__version__ = "0.1.0"
__author__ = "Ticket-Master Contributors"
__description__ = "AI-powered GitHub issue generator"

# Import with fallback installation pattern
# TODO: Consider using a more robust dependency management approach
# such as poetry or pipenv for better handling of dependencies.
try:
    from auth import Authentication as Authentication
    from auth import AuthenticationError as AuthenticationError
    from auth import GitHubAuthError as GitHubAuthError

except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    from auth import Authentication as Authentication
    from auth import AuthenticationError as AuthenticationError
    from auth import GitHubAuthError as GitHubAuthError

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
    from database import Database as Database
    from database import ServerDatabase as ServerDatabase
    from database import UserDatabase as UserDatabase

except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "sqlite3"])
    from database import Database as Database
    from database import ServerDatabase as ServerDatabase
    from database import UserDatabase as UserDatabase

try:
    from issue import Issue as Issue

except ImportError:
    from issue import Issue as Issue

try:
    from llm import LLM as LLM
    from llm import LLMBackend as LLMBackend
    from llm import LLMProvider as LLMProvider

except ImportError:
    from llm import LLM as LLM
    from llm import LLMBackend as LLMBackend
    from llm import LLMProvider as LLMProvider

try:
    from ollama_tools import OllamaPromptProcessor as OllamaPromptProcessor
    from ollama_tools import OllamaPromptValidator as OllamaPromptValidator
    from ollama_tools import create_ollama_processor as create_ollama_processor

except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama"])
    from ollama_tools import OllamaPromptProcessor as OllamaPromptProcessor
    from ollama_tools import OllamaPromptValidator as OllamaPromptValidator
    from ollama_tools import create_ollama_processor as create_ollama_processor

try:
    from pipe import Pipe as Pipe
    from pipe import PipelineStep as PipelineStep
    from pipe import PipeStage as PipeStage

except ImportError:
    from pipe import Pipe as Pipe
    from pipe import PipelineStep as PipelineStep
    from pipe import PipeStage as PipeStage

try:
    from prompt import Prompt as Prompt
    from prompt import PromptTemplate as PromptTemplate
    from prompt import PromptType as PromptType

except ImportError:
    from prompt import Prompt as Prompt
    from prompt import PromptTemplate as PromptTemplate
    from prompt import PromptType as PromptType

try:
    from pull_request import PullRequest as PullRequest

except ImportError:
    from pull_request import PullRequest as PullRequest

try:
    from repository import Repository as Repository

except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "gitpython"]
    )

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