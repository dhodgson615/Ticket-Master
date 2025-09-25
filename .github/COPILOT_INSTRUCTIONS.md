# Copilot Instructions for Ticket-Master

## Project Overview
Ticket-Master is an AI-powered tool that generates GitHub issues with descriptions based on Git repository contents. The project uses Large Language Models (LLMs) to analyze commit history and file changes to suggest relevant issues.

## Development Guidelines

### Code Quality Standards
- **ALWAYS** follow PEP 8 guidelines for Python code formatting
- **ALWAYS** include comprehensive docstrings for all classes, methods, and functions using Google-style docstrings
- **ALWAYS** use type hints for function parameters and return values
- **ALWAYS** implement proper error handling with specific exception types
- **NEVER** leave TODO comments in production code - convert them to GitHub issues instead
- **NEVER** commit hardcoded credentials or API keys

### Import Management
- **ALWAYS** use try-except blocks for package imports with automatic installation fallback:
```python
try:
    import requests
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests
```

### Architecture Principles
- **ALWAYS** make incremental changes - never break existing functionality
- **ALWAYS** implement modular design with clear separation of concerns
- **ALWAYS** create classes and functions that are easily testable
- **ALWAYS** implement proper logging using Python's logging module
- **NEVER** create tightly coupled components
- **NEVER** implement functionality without corresponding tests

### Testing Requirements
- **ALWAYS** write tests for new functionality before implementation (TDD approach)
- **ALWAYS** achieve minimum 80% code coverage for new code
- **ALWAYS** test error conditions and edge cases
- **ALWAYS** use pytest for test framework
- **ALWAYS** mock external API calls in tests
- **CRITICAL RULE**: Every Python file MUST have a corresponding test file (e.g., `file.py` requires `test_file.py`)
- **NEVER** skip testing for "simple" functions

### Git and Version Control
- **ALWAYS** commit small, focused changes with descriptive commit messages
- **ALWAYS** update the README todo list when completing items
- **ALWAYS** mark completed todo items with [x] and add implementation details
- **CRITICAL REMINDER**: Every time you complete a todo item, you MUST update the README.md todo list and mark it as completed with [x] - this is essential for project tracking
- **NEVER** commit compiled files, cache directories, or temporary files
- **NEVER** force push to shared branches

### Documentation Standards
- **ALWAYS** update documentation when changing functionality
- **ALWAYS** include usage examples in docstrings
- **ALWAYS** document configuration options and environment variables
- **ALWAYS** maintain up-to-date README with installation and usage instructions
- **NEVER** assume functionality is self-explanatory

### Specific Implementation Guidelines

#### Repository Class
- **MUST** handle Git operations safely with proper exception handling
- **MUST** support both local and remote repository paths
- **MUST** implement caching for expensive Git operations
- **MUST** respect .gitignore patterns when analyzing files

#### Issue Class
- **MUST** implement GitHub API authentication securely
- **MUST** handle API rate limiting gracefully
- **MUST** validate issue content before creation
- **MUST** support issue templates and labels

#### LLM Integration
- **MUST** implement abstract base class for LLM providers
- **MUST** support multiple LLM backends (Ollama, OpenAI, etc.)
- **MUST** implement prompt templates that are easily customizable
- **MUST** handle LLM API failures gracefully with fallback mechanisms
- **MUST** implement response validation and sanitization

#### Configuration Management
- **MUST** use YAML for configuration files
- **MUST** implement configuration validation with clear error messages
- **MUST** support environment variable overrides
- **MUST** provide sensible defaults for all configuration options

#### CLI Interface
- **MUST** use argparse for command-line argument parsing
- **MUST** implement comprehensive help text
- **MUST** validate user inputs before processing
- **MUST** provide progress indicators for long-running operations

### Performance Considerations
- **ALWAYS** implement caching for expensive operations
- **ALWAYS** use connection pooling for API calls
- **ALWAYS** implement pagination for large datasets
- **NEVER** load entire repository history into memory at once

### Security Requirements
- **ALWAYS** validate and sanitize all inputs
- **ALWAYS** use secure methods for credential storage
- **ALWAYS** implement proper authentication and authorization
- **NEVER** log sensitive information
- **NEVER** expose internal paths or system information

### Error Handling Patterns
- **ALWAYS** use specific exception types rather than generic Exception
- **ALWAYS** provide helpful error messages to users
- **ALWAYS** log errors with appropriate severity levels
- **ALWAYS** implement graceful degradation when possible

### Incremental Development Strategy
1. **Phase 1**: Core infrastructure (Repository, Issue classes)
2. **Phase 2**: LLM integration foundation
3. **Phase 3**: CLI interface and configuration
4. **Phase 4**: Advanced features (templates, pipelines)
5. **Phase 5**: UI and database integration

### Todo Item Management
- **ALWAYS** break down large todo items into smaller, actionable tasks
- **ALWAYS** mark completed items as [x] and add completion notes
- **ALWAYS** create new todo items for discovered requirements
- **NEVER** delete todo items - mark them as completed or outdated
- **NEVER** make todo items more vague - always be specific and actionable

### Example Code Structure
```python
class ExampleClass:
    """Example class demonstrating proper structure.
    
    This class shows the expected code quality and documentation
    standards for the Ticket-Master project.
    
    Attributes:
        config: Configuration object for the class
        logger: Logger instance for this class
    """
    
    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the example class.
        
        Args:
            config: Configuration dictionary with required settings
            
        Raises:
            ValueError: If required configuration is missing
        """
        self.config = self._validate_config(config)
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def _validate_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Validate configuration parameters."""
        # Implementation with proper validation
        pass
```

## Continuous Integration
- **ALWAYS** run tests before committing
- **ALWAYS** ensure linting passes (flake8, black)
- **ALWAYS** check for security vulnerabilities
- **NEVER** commit code that breaks CI pipeline