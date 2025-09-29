#!/usr/bin/env python3
"""
Flask web interface for Ticket-Master.

This provides a web-based interface for generating GitHub issues
using AI analysis of Git repository contents.
"""

import os
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from flask import flash  # noqa: E402
from flask import Flask, jsonify, redirect, render_template, request, url_for

# Import the main CLI functions to reuse logic
from main import generate_sample_issues, load_config  # noqa: E402
from ticket_master import Repository, __version__  # noqa: E402
from ticket_master.colors import header, info, success  # noqa: E402
from ticket_master.github_utils import (GitHubCloneError,  # noqa: E402
                                        GitHubUtils)
from ticket_master.issue import GitHubAuthError, Issue  # noqa: E402
from ticket_master.repository import RepositoryError  # noqa: E402

app = Flask(__name__)
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY", "dev-key-please-change-in-production"
)


@app.route("/")
def index():
    """Home page with repository input form."""
    return render_template("index.html", version=__version__)


@app.route("/generate", methods=["POST"])
def generate_issues():
    """Generate issues for the specified repository."""
    github_utils = None
    try:
        # Get form data
        github_repo_input = request.form.get("github_repo", "").strip()
        repository_path = request.form.get("repository_path", "").strip()
        max_issues = request.form.get("max_issues", type=int) or 5
        dry_run = "dry_run" in request.form

        # Validate GitHub repository input (required)
        if not github_repo_input:
            flash("GitHub repository name is required", "error")
            return redirect(url_for("index"))

        # Initialize GitHub utilities
        github_utils = GitHubUtils()
        repo_path = None
        temp_repo_path = None

        # Parse and validate GitHub repository format
        try:
            github_repo = github_utils.parse_github_url(github_repo_input)
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("index"))

        # Check if repository is public
        is_public = github_utils.is_public_repository(github_repo)

        # Load configuration
        config = load_config()
        config["issue_generation"]["max_issues"] = max_issues

        # Handle authentication requirements
        github_token = config["github"]["token"]
        if not is_public and not github_token:
            flash(
                f"Repository {github_repo} appears to be private but no GitHub token found. "
                "Please set GITHUB_TOKEN environment variable.",
                "error",
            )
            return redirect(url_for("index"))

        # Handle repository path - either use provided local path or clone
        if repository_path:
            # Use provided local path
            if not os.path.exists(repository_path):
                flash(
                    f"Local repository path does not exist: {repository_path}",
                    "error",
                )
                return redirect(url_for("index"))
            repo_path = repository_path
            flash(f"Using local repository at: {repository_path}", "info")
        else:
            # Clone repository to temporary location
            try:
                temp_repo_path = github_utils.clone_repository(
                    github_repo, token=github_token if not is_public else None
                )
                repo_path = temp_repo_path
                flash(
                    f"Repository cloned successfully from {github_repo}",
                    "success",
                )
            except GitHubCloneError as e:
                flash(f"Failed to clone repository: {e}", "error")
                return redirect(url_for("index"))

        # Initialize repository for analysis
        repo = Repository(repo_path)

        # Get repository analysis (use the same analysis function as CLI)
        from main import analyze_repository

        analysis = analyze_repository(repo_path, config)

        # Generate sample issues (reusing CLI logic)
        issues = generate_sample_issues(analysis, config)

        # Create GitHub issues (if not dry run)
        results = []
        if not dry_run:
            # Only validate token for issue creation if needed
            if not github_token:
                flash(
                    "GitHub token is required for creating issues. Set GITHUB_TOKEN environment variable.",
                    "error",
                )
                return redirect(url_for("index"))

            try:
                github_issue = Issue(
                    token=github_token, repository=github_repo
                )

                for issue in issues[:max_issues]:
                    try:
                        issue_url = github_issue.create_issue(
                            title=issue.title,
                            description=issue.description,
                            labels=issue.labels,
                        )
                        results.append(
                            {
                                "title": issue.title,
                                "description": issue.description,
                                "labels": issue.labels,
                                "url": issue_url,
                                "created": True,
                                "error": None,
                            }
                        )
                    except Exception as e:
                        results.append(
                            {
                                "title": issue.title,
                                "description": issue.description,
                                "labels": issue.labels,
                                "url": None,
                                "created": False,
                                "error": str(e),
                            }
                        )
            except GitHubAuthError as e:
                flash(f"GitHub authentication error: {e}", "error")
                return redirect(url_for("index"))
        else:
            # Dry run - just show what would be created
            for issue in issues[:max_issues]:
                results.append(
                    {
                        "title": issue.title,
                        "description": issue.description,
                        "labels": issue.labels,
                        "url": None,
                        "created": False,
                        "would_create": True,
                        "dry_run": True,
                        "error": None,
                    }
                )

        return render_template(
            "results.html",
            results=results,
            analysis=analysis,
            repository_path=repo_path,
            github_repo=github_repo,
            is_public=is_public,
            cloned=bool(temp_repo_path),
            dry_run=dry_run,
        )

    except (RepositoryError, GitHubCloneError) as e:
        flash(f"Repository error: {e}", "error")
        return redirect(url_for("index"))
    except Exception as e:
        flash(f"Unexpected error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        # Cleanup temporary directories
        if github_utils:
            github_utils.cleanup_temp_directories()


@app.route("/health")
def health_check():
    """Health check endpoint."""
    return jsonify({"status": "healthy", "version": __version__})


if __name__ == "__main__":
    # Get configuration from environment
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))

    print(
        f"{header('🚀 Starting Ticket-Master Web Interface')} {info(f'v{__version__}')}"
    )
    print(f"{success('🌐 Server running at')} {info(f'http://{host}:{port}')}")
    print(f"{info('💡 Press Ctrl+C to stop the server')}")

    app.run(debug=debug, host=host, port=port)
