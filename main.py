#!/usr/bin/env python3
"""
Main entry point for Ticket-Master.

This script provides a command-line interface for generating GitHub issues
using AI analysis of Git repository contents.
"""

import argparse
import logging
import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any

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

from ticket_master import Repository, Issue, __version__
from ticket_master.repository import RepositoryError
from ticket_master.issue import IssueError, GitHubAuthError


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
            "provider": "ollama",  # Future implementation
            "model": "llama2",  # Future implementation
            "temperature": 0.7,  # Future implementation
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
                        result[key] = value
                return result

            return merge_dicts(default_config, user_config)

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

        # Get commit history
        max_commits = config["repository"]["max_commits"]
        commits = repo.get_commit_history(max_count=max_commits)
        logger.info(f"Retrieved {len(commits)} commits")

        # Get file changes
        file_changes = repo.get_file_changes(max_commits=max_commits)
        logger.info(
            f"Analyzed changes across {file_changes['summary']['total_files']} files"
        )

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


def generate_sample_issues(
    analysis: Dict[str, Any], config: Dict[str, Any]
) -> List[Issue]:
    """Generate sample issues based on repository analysis.

    Note: This is a placeholder implementation. In the future, this will use
    LLM integration to generate intelligent issue suggestions.

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

    # Issue 1: Documentation improvements
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

    # Test GitHub connection first
    try:
        from ticket_master.issue import test_github_connection

        connection_test = test_github_connection(config["github"]["token"])

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
    print("\n" + "=" * 80)
    print("TICKET-MASTER RESULTS SUMMARY")
    print("=" * 80)

    # Repository summary
    repo_info = analysis["repository_info"]
    summary = analysis["analysis_summary"]

    print(f"\nRepository: {repo_info['name']} ({repo_info['active_branch']})")
    print(f"Path: {repo_info['path']}")
    print(f"Commits analyzed: {summary['commit_count']}")
    print(f"Files modified: {summary['files_modified']}")
    print(f"Files added: {summary['files_added']}")
    print(
        f"Total changes: +{summary['total_insertions']}/-{summary['total_deletions']} lines"
    )

    # Issues summary
    print(f"\nIssues processed: {len(results)}")

    successful = [
        r for r in results if r.get("created") or r.get("would_create")
    ]
    failed = [r for r in results if r.get("error")]
    dry_run = any(r.get("dry_run") for r in results)

    if dry_run:
        print(f"Dry run completed: {len(successful)} issues would be created")
    else:
        print(f"Successfully created: {len(successful)} issues")

    if failed:
        print(f"Failed: {len(failed)} issues")

    # List issues
    print("\nIssue Details:")
    for result in results:
        status = (
            "✓"
            if (result.get("created") or result.get("would_create"))
            else "✗"
        )
        title = (
            result["title"][:60] + "..."
            if len(result["title"]) > 60
            else result["title"]
        )

        if result.get("url"):
            print(f"  {status} #{result['issue_number']}: {title}")
            print(f"    URL: {result['url']}")
        elif result.get("dry_run"):
            print(f"  {status} [DRY RUN] {title}")
        else:
            print(f"  {status} FAILED: {title}")
            if result.get("error"):
                print(f"    Error: {result['error']}")

        if result.get("validation_warnings"):
            print(f"    Warnings: {'; '.join(result['validation_warnings'])}")

    print("\n" + "=" * 80)


def main() -> int:
    """Main entry point for the application.

    Returns:
        Exit code (0 for success, non-zero for error)
    """
    parser = argparse.ArgumentParser(
        description="Ticket-Master: AI-powered GitHub issue generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/repo owner/repo
  %(prog)s /path/to/repo owner/repo --dry-run
  %(prog)s /path/to/repo owner/repo --config config.yaml --max-issues 3
  %(prog)s /path/to/repo owner/repo --log-level DEBUG

Environment Variables:
  GITHUB_TOKEN    GitHub personal access token (required)

For more information, see: https://github.com/dhodgson615/Ticket-Master
        """,
    )

    # Required arguments
    parser.add_argument(
        "repository_path", help="Path to the Git repository to analyze"
    )

    parser.add_argument(
        "github_repo", help='GitHub repository name in format "owner/repo"'
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
        if args.max_issues:
            config["issue_generation"]["max_issues"] = args.max_issues

        # Validate required configuration
        if not config["github"]["token"]:
            logger.error(
                "GitHub token not found. Set GITHUB_TOKEN environment variable or add to config file."
            )
            return 1

        # Validate repository path
        repo_path = Path(args.repository_path).resolve()
        if not repo_path.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            return 1

        # Validate GitHub repository format
        if "/" not in args.github_repo or args.github_repo.count("/") != 1:
            logger.error("GitHub repository must be in format 'owner/repo'")
            return 1

        # Analyze repository
        logger.info("Analyzing repository...")
        analysis = analyze_repository(str(repo_path), config)

        # Generate issues
        logger.info("Generating issues...")
        issues = generate_sample_issues(analysis, config)

        if not issues:
            logger.warning(
                "No issues were generated based on repository analysis"
            )
            return 0

        # Create issues on GitHub
        logger.info(f"Processing {len(issues)} issues...")
        results = create_issues_on_github(
            issues, args.github_repo, config, args.dry_run
        )

        # Print summary
        print_results_summary(results, analysis)

        # Determine exit code
        failed_count = len([r for r in results if r.get("error")])
        return 1 if failed_count > 0 else 0

    except KeyboardInterrupt:
        logger.info("Operation cancelled by user")
        return 130
    except (RepositoryError, IssueError, GitHubAuthError) as e:
        logger.error(f"Application error: {e}")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
