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

from flask import (Flask, render_template, request, flash,  # noqa: E402
                   redirect, url_for, jsonify)

from ticket_master import Repository, __version__  # noqa: E402
from ticket_master.issue import Issue, GitHubAuthError  # noqa: E402
from ticket_master.repository import RepositoryError  # noqa: E402

# Import the main CLI functions to reuse logic
from main import load_config, generate_sample_issues  # noqa: E402

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY',
                           'dev-key-please-change-in-production')


@app.route('/')
def index():
    """Home page with repository input form."""
    return render_template('index.html', version=__version__)


@app.route('/generate', methods=['POST'])
def generate_issues():
    """Generate issues for the specified repository."""
    try:
        # Get form data
        repository_path = request.form.get('repository_path', '').strip()
        github_repo = request.form.get('github_repo', '').strip()
        max_issues = request.form.get('max_issues', type=int) or 5
        dry_run = 'dry_run' in request.form

        # Validate inputs
        if not repository_path:
            flash('Repository path is required', 'error')
            return redirect(url_for('index'))

        if not github_repo:
            flash('GitHub repository name is required', 'error')
            return redirect(url_for('index'))

        if not os.path.exists(repository_path):
            flash(f'Repository path does not exist: {repository_path}',
                  'error')
            return redirect(url_for('index'))

        # Load configuration
        config = load_config()
        config['issue_generation']['max_issues'] = max_issues

        # Validate GitHub token
        if not config['github']['token']:
            flash('GitHub token not found. Please set GITHUB_TOKEN '
                  'environment variable.', 'error')
            return redirect(url_for('index'))

        # Initialize repository
        repo = Repository(repository_path)

        # Get repository analysis
        analysis = repo.get_repository_info()

        # Generate sample issues (reusing CLI logic)
        issues = generate_sample_issues(analysis, config)

        # Create GitHub issues (if not dry run)
        results = []
        if not dry_run:
            try:
                github_issue = Issue(
                    token=config['github']['token'],
                    repository=github_repo
                )

                for issue in issues[:max_issues]:
                    try:
                        issue_url = github_issue.create_issue(
                            title=issue.title,
                            description=issue.description,
                            labels=issue.labels
                        )
                        results.append({
                            'title': issue.title,
                            'description': issue.description,
                            'labels': issue.labels,
                            'url': issue_url,
                            'created': True,
                            'error': None
                        })
                    except Exception as e:
                        results.append({
                            'title': issue.title,
                            'description': issue.description,
                            'labels': issue.labels,
                            'url': None,
                            'created': False,
                            'error': str(e)
                        })
            except GitHubAuthError as e:
                flash(f'GitHub authentication error: {e}', 'error')
                return redirect(url_for('index'))
        else:
            # Dry run - just show what would be created
            for issue in issues[:max_issues]:
                results.append({
                    'title': issue.title,
                    'description': issue.description,
                    'labels': issue.labels,
                    'url': None,
                    'created': False,
                    'would_create': True,
                    'dry_run': True,
                    'error': None
                })

        return render_template('results.html',
                               results=results,
                               analysis=analysis,
                               repository_path=repository_path,
                               github_repo=github_repo,
                               dry_run=dry_run)

    except RepositoryError as e:
        flash(f'Repository error: {e}', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        flash(f'Unexpected error: {e}', 'error')
        return redirect(url_for('index'))


@app.route('/health')
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy',
        'version': __version__
    })


if __name__ == '__main__':
    # Get configuration from environment
    debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    host = os.getenv('FLASK_HOST', '127.0.0.1')
    port = int(os.getenv('FLASK_PORT', '5000'))

    print(f"Starting Ticket-Master Web Interface v{__version__}")
    print(f"Server running at http://{host}:{port}")
    print("Press Ctrl+C to stop the server")

    app.run(debug=debug, host=host, port=port)
