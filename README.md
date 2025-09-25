# Ticket-Master

A project that attempts to use AI to suggest GitHub issues with descriptions
based on the contents of a Git repository

## Todo

- Make standard Python structure
  - Make it so that every import statement uses a try-except block to import
    packages, and if the package is not found, it installs it using pip
  - Make a Repository class that takes in a path to a Git repository and
    has methods to get the commit history, file changes, etc.
  - Make an Issue class that takes in a title and description and has methods
    to create the issue on GitHub using the GitHub API
  - Make a main.py file that uses argparse to take in command line arguments
    for the path to the Git repository and the number of issues to create
  - Make a function that uses Ollama's API to generate issue titles and
    descriptions based on the commit history and file changes
  - Make a function that uses the GitHub API to create the issues on GitHub
  - Make a requirements.txt file that lists all the required packages
  - Make a .gitignore file that ignores all unnecessary files
  - Implement LLM selection (Ollama, OpenAI, etc.)
  - Implement automatic installation of LLMs from Ollama
  - Ensure code follows PEP 8 guidelines
  - Ensure code is well-documented with comments and docstrings

- Add tests
  - Test Repository class
  - Test Issue class
  - Test main.py
  - Test issue generation function
  - Test GitHub issue creation function
  - Test LLM selection
  - Test automatic installation of LLMs from Ollama
  - Test command line arguments
  - Test error handling
  - Test edge cases
  - Test LLM installation
  - Test GitHub API integration
  - Test Ollama API integration
  - Test performance
  - Test security
  - Ensure 100% code coverage

- Add CI
  - Add GitHub Actions for running tests on every push
  - Ensure linting and formatting checks are included in CI
  - Update README with test coverage badge
  - Update README with CI status badge
  - Add Dependabot for dependency updates
  - Add code quality checks (e.g., using CodeClimate or SonarQube)

- Add documentation
  - Add docstrings to all classes and functions
  - Add usage examples to the README

- Add more LLMs
  - Add support for OpenAI's GPT-4
  - Add support for other popular LLMs (e.g., Cohere, AI21, etc.)
  - Add a configuration file to specify which LLM to use
  - Add a command line argument to specify which LLM to use
  - Add a function to list available LLMs
  - Add a function to check if the specified LLM is installed
  - Add a function to install the specified LLM if it is not installed

- Add fallback mechanism
  - If the specified LLM is not installed, fall back to a default LLM
  - If the default LLM is not installed, prompt the user to install it
  - If no LLMs are installed, exit with an error message

- Add configuration file
  - Add a config.yaml file to specify default settings (e.g., default LLM,
    default number of issues to create, etc.)
  - Add a function to read the configuration file
  - Add a function to write to the configuration file
  - Add a command line argument to specify a different configuration file
  - Add a function to validate the configuration file

- Add self correction mechanism
  - After generating an issue, use the LLM to review and improve the issue
    description
  - Implement a feedback loop where the user can provide feedback on the
    generated issues, and use that feedback to improve future issue generation
  - Use the LLM to analyze the commit history and file changes to identify
    patterns and trends that can inform issue generation
  - Implement a scoring system to rate the quality of generated issues,
    and use that score to improve future issue generation
  - Ensure that when LLMs give incorrect or nonsensical outputs, the system
    can identify and correct those errors using the LLM itself or other
    heuristics

- Add prompt pipelines
  - Create a series of prompts that guide the LLM through the issue
    generation process
  - Implement a mechanism to chain multiple prompts together to create more
    complex issue descriptions
  - Allow users to customize the prompt pipeline to suit their specific needs
  - Add a function to visualize the prompt pipeline and the flow of data
    through it
  - Ensure that the prompt pipeline is modular and can be easily extended
    with new prompts or modified as needed

- Add user interface
  - Create a simple web interface using Flask or Django to allow users to
    interact with the tool
  - Allow users to select the Git repository, LLM, and other settings
    through the web interface
  - Display the generated issues in a user-friendly format
  - Allow users to provide feedback on the generated issues through the
    web interface
  - Implement authentication and authorization to restrict access to the
    tool as needed
  - Ensure that the web interface is responsive and works well on different
    devices and screen sizes

