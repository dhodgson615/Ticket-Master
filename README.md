# Ticket-Master

[![CI Pipeline](https://github.com/dhodgson615/Ticket-Master/actions/workflows/ci.yml/badge.svg)](https://github.com/dhodgson615/Ticket-Master/actions/workflows/ci.yml)
[![CodeQL](https://github.com/dhodgson615/Ticket-Master/actions/workflows/codeql.yml/badge.svg)](https://github.com/dhodgson615/Ticket-Master/actions/workflows/codeql.yml)
[![Dependency Updates](https://github.com/dhodgson615/Ticket-Master/actions/workflows/dependency-updates.yml/badge.svg)](https://github.com/dhodgson615/Ticket-Master/actions/workflows/dependency-updates.yml)

A project that attempts to use AI to suggest GitHub issues with descriptions
based on the contents of a Git repository

## Installation

### Quick Setup (Recommended)

1. Clone the repository:
```bash
git clone https://github.com/dhodgson615/Ticket-Master.git
cd Ticket-Master
```

2. One-command setup (installs dependencies and creates config):
```bash
make setup
```

3. Set up your GitHub token:
```bash
export GITHUB_TOKEN="your_github_personal_access_token"
```

### Manual Installation

1. Clone the repository:
```bash
git clone https://github.com/dhodgson615/Ticket-Master.git
cd Ticket-Master
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy configuration file:
```bash
cp config.yaml.example config.yaml
```

4. Set up your GitHub token:
```bash
export GITHUB_TOKEN="your_github_personal_access_token"
```

### Available Make Targets

Run `make help` to see all available targets:

- `make setup` - One-command setup: install dependencies and copy config
- `make install` - Install Python dependencies only
- `make test` - Run tests with coverage
- `make lint` - Run linting checks
- `make typecheck` - Run type checking with mypy
- `make format` - Format code with black
- `make clean` - Clean build artifacts and cache files
- `make venv` - Create virtual environment
- `make help` - Show all available targets

## Usage

### Basic Usage
```bash
python main.py /path/to/your/repo owner/repo-name
```

### Dry Run (recommended first)
Test what issues would be created without actually creating them:
```bash
python main.py /path/to/your/repo owner/repo-name --dry-run
```

### Advanced Usage
```bash
# Use custom configuration
python main.py /path/to/repo owner/repo --config config.yaml

# Limit number of issues
python main.py /path/to/repo owner/repo --max-issues 3

# Enable debug logging
python main.py /path/to/repo owner/repo --log-level DEBUG

# Combine options
python main.py /path/to/repo owner/repo --dry-run --max-issues 2 --log-level INFO
```

### Configuration

Copy the example configuration file and customize it:
```bash
cp config.yaml.example config.yaml
# Edit config.yaml with your preferred settings
```

The configuration file allows you to set:
- Default labels for generated issues
- Repository analysis parameters
- Issue generation limits
- LLM settings (for future implementation)

## Features

### Current Implementation ✅
- **Repository Analysis**: Analyzes Git history, file changes, and repository metadata
- **Issue Generation**: Creates GitHub issues based on repository analysis patterns
- **GitHub Integration**: Full GitHub API integration with authentication and error handling
- **CLI Interface**: Comprehensive command-line interface with help and validation
- **Configuration**: YAML-based configuration with environment variable support
- **Testing**: Comprehensive test suite with 43+ passing tests
- **Code Quality**: PEP 8 compliant with comprehensive documentation

### Generated Issue Types
The current implementation can generate issues for:
- **Documentation Updates**: Based on recent code changes
- **Code Reviews**: For frequently modified files
- **Testing Improvements**: For newly added functionality

## Development

### CI/CD Pipeline

This project includes comprehensive GitHub Actions workflows for:

- **CI Pipeline** (`ci.yml`): Runs on all pushes and pull requests
  - Multi-version Python testing (3.9, 3.10, 3.11, 3.12)
  - Code formatting checks with Black
  - Linting with flake8
  - Type checking with mypy
  - Test suite with coverage reporting
  - Integration testing with example commands

- **Security Analysis** (`codeql.yml`): Automated security scanning
  - CodeQL analysis for security vulnerabilities
  - Runs weekly and on main branch changes

- **Dependency Updates** (`dependency-updates.yml`): Automated dependency management
  - Weekly checks for outdated packages
  - Automatic issue creation for available updates
  - Dependency review for pull requests

- **Release Management** (`release.yml`): Automated releases
  - Triggered on version tags (v*)
  - Full CI validation before release
  - Automatic changelog generation
  - GitHub release creation with assets

### Running Tests Locally
```bash
# Run all tests with coverage
make test

# Run tests without coverage
make test-fast

# Run full CI pipeline locally
make ci
```

### Code Quality
```bash
# Format code
make format

# Check formatting
make format-check

# Run linting
make lint

# Run type checking
make typecheck
```

## Architecture

- `src/ticket_master/repository.py`: Git repository analysis and operations
- `src/ticket_master/issue.py`: GitHub issue creation and management
- `main.py`: CLI interface and orchestration
- `tests/`: Comprehensive test suite
- `COPILOT_INSTRUCTIONS.md`: Detailed development guidelines

## Todo

- [x] Make standard Python structure
  - [x] Make it so that every import statement uses a try-except block to
        import packages, and if the package is not found, it installs it using
        pip
  - [x] Make a Repository class that takes in a path to a Git repository and
        has methods to get the commit history, file changes, etc.
  - [x] Make an Issue class that takes in a title and description and has
        methods to create the issue on GitHub using the GitHub API
  - [x] Make a main.py file that uses argparse to take in command line
        arguments for the path to the Git repository and the number of issues
        to create
  - [ ] Make a function that uses Ollama's API to generate issue titles and
        descriptions based on the commit history and file changes
  - [ ] Make a function that uses the GitHub API to create the issues on GitHub
  - [x] Make a requirements.txt file that lists all the required packages
  - [x] Make a .gitignore file that ignores all unnecessary files
  - [ ] Implement LLM selection (Ollama, OpenAI, etc.)
  - [ ] Implement automatic installation of LLMs from Ollama
  - [x] Ensure code follows PEP 8 guidelines
  - [x] Ensure code is well-documented with comments and docstrings

- [ ] Add tests
  - [x] Test Repository class
  - [x] Test Issue class
  - [x] Test main.py
  - [ ] Test issue generation function
  - [ ] Test GitHub issue creation function
  - [ ] Test LLM selection
  - [ ] Test automatic installation of LLMs from Ollama
  - [x] Test command line arguments
  - [x] Test error handling
  - [ ] Test edge cases
  - [ ] Test LLM installation
  - [ ] Test GitHub API integration
  - [ ] Test Ollama API integration
  - [ ] Test performance
  - [ ] Test security
  - [ ] Ensure 100% code coverage

- [ ] Add CI
  - [x] Add GitHub Actions for running tests on every push
  - [x] Ensure linting and formatting checks are included in CI
  - [x] Add multi-version Python testing (3.9-3.12)
  - [x] Add security scanning with CodeQL
  - [x] Add dependency update automation
  - [x] Add release automation with GitHub releases
  - [x] Update README with CI status badges
  - [ ] Update README with test coverage badge
  - [x] Add Dependabot for dependency updates (via dependency-updates workflow)
  - [x] Add code quality checks (via CodeQL and security scanning)

- [ ] Add documentation
  - [x] Add docstrings to all classes and functions
  - [ ] Add usage examples to the README

- [ ] Add more LLMs
  - [ ] Add support for OpenAI's GPT-4
  - [ ] Add support for other popular LLMs (e.g., Cohere, AI21, etc.)
  - [ ] Add a configuration file to specify which LLM to use
  - [ ] Add a command line argument to specify which LLM to use
  - [ ] Add a function to list available LLMs
  - [ ] Add a function to check if the specified LLM is installed
  - [ ] Add a function to install the specified LLM if it is not installed

- [ ] Add fallback mechanism
  - [ ] If the specified LLM is not installed, fall back to a default LLM
  - [ ] If the default LLM is not installed, prompt the user to install it
  - [ ] If no LLMs are installed, exit with an error message

- [ ] Add configuration file
  - [x] Add a config.yaml file to specify default settings (e.g., default LLM,
        default number of issues to create, etc.)
  - [x] Add a function to read the configuration file
  - [ ] Add a function to write to the configuration file
  - [x] Add a command line argument to specify a different configuration file
  - [x] Add a function to validate the configuration file

- [ ] Add self correction mechanism
  - [ ] After generating an issue, use the LLM to review and improve the issue
        description
  - [ ] Implement a feedback loop where the user can provide feedback on the
        generated issues, and use that feedback to improve future issue
        generation
  - [ ] Use the LLM to analyze the commit history and file changes to identify
        patterns and trends that can inform issue generation
  - [ ] Implement a scoring system to rate the quality of generated issues, and
        use that score to improve future issue generation
  - [ ] Ensure that when LLMs give incorrect or nonsensical outputs, the system
        can identify and correct those errors using the LLM itself or other
        heuristics

- [ ] Add prompt pipelines
  - [ ] Create a series of prompts that guide the LLM through the issue
        generation process
  - [ ] Implement a mechanism to chain multiple prompts together to create more
        complex issue descriptions
  - [ ] Allow users to customize the prompt pipeline to suit their specific
        needs
  - [ ] Add a function to visualize the prompt pipeline and the flow of data
        through it
  - [ ] Ensure that the prompt pipeline is modular and can be easily extended
        with new prompts or modified as needed

- [ ] Add user interface
  - [ ] Create a simple web interface using Flask or Django to allow users to
        interact with the tool
  - [ ] Allow users to select the Git repository, LLM, and other settings
        through the web interface
  - [ ] Display the generated issues in a user-friendly format
  - [ ] Allow users to provide feedback on the generated issues through the web
        interface
  - [ ] Implement authentication and authorization to restrict access to the
        tool as needed
  - [ ] Ensure that the web interface is responsive and works well on different
        devices and screen sizes

- [ ] Add database integration
  - [ ] Use a database (e.g., SQLite, PostgreSQL, etc.) to store generated
        issues and their metadata
  - [ ] Allow users to view and manage previously generated issues through the
        user interface
  - [ ] Implement a search functionality to find specific issues based on
        keywords or other criteria
  - [ ] Ensure that the database is properly indexed for performance
  - [ ] Implement backup and restore functionality for the database
  - [ ] Ensure that the database is secure and access is restricted as needed

- [ ] Add user database
  - [ ] Allow users to create accounts and save their settings and preferences
  - [ ] Implement user profiles to store information about each user
  - [ ] Allow users to view their history of generated issues and manage them
  - [ ] Implement a rating system for users to rate the quality of generated
        issues
  - [ ] Ensure that user data is stored securely and access is restricted as
        needed

- [ ] Add analytics
  - [ ] Track usage statistics (e.g., number of issues generated, most popular
        LLMs, etc.)
  - [ ] Implement a dashboard to display analytics data in a user-friendly
        format
  - [ ] Allow users to export analytics data for further analysis
  - [ ] Use analytics data to identify areas for improvement and inform future
        development
  - [ ] Ensure that analytics data is collected and stored securely and access
        is restricted as needed

- [ ] Add notifications
  - [ ] Implement email notifications to inform users when new issues are
        generated
  - [ ] Allow users to customize their notification settings (e.g., frequency,
        types of notifications, etc.)
  - [ ] Implement push notifications for mobile devices
  - [ ] Ensure that notifications are sent securely and access is restricted as
        needed

- [ ] Add error handling
  - [ ] Implement robust error handling throughout the codebase
  - [ ] Ensure that meaningful error messages are displayed to the user
  - [ ] Log errors for further analysis and debugging
  - [ ] Implement a mechanism to report errors to the development team
  - [ ] Ensure that the tool can recover gracefully from errors and continue
        functioning as much as possible

- [ ] Add as much support for private repositories as possible
  - [ ] Implement OAuth authentication to allow users to access private
        repositories
  - [ ] Ensure that the tool can handle different types of authentication
        (e.g., personal access tokens, SSH keys, etc.)
  - [ ] Implement a mechanism to securely store and manage authentication
        credentials
  - [ ] Ensure that the tool respects repository permissions and only accesses
        data that the user has permission to access
  - [ ] Test the tool with a variety of private repositories to ensure
        compatibility

- [ ] Add support for user-defined issue templates
  - [ ] Allow users to create and manage their own issue templates
  - [ ] Implement a mechanism to select and use different issue templates based
        on the context (e.g., type of repository, type of issue, etc.)
  - [ ] Ensure that the tool can handle different formats for issue templates
        (e.g., Markdown, plain text, etc.)
  - [ ] Allow users to customize the generated issues based on their selected
        template
  - [ ] Test the tool with a variety of user-defined issue templates to ensure
        compatibility

- [ ] Add support for user-defined rules and heuristics
  - [ ] Allow users to define their own rules and heuristics for issue
        generation
  - [ ] Implement a mechanism to apply user-defined rules and heuristics during
        the issue generation process
  - [ ] Ensure that the tool can handle different types of rules and heuristics
        (e.g., keyword-based, pattern-based, etc.)
  - [ ] Allow users to customize the generated issues based on their defined
        rules and heuristics
  - [ ] Test the tool with a variety of user-defined rules and heuristics to
        ensure compatibility

- [ ] Add support for user-defined workflows
  - [ ] Allow users to define their own workflows for issue generation and
        management
  - [ ] Implement a mechanism to execute user-defined workflows during the
        issue generation process
  - [ ] Ensure that the tool can handle different types of workflows (e.g.,
        sequential, parallel, conditional, etc.)
  - [ ] Allow users to customize the generated issues based on their defined
        workflows
  - [ ] Test the tool with a variety of user-defined workflows to ensure
        compatibility

- [ ] Add support for user-hosted LLMs
  - [ ] Allow users to configure and use their own hosted LLMs for issue
        generation
  - [ ] Implement a mechanism to connect to and authenticate with user-hosted
        LLMs
  - [ ] Ensure that the tool can handle different types of user-hosted LLMs
        (e.g., different APIs, authentication methods, etc.)
  - [ ] Allow users to customize the generated issues based on their selected
        user-hosted LLM
  - [ ] Test the tool with a variety of user-hosted LLMs to ensure
        compatibility

- [ ] Determine software stack
  - [ ] Choose a web framework (e.g., Flask, Django, etc.)
  - [ ] Choose a database (e.g., SQLite, PostgreSQL, etc.)
  - [ ] Choose an ORM (e.g., SQLAlchemy, Django ORM, etc.)
  - [ ] Choose a front-end framework (e.g., React, Vue, etc.)
  - [ ] Choose a testing framework (e.g., pytest, unittest, etc.)
  - [ ] Choose a CI/CD platform (e.g., GitHub Actions, Travis CI, etc.)
  - [ ] Choose a code quality tool (e.g., CodeClimate, SonarQube, etc.)
  - [ ] Choose a deployment platform (e.g., Heroku, AWS, etc.)

- [ ] Create project roadmap
  - [ ] Define project milestones and deadlines
  - [ ] Prioritize features and tasks
  - [ ] Allocate resources and assign tasks to team members
  - [ ] Monitor progress and adjust the roadmap as needed
  - [ ] Communicate the roadmap to all stakeholders

- [ ] Determine software architecture
  - [ ] Define the overall structure and organization of the codebase
  - [ ] Identify key components and their interactions
  - [ ] Choose design patterns and best practices to follow
  - [ ] Ensure scalability, maintainability, and extensibility of the
        architecture
  - [ ] Document the architecture for future reference

- [ ] Set up development environment
  - [ ] Create a virtual environment for the project
  - [ ] Install all required packages and dependencies
  - [ ] Set up version control using Git
  - [ ] Configure code formatting and linting tools
  - [ ] Set up pre-commit hooks to enforce code quality standards

- [ ] Perform initial research
  - [ ] Research available LLMs and their capabilities
  - [ ] Research GitHub API and its capabilities
  - [ ] Research best practices for issue generation and management
  - [ ] Research existing tools and solutions in the market
  - [ ] Identify potential challenges and risks

