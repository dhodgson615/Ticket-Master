import logging
import os
import subprocess
import sys
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Setup logging
logger = logging.getLogger("TicketMasterApp")
logging.basicConfig(level=logging.INFO)

# Import with fallback installation - Flask
try:
    from flask import (Flask, flash, jsonify, redirect, render_template,
                       request, url_for)
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "flask"])
    from flask import (Flask, flash, jsonify, redirect, render_template,
                       request, url_for)

# Import core modules from src
try:
    from colors import header, info, success
    from github_utils import GitHubCloneError, GitHubUtils
    from issue import GitHubAuthError, Issue
    from main import analyze_repository, generate_sample_issues, load_config
    from repository import Repository, RepositoryError
    from src import __version__
except ImportError as e:
    logger.error(f"Failed to import core modules: {e}")
    raise

app = Flask(__name__)
app.secret_key = os.getenv(
    "FLASK_SECRET_KEY", "dev-key-please-change-in-production"
)


@app.route("/")
def index() -> str:
    """Home page with repository input form.

    Returns:
        str: Rendered HTML for the index page.
    """
    return render_template("index.html", version=__version__)


@app.route("/generate", methods=["POST"])
def generate_issues():
    """Generate issues for the specified repository.

    Returns:
        Response: Flask response object with results or redirect.
    """
    github_utils = None
    try:
        github_repo_input = request.form.get("github_repo", "").strip()
        repository_path = request.form.get("repository_path", "").strip()
        max_issues = request.form.get("max_issues", type=int) or 5
        dry_run = "dry_run" in request.form

        if not github_repo_input:
            flash("GitHub repository name is required", "error")
            return redirect(url_for("index"))

        github_utils = GitHubUtils()
        repo_path = None
        temp_repo_path = None

        try:
            github_repo = github_utils.parse_github_url(github_repo_input)
        except ValueError as e:
            flash(str(e), "error")
            return redirect(url_for("index"))

        is_public = github_utils.is_public_repository(github_repo)

        config = load_config()
        config.setdefault("issue_generation", {})["max_issues"] = max_issues

        github_token = config.get("github", {}).get("token")
        if not is_public and not github_token:
            flash(
                f"Repository {github_repo} appears to be private but no GitHub token found. "
                "Please set GITHUB_TOKEN environment variable.",
                "error",
            )
            return redirect(url_for("index"))

        if repository_path:
            if not os.path.exists(repository_path):
                flash(
                    f"Local repository path does not exist: {repository_path}",
                    "error",
                )
                return redirect(url_for("index"))
            repo_path = repository_path
            flash(f"Using local repository at: {repository_path}", "info")
        else:
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

        repo = Repository(repo_path)
        analysis = analyze_repository(repo_path, config)
        issues = generate_sample_issues(analysis, config)

        results = []
        if not dry_run:
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
        logger.error(f"Repository error: {e}")
        flash(f"Repository error: {e}", "error")
        return redirect(url_for("index"))
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        flash(f"Unexpected error: {e}", "error")
        return redirect(url_for("index"))
    finally:
        if github_utils:
            github_utils.cleanup_temp_directories()


@app.route("/health")
def health_check() -> "Response":
    """Health check endpoint.

    Returns:
        Response: JSON response with health status and version.
    """
    return jsonify({"status": "healthy", "version": __version__})


if __name__ == "__main__":
    debug = os.getenv("FLASK_DEBUG", "False").lower() in ("true", "1", "yes")
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))

    print(
        f"{header('🚀 Starting Ticket-Master Web Interface')} {info(f'v{__version__}')}"
    )
    print(f"{success('🌐 Server running at')} {info(f'http://{host}:{port}')}")
    print(f"{info('💡 Press Ctrl+C to stop the server')}")

    app.run(debug=debug, host=host, port=port)