- Add database integration
  - Use a database (e.g., SQLite, PostgreSQL, etc.) to store generated
    issues and their metadata
  - Allow users to view and manage previously generated issues through the
    user interface
  - Implement a search functionality to find specific issues based on
    keywords or other criteria
  - Ensure that the database is properly indexed for performance
  - Implement backup and restore functionality for the database
  - Ensure that the database is secure and access is restricted as needed

- Add user database
  - Allow users to create accounts and save their settings and preferences
  - Implement user profiles to store information about each user
  - Allow users to view their history of generated issues and manage them
  - Implement a rating system for users to rate the quality of generated
    issues
  - Ensure that user data is stored securely and access is restricted as needed

- Add analytics
  - Track usage statistics (e.g., number of issues generated, most popular
    LLMs, etc.)
  - Implement a dashboard to display analytics data in a user-friendly format
  - Allow users to export analytics data for further analysis
  - Use analytics data to identify areas for improvement and inform future
    development
  - Ensure that analytics data is collected and stored securely and access is
    restricted as needed

- Add notifications
  - Implement email notifications to inform users when new issues are
    generated
  - Allow users to customize their notification settings (e.g., frequency,
    types of notifications, etc.)
  - Implement push notifications for mobile devices
  - Ensure that notifications are sent securely and access is restricted as
    needed

- Add error handling
  - Implement robust error handling throughout the codebase
  - Ensure that meaningful error messages are displayed to the user
  - Log errors for further analysis and debugging
  - Implement a mechanism to report errors to the development team
  - Ensure that the tool can recover gracefully from errors and continue
    functioning as much as possible

- Add as much support for private repositories as possible
  - Implement OAuth authentication to allow users to access private
    repositories
  - Ensure that the tool can handle different types of authentication
    (e.g., personal access tokens, SSH keys, etc.)
  - Implement a mechanism to securely store and manage authentication
    credentials
  - Ensure that the tool respects repository permissions and only accesses
    data that the user has permission to access
  - Test the tool with a variety of private repositories to ensure
    compatibility

- Add support for user-defined issue templates
  - Allow users to create and manage their own issue templates
  - Implement a mechanism to select and use different issue templates
    based on the context (e.g., type of repository, type of issue, etc.)
  - Ensure that the tool can handle different formats for issue templates
    (e.g., Markdown, plain text, etc.)
  - Allow users to customize the generated issues based on their selected
    template
  - Test the tool with a variety of user-defined issue templates to ensure
    compatibility

- Add support for user-defined rules and heuristics
  - Allow users to define their own rules and heuristics for issue generation
  - Implement a mechanism to apply user-defined rules and heuristics during
    the issue generation process
  - Ensure that the tool can handle different types of rules and heuristics
    (e.g., keyword-based, pattern-based, etc.)
  - Allow users to customize the generated issues based on their defined
    rules and heuristics
  - Test the tool with a variety of user-defined rules and heuristics to
    ensure compatibility

- Add support for user-defined workflows
  - Allow users to define their own workflows for issue generation and
    management
  - Implement a mechanism to execute user-defined workflows during the
    issue generation process
  - Ensure that the tool can handle different types of workflows (e.g.,
    sequential, parallel, conditional, etc.)
  - Allow users to customize the generated issues based on their defined
    workflows
  - Test the tool with a variety of user-defined workflows to ensure
    compatibility

- Add support for user-hosted LLMs
  - Allow users to configure and use their own hosted LLMs for issue
    generation
  - Implement a mechanism to connect to and authenticate with user-hosted
    LLMs
  - Ensure that the tool can handle different types of user-hosted LLMs
    (e.g., different APIs, authentication methods, etc.)
  - Allow users to customize the generated issues based on their selected
    user-hosted LLM
  - Test the tool with a variety of user-hosted LLMs to ensure compatibility

