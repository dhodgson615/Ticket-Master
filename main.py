#!/usr/bin/env python3
"""
Main entry point for Ticket-Master.

This script provides a command-line interface for generating GitHub issues
using AI analysis of Git repository contents.
"""

import argparse
import json
import logging
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import with fallback installation
try:
    import yaml
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "PyYAML>=6.0.1"]
    )
    import yaml

from ticket_master import Issue, Repository, __version__
from ticket_master.issue import GitHubAuthError, IssueError
from ticket_master.llm import LLM, LLMError
from ticket_master.repository import RepositoryError
from ticket_master.github_utils import GitHubUtils, GitHubCloneError
from ticket_master.colors import (
    success,
    error,
    warning,
    info,
    header,
    highlight,
    dim,
    print_colored,
    Colors,
)


def setup_logging(level: str = "INFO") -> None:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    numeric_level = getattr(logging, level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Setup console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # Setup root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)
    root_logger.addHandler(console_handler)

    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("github").setLevel(logging.WARNING)
    logging.getLogger("git").setLevel(logging.WARNING)


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to configuration file (optional)

    Returns:
        Configuration dictionary with defaults applied
    """
    # Default configuration
    default_config = {
        "github": {
            "token": os.getenv("GITHUB_TOKEN"),
            "default_labels": ["enhancement", "automated"],
        },
        "repository": {
            "max_commits": 50,
            "ignore_patterns": [
                ".git",
                "__pycache__",
                "*.pyc",
                "node_modules",
            ],
        },
        "issue_generation": {"max_issues": 5, "min_description_length": 50},
        "llm": {
            "provider": "ollama",
            "model": "llama3.2",
            "host": "localhost",
            "port": 11434,
            "temperature": 0.7,
        },
    }

    if config_path and Path(config_path).exists():
        try:
            with open(config_path, "r", encoding="utf-8") as f:
                user_config = yaml.safe_load(f) or {}

            # Merge user config with defaults
            def merge_dicts(default: Dict, user: Dict) -> Dict:
                """Recursively merge dictionaries."""
                result = default.copy()
                for key, value in user.items():
                    if (
                        key in result
                        and isinstance(result[key], dict)
                        and isinstance(value, dict)
                    ):
                        result[key] = merge_dicts(result[key], value)
                    else:
                        # Don't override with null values - keep defaults
                        if value is not None:
                            result[key] = value
                return result

            merged_config = merge_dicts(default_config, user_config)

            # Ensure github token is set from environment if not in config
            if not merged_config["github"]["token"]:
                merged_config["github"]["token"] = os.getenv("GITHUB_TOKEN")

            return merged_config

        except Exception as e:
            logging.getLogger(__name__).warning(
                f"Failed to load config from {config_path}: {e}"
            )

    return default_config


def analyze_repository(
    repo_path: str, config: Dict[str, Any]
) -> Dict[str, Any]:
    """Analyze repository and prepare data for issue generation.

    Args:
        repo_path: Path to Git repository
        config: Configuration dictionary

    Returns:
        Dictionary containing repository analysis results

    Raises:
        RepositoryError: If repository analysis fails
    """
    logger = logging.getLogger(__name__)

    try:
        # Initialize repository
        repo = Repository(repo_path)
        logger.info(f"Analyzing repository: {repo.path}")

        # Get repository information
        repo_info = repo.get_repository_info()
        logger.info(
            f"Repository: {repo_info['name']} ({repo_info['active_branch']})"
        )

        # Try to get commit history, but fall back to minimal analysis if it fails
        max_commits = config["repository"]["max_commits"]
        try:
            commits = repo.get_commit_history(max_count=max_commits)
            logger.info(f"Retrieved {len(commits)} commits")
        except Exception as commit_error:
            logger.warning(
                f"Could not get detailed commit history: {commit_error}"
            )
            logger.info("Using minimal commit analysis")
            commits = [
                {
                    "hash": "unknown",
                    "short_hash": "unknown",
                    "author": {"name": "unknown", "email": "unknown"},
                    "committer": {"name": "unknown", "email": "unknown"},
                    "message": "Repository analysis limited due to git issues",
                    "summary": "Limited analysis mode",
                    "date": datetime.now(),
                    "files_changed": 0,
                    "insertions": 0,
                    "deletions": 0,
                }
            ]

        # Try to get file changes, but fall back to minimal analysis if it fails
        try:
            file_changes = repo.get_file_changes(max_commits=max_commits)
            logger.info(
                f"Analyzed changes across "
                f"{file_changes['summary']['total_files']} files"
            )
        except Exception as file_error:
            logger.warning(
                f"Could not get detailed file changes: {file_error}"
            )
            logger.info("Using minimal file change analysis")
            file_changes = {
                "modified_files": {},
                "new_files": [],
                "deleted_files": [],
                "renamed_files": [],
                "summary": {
                    "total_files": 1,
                    "total_insertions": 0,
                    "total_deletions": 0,
                },
            }

        return {
            "repository_info": repo_info,
            "commits": commits,
            "file_changes": file_changes,
            "analysis_summary": {
                "commit_count": len(commits),
                "files_modified": len(file_changes["modified_files"]),
                "files_added": len(file_changes["new_files"]),
                "files_deleted": len(file_changes["deleted_files"]),
                "total_insertions": file_changes["summary"][
                    "total_insertions"
                ],
                "total_deletions": file_changes["summary"]["total_deletions"],
            },
        }

    except Exception as e:
        raise RepositoryError(f"Repository analysis failed: {e}")


def generate_issues_with_llm(
    analysis: Dict[str, Any], config: Dict[str, Any]
) -> List[Issue]:
    """Generate issues using LLM based on repository analysis.

    Args:
        analysis: Repository analysis results
        config: Configuration dictionary

    Returns:
        List of generated Issue objects
    """
    logger = logging.getLogger(__name__)
    issues = []

    try:
        # Get max issues from config
        max_issues = config["issue_generation"]["max_issues"]

        # Initialize LLM
        llm_config = config["llm"].copy()
        provider = llm_config.pop("provider", "ollama")

        logger.info(f"Initializing LLM with provider: {provider}")

        # Use Ollama tools if provider is Ollama
        if provider == "ollama":
            try:
                from ticket_master.ollama_tools import create_ollama_processor

                processor = create_ollama_processor(llm_config)

                # Check availability
                if not processor.client:
                    logger.warning(
                        "Ollama client not available, falling back to standard LLM"
                    )
                    return generate_issues_with_standard_llm(analysis, config)

                # Generate issues using Ollama tools
                logger.info("Using Ollama tools for issue generation...")
                generated_issues = processor.generate_issues_from_analysis(
                    analysis, max_issues=max_issues
                )

                # Convert to Issue objects
                default_labels = config["github"]["default_labels"]

                for issue_data in generated_issues:
                    try:
                        # Combine default labels with generated labels
                        issue_labels = default_labels.copy()
                        suggested_labels = issue_data.get("labels", [])
                        if isinstance(suggested_labels, list):
                            issue_labels.extend(suggested_labels)

                        issue = Issue(
                            title=issue_data["title"],
                            description=issue_data["description"],
                            labels=issue_labels,
                            assignees=issue_data.get("assignees", []),
                        )

                        issues.append(issue)
                        logger.info(f"Created issue: {issue_data['title']}")

                    except Exception as e:
                        logger.error(
                            f"Error creating issue from Ollama data: {e}"
                        )
                        continue

                if issues:
                    logger.info(
                        f"Successfully generated {len(issues)} issues using Ollama tools"
                    )
                    return issues
                else:
                    logger.warning(
                        "No valid issues generated using Ollama tools, falling back"
                    )

            except Exception as e:
                logger.warning(
                    f"Ollama tools failed: {e}, falling back to standard LLM"
                )

        return generate_issues_with_standard_llm(analysis, config)

    except Exception as e:
        logger.error(f"Unexpected error in LLM issue generation: {e}")
        logger.info("Falling back to sample issue generation")
        return generate_sample_issues(analysis, config)


def generate_issues_with_standard_llm(
    analysis: Dict[str, Any], config: Dict[str, Any]
) -> List[Issue]:
    """Generate issues using standard LLM interface.

    Args:
        analysis: Repository analysis results
        config: Configuration dictionary

    Returns:
        List of generated Issue objects
    """
    logger = logging.getLogger(__name__)
    issues = []

    try:
        # Get max issues from config
        max_issues = config["issue_generation"]["max_issues"]

        # Initialize LLM
        llm_config = config["llm"].copy()
        provider = llm_config.pop("provider", "ollama")

        llm = LLM(provider, llm_config)

        # Check if LLM is available
        if not llm.is_available():
            logger.warning(
                f"LLM provider {provider} is not available, "
                "falling back to sample generation"
            )
            return generate_sample_issues(analysis, config)

        # Use proper prompt template system
        from ticket_master.prompt import Prompt

        prompt_manager = Prompt()
        prompt_manager.create_builtin_templates()  # Ensure built-in templates are created

        # Prepare variables for the prompt template
        template_variables = {
            "repo_path": analysis["repository_info"]["path"],
            "commit_count": analysis["analysis_summary"]["commit_count"],
            "modified_files_count": analysis["analysis_summary"][
                "files_modified"
            ],
            "new_files_count": analysis["analysis_summary"]["files_added"],
            "num_issues": max_issues,
            "recent_changes": "\n".join(
                f"- {commit['short_hash']}: {commit['summary']}"
                for commit in analysis["commits"][:5]
            ),
            "file_changes_summary": f"Modified: {analysis['analysis_summary']['files_modified']} files, "
            f"Added: {analysis['analysis_summary']['files_added']} files, "
            f"Changes: +{analysis['analysis_summary']['total_insertions']}/"
            f"-{analysis['analysis_summary']['total_deletions']} lines",
        }

        # Get the appropriate prompt template for the LLM provider
        template = prompt_manager.get_template("basic_issue_generation")
        if not template:
            logger.warning("No prompt template found, using fallback")
            return generate_sample_issues(analysis, config)

        prompt = template.render(provider, **template_variables)

        logger.info("Generating issues using LLM...")

        # Generate response using LLM
        llm_response = llm.generate(
            prompt,
            temperature=llm_config.get("temperature", 0.7),
            max_tokens=llm_config.get("max_tokens", 2000),
        )

        if not llm_response or not llm_response.get("response"):
            logger.warning(
                "LLM generated empty response, falling back to sample generation"
            )
            return generate_sample_issues(analysis, config)

        # Parse the LLM response to extract issues
        generated_text = llm_response["response"]
        logger.debug(f"LLM generated response: {generated_text}")

        # Try to parse the response as JSON first
        parsed_issues = []
        try:
            # Clean the response - remove any markdown formatting
            cleaned_response = generated_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            cleaned_response = cleaned_response.strip()

            # Try to parse as JSON
            parsed_issues = json.loads(cleaned_response)

            # Ensure it's a list
            if not isinstance(parsed_issues, list):
                parsed_issues = [parsed_issues] if parsed_issues else []

        except json.JSONDecodeError:
            # If JSON parsing fails, try to extract issues from text
            logger.warning(
                "Failed to parse as JSON, attempting text extraction"
            )
            parsed_issues = []

        if not parsed_issues:
            logger.warning(
                "Failed to parse LLM response, falling back to sample generation"
            )
            return generate_sample_issues(analysis, config)

        # Convert parsed data to Issue objects
        default_labels = config["github"]["default_labels"]

        for issue_data in parsed_issues[:max_issues]:
            try:
                # Ensure minimum required fields
                title = issue_data.get("title", "").strip()
                description = issue_data.get("description", "").strip()

                if not title or not description:
                    logger.warning(f"Skipping incomplete issue: {issue_data}")
                    continue

                # Combine default labels with LLM-suggested labels
                issue_labels = default_labels.copy()
                suggested_labels = issue_data.get("labels", [])
                if isinstance(suggested_labels, list):
                    issue_labels.extend(suggested_labels)

                issue = Issue(
                    title=title,
                    description=description,
                    labels=issue_labels,
                    assignees=issue_data.get("assignees", []),
                )

                issues.append(issue)
                logger.info(f"Created issue: {title}")

            except Exception as e:
                logger.error(f"Error creating issue from LLM data: {e}")
                continue

        if not issues:
            logger.warning("No valid issues were generated from LLM response")
            return generate_sample_issues(analysis, config)

        logger.info(f"Successfully generated {len(issues)} issues using LLM")
        return issues

    except LLMError as e:
        logger.error(f"LLM error: {e}")
        logger.info("Falling back to sample issue generation")
        return generate_sample_issues(analysis, config)

    except Exception as e:
        logger.error(f"Unexpected error in LLM issue generation: {e}")
        logger.info("Falling back to sample issue generation")
        return generate_sample_issues(analysis, config)


def generate_sample_issues(
    analysis: Dict[str, Any], config: Dict[str, Any]
) -> List[Issue]:
    """Generate sample issues based on repository analysis.

    This is a fallback implementation that generates basic issues based on
    repository patterns when LLM is not available.

    Args:
        analysis: Repository analysis results
        config: Configuration dictionary

    Returns:
        List of generated Issue objects
    """
    logger = logging.getLogger(__name__)
    issues = []

    commits = analysis["commits"]
    file_changes = analysis["file_changes"]
    summary = analysis["analysis_summary"]

    # Generate issues based on analysis patterns
    default_labels = config["github"]["default_labels"]

    # Always generate at least one issue for basic functionality testing
    issues.append(
        Issue(
            title="Repository Analysis and Issue Generation",
            description=f"""## Repository Analysis Complete

Ticket-Master has successfully analyzed this repository:

**Repository Information:**
- Repository: {analysis.get('repository_info', {}).get('name', 'Unknown')}
- Active Branch: {analysis.get('repository_info', {}).get('active_branch', 'Unknown')}
- Commits Analyzed: {summary['commit_count']}
- Files Modified: {summary['files_modified']}
- Files Added: {summary['files_added']}

**Analysis Summary:**
- Total Insertions: {summary['total_insertions']}
- Total Deletions: {summary['total_deletions']}

This issue demonstrates that Ticket-Master is working correctly and can analyze your repository to generate relevant issues.

**Next Steps:**
1. Review this generated issue
2. Configure LLM integration for more sophisticated issue generation
3. Customize issue templates and patterns for your project

This issue was automatically generated based on repository analysis.""",
            labels=default_labels + ["automated", "analysis"],
        )
    )

    # Issue 1: Documentation improvements (if applicable)
    if summary["files_modified"] > 5:
        issues.append(
            Issue(
                title="Update project documentation based on recent changes",
                description=f"""## Documentation Update Required

Based on recent repository activity, the project documentation may need updates:

**Recent Activity Summary:**
- {summary['commit_count']} commits analyzed
- {summary['files_modified']} files modified
- {summary['files_added']} new files added
- {summary['total_insertions']} lines added, {summary['total_deletions']} lines removed

**Suggested Actions:**
- Review README.md for accuracy
- Update API documentation if applicable
- Add documentation for new features
- Review and update installation instructions

**Files that may need documentation updates:**
{chr(10).join(f"- {file}" for file in list(file_changes['modified_files'].keys())[:5])}
{"- ... and more" if len(file_changes['modified_files']) > 5 else ""}

This issue was automatically generated based on repository analysis.""",
                labels=default_labels + ["documentation"],
            )
        )

    # Issue 2: Code review for high-activity files
    high_activity_files = {
        file: info
        for file, info in file_changes["modified_files"].items()
        if info["changes"] > 3
    }

    if high_activity_files:
        issues.append(
            Issue(
                title="Code review needed for frequently modified files",
                description=f"""## Code Review Required

The following files have been modified frequently in recent commits and may benefit from a code review:

**High-Activity Files:**
{chr(10).join(f"- `{file}`: {info['changes']} changes, +{info['insertions']}/-{info['deletions']} lines" for file, info in high_activity_files.items())}

**Recommended Review Areas:**
- Code quality and maintainability
- Performance implications of changes
- Test coverage for modified code
- Documentation updates needed
- Potential refactoring opportunities

**Recent Commits Affecting These Files:**
{chr(10).join(f"- {commit['short_hash']}: {commit['summary']}" for commit in commits[:3])}

This issue was automatically generated based on repository analysis.""",
                labels=default_labels + ["code-review", "maintenance"],
            )
        )

    # Issue 3: Testing improvements
    if summary["files_added"] > 0:
        issues.append(
            Issue(
                title="Add tests for recently added functionality",
                description=f"""## Testing Requirements

New files have been added to the repository that may require test coverage:

**Recently Added Files:**
{chr(10).join(f"- {file}" for file in file_changes['new_files'][:10])}
{"- ... and more" if len(file_changes['new_files']) > 10 else ""}

**Suggested Testing Actions:**
- Add unit tests for new functions and classes
- Add integration tests for new features
- Update test coverage reports
- Review existing tests for compatibility with changes
- Consider adding performance tests if applicable

**Testing Best Practices:**
- Ensure each new public method has corresponding tests
- Test both success and error scenarios
- Use appropriate mocking for external dependencies

This issue was automatically generated based on repository analysis.""",
                labels=default_labels + ["testing", "quality-assurance"],
            )
        )

    # Limit number of issues based on configuration
    max_issues = config["issue_generation"]["max_issues"]
    if len(issues) > max_issues:
        issues = issues[:max_issues]
        logger.info(f"Limited issues to {max_issues} as configured")

    logger.info(f"Generated {len(issues)} sample issues")
    return issues


def create_issues_on_github(
    issues: List[Issue],
    repo_name: str,
    config: Dict[str, Any],
    dry_run: bool = True,
) -> List[Dict[str, Any]]:
    """Create issues on GitHub.

    Args:
        issues: List of Issue objects to create
        repo_name: GitHub repository name (owner/repo)
        config: Configuration dictionary
        dry_run: If True, validate but don't actually create issues

    Returns:
        List of dictionaries containing creation results

    Raises:
        GitHubAuthError: If GitHub authentication fails
        IssueError: If issue creation fails
    """
    logger = logging.getLogger(__name__)
    results = []

    if dry_run:
        logger.info("DRY RUN MODE: Issues will be validated but not created")

    # Test GitHub connection first (skip if using dummy token or dry run)
    github_token = config["github"]["token"]
    if not dry_run and github_token and github_token != "dummy_token":
        try:
            from ticket_master.issue import test_github_connection

            connection_test = test_github_connection(github_token)

            if not connection_test["authenticated"]:
                raise GitHubAuthError(
                    f"GitHub authentication failed: {connection_test['error']}"
                )

            logger.info(
                f"Connected to GitHub as: {connection_test['user']['login']}"
            )
            logger.info(
                f"Rate limit remaining: {connection_test['rate_limit']['core']['remaining']}"
            )

        except Exception as e:
            raise GitHubAuthError(f"Failed to connect to GitHub: {e}")
    else:
        if dry_run:
            logger.info("Skipping GitHub connection test in dry-run mode")
        else:
            logger.info(
                "Skipping GitHub connection test with dummy/missing token"
            )

    # Process each issue
    for i, issue in enumerate(issues, 1):
        try:
            # Validate issue content
            warnings = issue.validate_content()
            if warnings:
                logger.warning(
                    f"Issue {i} validation warnings: {'; '.join(warnings)}"
                )

            if dry_run:
                result = {
                    "issue_number": i,
                    "title": issue.title,
                    "dry_run": True,
                    "validation_warnings": warnings,
                    "would_create": True,
                }
                logger.info(f"[DRY RUN] Would create issue {i}: {issue.title}")
            else:
                # Actually create the issue
                issue_info = issue.create_on_github(
                    repo_name, config["github"]["token"]
                )
                result = {
                    "issue_number": issue_info["number"],
                    "title": issue_info["title"],
                    "url": issue_info["url"],
                    "created": True,
                    "validation_warnings": warnings,
                }
                logger.info(
                    f"Created issue #{issue_info['number']}: {issue.title}"
                )

            results.append(result)

        except Exception as e:
            error_result = {
                "issue_number": i,
                "title": issue.title,
                "error": str(e),
                "created": False,
            }
            results.append(error_result)
            logger.error(f"Failed to create issue {i}: {e}")

    return results


def print_results_summary(
    results: List[Dict[str, Any]], analysis: Dict[str, Any]
) -> None:
    """Print summary of results to console.

    Args:
        results: List of issue creation results
        analysis: Repository analysis results
    """
    print_colored("\n" + "=" * 80, Colors.CYAN, Colors.BOLD)
    print_colored("TICKET-MASTER RESULTS SUMMARY", Colors.CYAN, Colors.BOLD)
    print_colored("=" * 80, Colors.CYAN, Colors.BOLD)

    # Repository summary
    repo_info = analysis["repository_info"]
    summary = analysis["analysis_summary"]

    print(
        f"\n{info('Repository:')} {highlight(repo_info['name'])} ({dim(repo_info['active_branch'])})"
    )
    print(f"{info('Path:')} {dim(repo_info['path'])}")
    print(
        f"{info('Commits analyzed:')} {highlight(str(summary['commit_count']))}"
    )
    print(
        f"{info('Files modified:')} {highlight(str(summary['files_modified']))}"
    )
    print(f"{info('Files added:')} {highlight(str(summary['files_added']))}")
    insertions = summary["total_insertions"]
    deletions = summary["total_deletions"]
    print(
        f"{info('Total changes:')} {success(f'+{insertions}')}/{error(f'-{deletions}', False)} lines"
    )

    # Issues summary
    print(f"\n{header('Issues processed:')} {highlight(str(len(results)))}")

    successful = [
        r for r in results if r.get("created") or r.get("would_create")
    ]
    failed = [r for r in results if r.get("error")]
    dry_run = any(r.get("dry_run") for r in results)

    if dry_run:
        print(
            f"{info('Dry run completed:')} {success(f'{len(successful)} issues would be created', True)}"
        )
    else:
        print(
            f"{success('Successfully created:')} {success(f'{len(successful)} issues', True)}"
        )

    if failed:
        print(f"{error('Failed:')} {error(f'{len(failed)} issues', True)}")

    # List issues
    print(f"\n{header('Issue Details:')}")
    for result in results:
        status_symbol = (
            "✓"
            if (result.get("created") or result.get("would_create"))
            else "✗"
        )
        status_color = (
            success
            if (result.get("created") or result.get("would_create"))
            else error
        )
        title = (
            result["title"][:60] + "..."
            if len(result["title"]) > 60
            else result["title"]
        )

        if result.get("url"):
            print(
                f"  {status_color(status_symbol)} #{highlight(str(result['issue_number']))}: {title}"
            )
            print(f"    {dim('URL:')} {info(result['url'])}")
        elif result.get("dry_run"):
            print(
                f"  {status_color(status_symbol)} {warning('[DRY RUN]', True)} {title}"
            )
        else:
            print(
                f"  {status_color(status_symbol)} {error('FAILED:', True)} {title}"
            )
            if result.get("error"):
                print(f"    {error('Error:')} {result['error']}")

        if result.get("validation_warnings"):
            print(
                f"    {warning('Warnings:')} {'; '.join(result['validation_warnings'])}"
            )

    print_colored("\n" + "=" * 80, Colors.CYAN, Colors.BOLD)


def validate_config_command(config_path: Optional[str] = None) -> int:
    """Validate configuration file and display results.

    Args:
        config_path: Path to configuration file (optional)

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    logger = logging.getLogger(__name__)

    try:
        logger.info("Validating configuration...")

        # Load configuration
        config = load_config(config_path)

        print_colored("\n" + "=" * 60, Colors.CYAN, Colors.BOLD)
        print_colored(
            "CONFIGURATION VALIDATION RESULTS", Colors.CYAN, Colors.BOLD
        )
        print_colored("=" * 60, Colors.CYAN, Colors.BOLD)

        validation_results = []

        # Validate GitHub configuration
        github_config = config.get("github", {})
        if github_config.get("token"):
            print(f"{success('✓')} {info('GitHub token:')} {success('Found')}")
            validation_results.append(("GitHub token", True, "Token found"))

            # Test GitHub connection
            try:
                from ticket_master.issue import test_github_connection

                connection_result = test_github_connection(
                    github_config["token"]
                )
                if connection_result.get("authenticated"):
                    user_info = connection_result.get("user", {})
                    username = user_info.get("login", "unknown")
                    auth_msg = f"Authenticated as {highlight(username)}"
                    print(
                        f"{success('✓')} {info('GitHub connection:')} {success(auth_msg)}"
                    )
                    validation_results.append(
                        (
                            "GitHub connection",
                            True,
                            f"Authenticated as {user_info.get('login')}",
                        )
                    )
                else:
                    error_msg = connection_result.get("error", "Unknown error")
                    print(
                        f"{error('✗')} {info('GitHub connection:')} {error(f'Failed - {error_msg}')}"
                    )
                    validation_results.append(
                        (
                            "GitHub connection",
                            False,
                            connection_result.get("error", "Unknown error"),
                        )
                    )
            except Exception as e:
                print(
                    f"{error('✗')} {info('GitHub connection:')} {error(f'Error testing connection - {e}')}"
                )
                validation_results.append(("GitHub connection", False, str(e)))
        else:
            print(f"{error('✗')} {info('GitHub token:')} {error('Missing')}")
            validation_results.append(
                (
                    "GitHub token",
                    False,
                    "Token not found in config or environment",
                )
            )

        # Validate LLM configuration
        llm_config = config.get("llm", {})
        provider = llm_config.get("provider", "ollama")
        print(f"{success('✓')} {info('LLM provider:')} {highlight(provider)}")
        validation_results.append(
            ("LLM provider", True, f"Provider set to {provider}")
        )

        # Test LLM availability
        try:
            from ticket_master.llm import LLM

            llm = LLM(provider, llm_config)

            if llm.is_available():
                print(
                    f"{success('✓')} {info('LLM availability:')} {success(f'{provider} is available')}"
                )
                validation_results.append(
                    ("LLM availability", True, f"{provider} is available")
                )

                # Check model availability
                model_info = llm.backend.get_model_info()
                model_name = model_info.get(
                    "name", llm_config.get("model", "unknown")
                )
                if model_info.get("status") not in [
                    "not_found",
                    "model_not_found",
                    "unavailable",
                    "error",
                ]:
                    print(
                        f"{success('✓')} {info('LLM model:')} {success(f'{model_name} is available')}"
                    )
                    validation_results.append(
                        ("LLM model", True, f"{model_name} is available")
                    )
                else:
                    print(
                        f"{error('✗')} {info('LLM model:')} {error(f'{model_name} not found')}"
                    )
                    validation_results.append(
                        ("LLM model", False, f"{model_name} not found")
                    )

                    # Offer to install if Ollama
                    if provider == "ollama":
                        print(
                            f"  {dim('→')} {warning(f'You can install it with: ollama pull {model_name}')}"
                        )
            else:
                print(
                    f"{error('✗')} {info('LLM availability:')} {error(f'{provider} is not available')}"
                )
                validation_results.append(
                    ("LLM availability", False, f"{provider} is not available")
                )

                if provider == "ollama":
                    print(
                        f"  {dim('→')} {warning('Make sure Ollama is running (ollama serve)')}"
                    )
        except Exception as e:
            print(
                f"{error('✗')} {info('LLM configuration:')} {error(f'Error testing LLM - {e}')}"
            )
            validation_results.append(("LLM configuration", False, str(e)))

        # Validate other configuration sections
        repo_config = config.get("repository", {})
        max_commits = repo_config.get("max_commits", 50)
        print(
            f"{success('✓')} {info('Repository config:')} {highlight(f'Max commits: {max_commits}')}"
        )
        validation_results.append(
            ("Repository config", True, "Configuration valid")
        )

        issue_config = config.get("issue_generation", {})
        max_issues = issue_config.get("max_issues", 5)
        print(
            f"{success('✓')} {info('Issue generation config:')} {highlight(f'Max issues: {max_issues}')}"
        )
        validation_results.append(
            ("Issue generation config", True, "Configuration valid")
        )

        # Summary
        print_colored("\n" + "-" * 60, Colors.YELLOW)
        passed = sum(1 for _, status, _ in validation_results if status)
        total = len(validation_results)
        print(
            f"{header('Validation Summary:')} {highlight(f'{passed}/{total}')} checks passed"
        )

        if passed == total:
            print(
                f"{success('✓', True)} {success('Configuration is valid and ready to use!', True)}"
            )
            return 0
        else:
            print(
                f"{error('✗', True)} {error('Configuration has issues that need to be resolved.', True)}"
            )
            return 1

    except Exception as e:
        logger.error(f"Configuration validation failed: {e}")
        print(
            f"\n{error('✗', True)} {error(f'Configuration validation failed: {e}')}"
        )
        return 1


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Check if this looks like the validate-config command
    if len(sys.argv) > 1 and sys.argv[1] == "validate-config":
        # Handle validate-config command
        parser = argparse.ArgumentParser(
            description="Validate Ticket-Master configuration",
            formatter_class=argparse.RawDescriptionHelpFormatter,
        )
        parser.add_argument("command", help="Command to run")
        parser.add_argument("--config", help="Path to configuration YAML file")
        parser.add_argument(
            "--log-level",
            choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
            default="INFO",
            help="Set the logging level",
        )

        args = parser.parse_args()
        setup_logging(args.log_level)

        return validate_config_command(getattr(args, "config", None))

    # Default behavior - generate issues (backward compatibility)
    parser = argparse.ArgumentParser(
        description="Ticket-Master: AI-powered GitHub issue generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s owner/repo
  %(prog)s https://github.com/owner/repo --dry-run
  %(prog)s owner/repo --local-path /path/to/repo --config config.yaml \\
    --max-issues 3
  %(prog)s validate-config --config config.yaml

Environment Variables:
  GITHUB_TOKEN    GitHub personal access token (required for private repos)

For more information, see:
  https://github.com/dhodgson615/Ticket-Master
        """,
    )

    # Required arguments
    parser.add_argument(
        "github_repo",
        help='GitHub repository name in format "owner/repo" or GitHub URL',
    )

    # Optional arguments
    parser.add_argument(
        "--local-path",
        help="Optional path to local Git repository. If not provided, "
        "repository will be cloned to a temporary directory",
    )

    # Optional arguments
    parser.add_argument("--config", help="Path to configuration YAML file")

    parser.add_argument(
        "--max-issues",
        type=int,
        help="Maximum number of issues to generate (overrides config)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate and show issues that would be created without actually creating them",
    )

    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Set the logging level",
    )

    parser.add_argument(
        "--version", action="version", version=f"Ticket-Master {__version__}"
    )

    args = parser.parse_args()

    # Setup logging
    setup_logging(args.log_level)
    logger = logging.getLogger(__name__)

    try:
        logger.info(f"Starting Ticket-Master {__version__}")

        # Load configuration
        config = load_config(args.config)

        # Apply command line overrides
        if hasattr(args, "max_issues") and args.max_issues:
            config["issue_generation"]["max_issues"] = args.max_issues

        # Initialize GitHub utilities
        github_utils = GitHubUtils()
        repo_path = None
        temp_repo_path = None

        # Parse and validate GitHub repository format
        try:
            github_repo = github_utils.parse_github_url(args.github_repo)
            logger.info(f"Analyzing GitHub repository: {github_repo}")
        except ValueError as e:
            logger.error(str(e))
            return 1

        # Check if repository is public
        is_public = github_utils.is_public_repository(github_repo)
        logger.info(
            f"Repository is {'public' if is_public else 'private/not found'}"
        )

        # Handle authentication requirements
        github_token = config["github"]["token"]
        if not is_public and not github_token:
            logger.error(
                f"Repository {github_repo} appears to be private but no GitHub token found. "
                "Set GITHUB_TOKEN environment variable or add to config file."
            )
            return 1
        elif is_public and not github_token:
            logger.info(
                "Public repository detected - GitHub token not required"
            )

        # Handle repository path - either use provided local path or clone
        if hasattr(args, "local_path") and args.local_path:
            # Use provided local path
            repo_path = Path(args.local_path).resolve()
            if not repo_path.exists():
                logger.error(
                    f"Local repository path does not exist: {repo_path}"
                )
                return 1
            logger.info(f"Using local repository at: {repo_path}")
        else:
            # Clone repository to temporary location
            logger.info(f"Cloning {github_repo} to temporary directory...")
            try:
                temp_repo_path = github_utils.clone_repository(
                    github_repo, token=github_token if not is_public else None
                )
                repo_path = Path(temp_repo_path)
                logger.info(f"Repository cloned to: {repo_path}")
            except GitHubCloneError as e:
                logger.error(f"Failed to clone repository: {e}")
                return 1

        # Analyze repository
        logger.info("Analyzing repository...")
        analysis = analyze_repository(str(repo_path), config)

        # Generate issues
        logger.info("Generating issues using AI...")
        issues = generate_issues_with_llm(analysis, config)

        if not issues:
            logger.warning(
                "No issues were generated based on repository analysis"
            )
            return 0

        # Create issues on GitHub
        logger.info(f"Processing {len(issues)} issues...")
        results = create_issues_on_github(
            issues, github_repo, config, args.dry_run
        )

        # Print summary
        print_results_summary(results, analysis)

        # Determine exit code
        failed_count = len([r for r in results if r.get("error")])
        return 1 if failed_count > 0 else 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except (
        RepositoryError,
        IssueError,
        GitHubAuthError,
        GitHubCloneError,
    ) as e:
        logger.error(f"Application error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1
    finally:
        # Cleanup temporary directories
        if "github_utils" in locals():
            github_utils.cleanup_temp_directories()


if __name__ == "__main__":
    sys.exit(main())
