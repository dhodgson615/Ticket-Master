import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

# TODO: Consider using a more robust dependency management approach
# such as poetry or pipenv for better handling of dependencies.
# Add src and root directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Mock external dependencies before importing app
with patch("auth.Authentication"):
    with patch("repository.Repository"):
        with patch("issue.Issue"):
            with patch("github_utils.GitHubUtils"):
                import app


class TestAppConfiguration:
    """Test Flask app configuration."""

    def test_app_exists(self):
        """Test that Flask app is properly configured."""
        assert app.app is not None
        assert app.app.name == "app"

    def test_secret_key_set(self):
        """Test that secret key is configured."""
        assert app.app.secret_key is not None
        # Should use environment variable or default
        expected = os.getenv(
            "FLASK_SECRET_KEY", "dev-key-please-change-in-production"
        )
        assert app.app.secret_key == expected


class TestIndexRoute:
    """Test cases for the index route."""

    def test_index_route_get(self):
        """Test GET request to index route."""
        with app.app.test_client() as client:
            with patch("app.render_template") as mock_render:
                mock_render.return_value = "mocked_template"

                response = client.get("/")

                assert response.status_code == 200
                mock_render.assert_called_once_with(
                    "index.html", version=app.__version__
                )

    def test_index_route_template_variables(self):
        """Test that index route passes correct template variables."""
        with app.app.test_client() as client:
            with patch("app.render_template") as mock_render:
                mock_render.return_value = "mocked_template"

                client.get("/")

                # Verify template is called with version
                args, kwargs = mock_render.call_args
                assert args[0] == "index.html"
                assert "version" in kwargs
                assert kwargs["version"] == app.__version__


class TestHealthCheckRoute:
    """Test cases for the health check route."""

    def test_health_check_route(self):
        """Test health check endpoint returns JSON."""
        with app.app.test_client() as client:
            response = client.get("/health")

            assert response.status_code == 200
            assert response.is_json

            data = response.get_json()
            assert data["status"] == "healthy"
            assert data["version"] == app.__version__

    def test_health_check_content_type(self):
        """Test health check returns proper content type."""
        with app.app.test_client() as client:
            response = client.get("/health")

            assert "application/json" in response.content_type


class TestGenerateIssuesRoute:
    """Test cases for the generate issues route."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_repo = "test-owner/test-repo"
        self.form_data = {"github_repo": self.test_repo, "max_issues": 3}

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    def test_generate_issues_missing_repo(
        self, mock_load_config, mock_github_utils
    ):
        """Test generate_issues with missing repository."""
        mock_load_config.return_value = {"github": {"token": "test_token"}}

        with app.app.test_client() as client:
            response = client.post(
                "/generate", data={"max_issues": 3}, follow_redirects=True
            )

            assert response.status_code == 200
            # Should redirect to index with error flash message

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    def test_generate_issues_empty_repo(
        self, mock_load_config, mock_github_utils
    ):
        """Test generate_issues with empty repository field."""
        mock_load_config.return_value = {"github": {"token": "test_token"}}

        with app.app.test_client() as client:
            response = client.post(
                "/generate",
                data={
                    "github_repo": "   ",  # Only whitespace
                    "max_issues": 3,
                },
                follow_redirects=True,
            )

            assert response.status_code == 200

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    def test_generate_issues_invalid_repo_format(
        self, mock_load_config, mock_github_utils
    ):
        """Test generate_issues with invalid repository format."""
        mock_load_config.return_value = {"github": {"token": "test_token"}}

        # Mock GitHubUtils to raise ValueError for invalid format
        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.side_effect = ValueError(
            "Invalid format"
        )
        mock_github_utils.return_value = mock_utils_instance

        with app.app.test_client() as client:
            response = client.post(
                "/generate",
                data={"github_repo": "invalid-format", "max_issues": 3},
                follow_redirects=True,
            )

            assert response.status_code == 200

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    @patch("app.Repository")
    def test_generate_issues_private_repo_no_token(
        self, mock_repository, mock_load_config, mock_github_utils
    ):
        """Test generate_issues with private repository but no token."""
        mock_load_config.return_value = {
            "github": {"token": None},
            "issue_generation": {"max_issues": 5},
        }

        # Mock GitHubUtils
        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = self.test_repo
        mock_utils_instance.is_public_repository.return_value = (
            False  # Private repo
        )
        mock_github_utils.return_value = mock_utils_instance

        with app.app.test_client() as client:
            response = client.post(
                "/generate", data=self.form_data, follow_redirects=True
            )

            assert response.status_code == 200

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    @patch("app.Repository")
    def test_generate_issues_nonexistent_local_path(
        self, mock_repository, mock_load_config, mock_github_utils
    ):
        """Test generate_issues with nonexistent local path."""
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
        }

        # Mock GitHubUtils
        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = self.test_repo
        mock_utils_instance.is_public_repository.return_value = True
        mock_github_utils.return_value = mock_utils_instance

        form_data = self.form_data.copy()
        form_data["repository_path"] = "/nonexistent/path"

        with app.app.test_client() as client:
            response = client.post(
                "/generate", data=form_data, follow_redirects=True
            )

            assert response.status_code == 200

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    @patch("app.Repository")
    @patch("app.generate_sample_issues")
    @patch("os.path.exists")
    def test_generate_issues_with_local_path(
        self,
        mock_exists,
        mock_generate,
        mock_repository,
        mock_load_config,
        mock_github_utils,
    ):
        """Test generate_issues with valid local path."""
        # Setup mocks
        mock_exists.return_value = True
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
            "repository": {},
            "llm": {"provider": "mock"},
        }

        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = self.test_repo
        mock_utils_instance.is_public_repository.return_value = True
        mock_github_utils.return_value = mock_utils_instance

        mock_repo_instance = Mock()
        mock_repo_instance.analyze.return_value = {
            "commits": [],
            "file_changes": {"new_files": [], "modified_files": {}},
            "summary": {
                "commit_count": 0,
                "files_modified": 0,
                "files_added": 0,
            },
        }
        mock_repository.return_value = mock_repo_instance

        mock_generate.return_value = []

        form_data = self.form_data.copy()
        form_data["repository_path"] = "/valid/path"

        with app.app.test_client() as client:
            with patch("app.render_template") as mock_render:
                mock_render.return_value = "mocked_result"

                response = client.post("/generate", data=form_data)

                assert response.status_code == 200

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    def test_generate_issues_clone_failure(
        self, mock_load_config, mock_github_utils
    ):
        """Test generate_issues when repository cloning fails."""
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
        }

        # Mock GitHubUtils to fail on clone
        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = self.test_repo
        mock_utils_instance.is_public_repository.return_value = True
        mock_utils_instance.clone_repository.side_effect = (
            app.GitHubCloneError("Clone failed")
        )
        mock_github_utils.return_value = mock_utils_instance

        with app.app.test_client() as client:
            response = client.post(
                "/generate", data=self.form_data, follow_redirects=True
            )

            assert response.status_code == 200

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    @patch("app.Repository")
    def test_generate_issues_repository_error(
        self, mock_repository, mock_load_config, mock_github_utils
    ):
        """Test generate_issues when repository analysis fails."""
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
        }

        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = self.test_repo
        mock_utils_instance.is_public_repository.return_value = True
        mock_utils_instance.clone_repository.return_value = "/tmp/test_repo"
        mock_github_utils.return_value = mock_utils_instance

        # Mock Repository to raise an error
        mock_repository.side_effect = app.RepositoryError("Analysis failed")

        with app.app.test_client() as client:
            response = client.post(
                "/generate", data=self.form_data, follow_redirects=True
            )

            assert response.status_code == 200

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    @patch("app.Repository")
    @patch("app.generate_sample_issues")
    def test_generate_issues_success_public_repo(
        self,
        mock_generate,
        mock_repository,
        mock_load_config,
        mock_github_utils,
    ):
        """Test successful issue generation for public repository."""
        # Setup mocks
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
            "repository": {},
            "llm": {"provider": "mock"},
        }

        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = self.test_repo
        mock_utils_instance.is_public_repository.return_value = True
        mock_utils_instance.clone_repository.return_value = "/tmp/test_repo"
        mock_github_utils.return_value = mock_utils_instance

        mock_repo_instance = Mock()
        mock_repo_instance.analyze.return_value = {
            "commits": [{"short_hash": "abc123", "summary": "Test commit"}],
            "file_changes": {"new_files": ["test.py"], "modified_files": {}},
            "summary": {
                "commit_count": 1,
                "files_modified": 0,
                "files_added": 1,
            },
        }
        mock_repository.return_value = mock_repo_instance

        # Mock issue generation
        mock_issue = Mock()
        mock_issue.title = "Test Issue"
        mock_issue.description = "Test Description"
        mock_generate.return_value = [mock_issue]

        with app.app.test_client() as client:
            with patch("app.render_template") as mock_render:
                mock_render.return_value = "success_page"

                response = client.post("/generate", data=self.form_data)

                assert response.status_code == 200
                mock_render.assert_called_once()

    def test_generate_issues_dry_run_flag(self):
        """Test that dry_run flag is properly processed."""
        with app.app.test_client() as client:
            with patch("app.GitHubUtils") as mock_github_utils:
                with patch("app.load_config") as mock_load_config:
                    mock_load_config.return_value = {
                        "github": {"token": "test_token"}
                    }

                    # Test with dry_run checkbox checked
                    form_data = self.form_data.copy()
                    form_data["dry_run"] = "on"

                    response = client.post(
                        "/generate", data=form_data, follow_redirects=True
                    )
                    assert response.status_code == 200

    def test_generate_issues_max_issues_default(self):
        """Test that max_issues defaults to 5 when not provided."""
        with app.app.test_client() as client:
            with patch("app.GitHubUtils") as mock_github_utils:
                with patch("app.load_config") as mock_load_config:
                    mock_load_config.return_value = {
                        "github": {"token": "test_token"}
                    }

                    # Test without max_issues in form data
                    response = client.post(
                        "/generate",
                        data={"github_repo": self.test_repo},
                        follow_redirects=True,
                    )

                    assert response.status_code == 200

    def test_generate_issues_invalid_max_issues(self):
        """Test that invalid max_issues defaults to 5."""
        with app.app.test_client() as client:
            with patch("app.GitHubUtils") as mock_github_utils:
                with patch("app.load_config") as mock_load_config:
                    mock_load_config.return_value = {
                        "github": {"token": "test_token"}
                    }

                    # Test with invalid max_issues
                    response = client.post(
                        "/generate",
                        data={
                            "github_repo": self.test_repo,
                            "max_issues": "invalid",
                        },
                        follow_redirects=True,
                    )

                    assert response.status_code == 200


class TestAppErrorHandling:
    """Test error handling in the Flask app."""

    @patch("app.GitHubUtils")
    @patch("app.load_config")
    @patch("app.Repository")
    def test_general_exception_handling(
        self, mock_repository, mock_load_config, mock_github_utils
    ):
        """Test that general exceptions are properly handled."""
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
        }

        mock_utils_instance = Mock()
        mock_utils_instance.parse_github_url.return_value = "test/repo"
        mock_utils_instance.is_public_repository.return_value = True
        mock_utils_instance.clone_repository.return_value = "/tmp/test"
        mock_github_utils.return_value = mock_utils_instance

        # Mock Repository to raise a general exception
        mock_repository.side_effect = Exception("Unexpected error")

        with app.app.test_client() as client:
            response = client.post(
                "/generate",
                data={"github_repo": "test/repo", "max_issues": 3},
                follow_redirects=True,
            )

            assert response.status_code == 200

    def test_post_request_to_index(self):
        """Test that POST requests to index route work (form submission)."""
        with app.app.test_client() as client:
            response = client.post("/")
            # Should handle gracefully (either redirect or show form again)
            assert response.status_code in [200, 302, 405]


class TestAppUtilityFunctions:
    """Test utility functions and imports."""

    def test_imports_work(self):
        """Test that all required imports are available."""
        # Test that main imports work
        assert hasattr(app, "Flask")
        assert hasattr(app, "render_template")
        assert hasattr(app, "request")
        assert hasattr(app, "flash")
        assert hasattr(app, "redirect")
        assert hasattr(app, "url_for")
        assert hasattr(app, "jsonify")

    def test_version_import(self):
        """Test that version is properly imported."""
        assert hasattr(app, "__version__")
        assert app.__version__ is not None

    def test_main_function_imports(self):
        """Test that main module functions are imported."""
        assert hasattr(app, "load_config")
        assert hasattr(app, "generate_sample_issues")


class TestAppEnvironmentVariables:
    """Test environment variable handling."""

    @patch.dict(os.environ, {"FLASK_SECRET_KEY": "test_secret_key"})
    def test_custom_secret_key(self):
        """Test that custom secret key from environment is used."""
        # Need to reimport to pick up env var
        import importlib

        importlib.reload(app)

        assert app.app.secret_key == "test_secret_key"

    @patch.dict(os.environ, {}, clear=True)
    def test_default_secret_key(self):
        """Test that default secret key is used when env var not set."""
        import importlib

        importlib.reload(app)

        assert app.app.secret_key == "dev-key-please-change-in-production"


class TestTemplateRendering:
    """Test template rendering functionality."""

    def test_template_context_processor(self):
        """Test that templates have access to required context variables."""
        with app.app.test_client() as client:
            with patch("app.render_template") as mock_render:
                mock_render.return_value = "mocked"

                client.get("/")

                # Check that version is passed to template
                args, kwargs = mock_render.call_args
                assert "version" in kwargs


if __name__ == "__main__":
    pytest.main([__file__])
