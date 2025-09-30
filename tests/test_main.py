import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

import main


class TestSetupLogging(unittest.TestCase):
    """Test logging setup functionality."""

    def test_setup_logging_default(self):
        """Test logging setup with default level."""
        # Test that setup_logging doesn't raise an exception
        main.setup_logging()
        self.assertTrue(True)  # If we get here, no exception was raised

    def test_setup_logging_debug(self):
        """Test logging setup with DEBUG level."""
        main.setup_logging("DEBUG")
        self.assertTrue(True)  # If we get here, no exception was raised

    def test_setup_logging_invalid(self):
        """Test logging setup with invalid level."""
        # Should fallback to INFO level without crashing
        main.setup_logging("INVALID_LEVEL")
        self.assertTrue(True)


class TestLoadConfig(unittest.TestCase):
    """Test configuration loading functionality."""

    def test_load_config_default(self):
        """Test loading default configuration."""
        config = main.load_config()

        # Verify default configuration structure
        self.assertIn("github", config)
        self.assertIn("repository", config)
        self.assertIn("issue_generation", config)
        self.assertIn("llm", config)

        # Verify default values
        self.assertEqual(config["issue_generation"]["max_issues"], 5)
        self.assertEqual(config["llm"]["provider"], "ollama")

    def test_load_config_nonexistent_file(self):
        """Test loading configuration with nonexistent file path."""
        config = main.load_config("/nonexistent/config.yaml")

        # Should return default configuration
        self.assertIn("github", config)
        self.assertEqual(config["issue_generation"]["max_issues"], 5)

    def test_load_config_with_yaml_file(self):
        """Test loading configuration from YAML file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            test_config = {
                "github": {"default_labels": ["test"]},
                "issue_generation": {"max_issues": 10},
            }
            import yaml

            yaml.dump(test_config, f)
            config_path = f.name

        try:
            config = main.load_config(config_path)

            # Should merge with defaults
            self.assertIn("github", config)
            self.assertEqual(config["github"]["default_labels"], ["test"])
            self.assertEqual(config["issue_generation"]["max_issues"], 10)
        finally:
            Path(config_path).unlink()


class TestGenerateSampleIssues(unittest.TestCase):
    """Test sample issue generation functionality."""

    def setUp(self):
        """Set up test data."""
        self.analysis = {
            "commits": [
                {"short_hash": "abc123", "summary": "Test commit"},
                {"short_hash": "def456", "summary": "Another commit"},
            ],
            "file_changes": {
                "new_files": ["test.py", "another.py"],
                "modified_files": {
                    "main.py": {"changes": 5, "insertions": 10, "deletions": 2}
                },
            },
            "analysis_summary": {
                "commit_count": 2,
                "files_modified": 6,
                "files_added": 2,
                "total_insertions": 15,
                "total_deletions": 3,
            },
        }

        self.config = {
            "github": {"default_labels": ["enhancement", "automated"]},
            "issue_generation": {"max_issues": 5},
        }

    def test_generate_sample_issues_basic(self):
        """Test basic issue generation."""
        issues = main.generate_sample_issues(self.analysis, self.config)

        self.assertIsInstance(issues, list)
        self.assertLessEqual(
            len(issues), self.config["issue_generation"]["max_issues"]
        )

        # Check that issues are Issue objects
        for issue in issues:
            self.assertIsInstance(issue, main.Issue)
            self.assertIsInstance(issue.title, str)
            self.assertIsInstance(issue.description, str)

    def test_generate_sample_issues_no_changes(self):
        """Test issue generation with no file changes."""
        empty_analysis = {
            "commits": [],
            "file_changes": {"new_files": [], "modified_files": {}},
            "analysis_summary": {
                "commit_count": 0,
                "files_modified": 0,
                "files_added": 0,
                "total_insertions": 0,
                "total_deletions": 0,
            },
        }

        issues = main.generate_sample_issues(empty_analysis, self.config)
        self.assertIsInstance(issues, list)

    def test_generate_sample_issues_respects_max_limit(self):
        """Test that issue generation respects max_issues configuration."""
        config_with_limit = self.config.copy()
        config_with_limit["issue_generation"]["max_issues"] = 1

        issues = main.generate_sample_issues(self.analysis, config_with_limit)
        self.assertLessEqual(len(issues), 1)


class TestMainFunction(unittest.TestCase):
    """Test main function execution."""

    def test_main_help(self):
        """Test main function help display."""
        with patch("sys.argv", ["main.py", "--help"]):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 0)  # Help should exit with 0


class TestPrintResultsSummary(unittest.TestCase):
    """Test print_results_summary functionality."""

    def setUp(self):
        """Set up test data."""
        self.analysis = {
            "repository_info": {
                "name": "test-repo",
                "active_branch": "main",
                "path": "/path/to/repo",
            },
            "analysis_summary": {
                "commit_count": 10,
                "files_modified": 5,
                "files_added": 3,
                "total_insertions": 100,
                "total_deletions": 20,
            },
        }

    @patch("main.print_colored")
    @patch("builtins.print")
    def test_print_results_summary_successful_issues(
        self, mock_print, mock_print_colored
    ):
        """Test print_results_summary with successful issues."""
        results = [
            {
                "title": "Test Issue 1",
                "created": True,
                "issue_number": 123,
                "url": "https://github.com/test/repo/issues/123",
            },
            {
                "title": "Test Issue 2",
                "created": True,
                "issue_number": 124,
                "url": "https://github.com/test/repo/issues/124",
            },
        ]

        main.print_results_summary(results, self.analysis)

        # Verify print_colored was called for headers
        mock_print_colored.assert_called()

        # Verify regular print was called with repository info
        mock_print.assert_called()

    @patch("main.print_colored")
    @patch("builtins.print")
    def test_print_results_summary_failed_issues(
        self, mock_print, mock_print_colored
    ):
        """Test print_results_summary with failed issues."""
        results = [{"title": "Failed Issue", "error": "Authentication failed"}]

        main.print_results_summary(results, self.analysis)

        mock_print_colored.assert_called()
        mock_print.assert_called()

    @patch("main.print_colored")
    @patch("builtins.print")
    def test_print_results_summary_dry_run(
        self, mock_print, mock_print_colored
    ):
        """Test print_results_summary with dry run results."""
        results = [
            {"title": "Dry Run Issue", "would_create": True, "dry_run": True}
        ]

        main.print_results_summary(results, self.analysis)

        mock_print_colored.assert_called()
        mock_print.assert_called()

    @patch("main.print_colored")
    @patch("builtins.print")
    def test_print_results_summary_long_title(
        self, mock_print, mock_print_colored
    ):
        """Test print_results_summary with long issue title."""
        results = [
            {
                "title": "This is a very long issue title that should be truncated to fit within the summary display format",
                "created": True,
                "issue_number": 123,
                "url": "https://github.com/test/repo/issues/123",
            }
        ]

        main.print_results_summary(results, self.analysis)

        mock_print_colored.assert_called()
        mock_print.assert_called()

    @patch("main.print_colored")
    @patch("builtins.print")
    def test_print_results_summary_with_warnings(
        self, mock_print, mock_print_colored
    ):
        """Test print_results_summary with validation warnings."""
        results = [
            {
                "title": "Issue with warnings",
                "created": True,
                "issue_number": 123,
                "url": "https://github.com/test/repo/issues/123",
                "validation_warnings": ["Title too short", "Missing labels"],
            }
        ]

        main.print_results_summary(results, self.analysis)

        mock_print_colored.assert_called()
        mock_print.assert_called()


class TestValidateConfigCommand(unittest.TestCase):
    """Test validate_config_command functionality."""

    @patch("main.load_config")
    @patch("builtins.print")
    def test_validate_config_command_valid_config(
        self, mock_print, mock_load_config
    ):
        """Test validate_config_command with valid configuration."""
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
        }

        result = main.validate_config_command()

        self.assertEqual(result, 0)
        mock_load_config.assert_called_once()
        mock_print.assert_called()

    @patch("main.load_config")
    @patch("builtins.print")
    def test_validate_config_command_with_path(
        self, mock_print, mock_load_config
    ):
        """Test validate_config_command with specific config path."""
        mock_load_config.return_value = {
            "github": {"token": "test_token"},
            "issue_generation": {"max_issues": 5},
        }

        result = main.validate_config_command("/path/to/config.yaml")

        self.assertEqual(result, 0)
        mock_load_config.assert_called_once_with("/path/to/config.yaml")
        mock_print.assert_called()

    @patch("main.load_config")
    @patch("builtins.print")
    def test_validate_config_command_missing_required_fields(
        self, mock_print, mock_load_config
    ):
        """Test validate_config_command with missing required fields."""
        # Return config missing some required fields
        mock_load_config.return_value = {"github": {}}  # Missing token

        result = main.validate_config_command()

        # Should return 1 (error) for invalid configuration
        self.assertEqual(result, 1)
        mock_load_config.assert_called_once()
        mock_print.assert_called()


class TestAnalyzeRepository(unittest.TestCase):
    """Test analyze_repository functionality."""

    @patch("main.Repository")
    def test_analyze_repository_success(self, mock_repository):
        """Test successful repository analysis."""
        mock_repo_instance = Mock()
        mock_repo_instance.analyze.return_value = {
            "commits": [],
            "file_changes": {"new_files": [], "modified_files": {}},
            "summary": {"commit_count": 0},
        }
        mock_repository.return_value = mock_repo_instance

        config = {"repository": {"max_commits": 100}}
        result = main.analyze_repository("/path/to/repo", config)

        self.assertIsInstance(result, dict)
        mock_repository.assert_called_once_with("/path/to/repo")
        mock_repo_instance.analyze.assert_called_once()

    @patch("main.Repository")
    def test_analyze_repository_with_exception(self, mock_repository):
        """Test repository analysis with exception."""
        mock_repository.side_effect = Exception("Repository error")

        config = {"repository": {"max_commits": 100}}

        with self.assertRaises(Exception):
            main.analyze_repository("/path/to/repo", config)


class TestGenerateIssuesWithLLM(unittest.TestCase):
    """Test generate_issues_with_llm functionality."""

    def setUp(self):
        """Set up test data."""
        self.analysis = {
            "commits": [],
            "file_changes": {"new_files": [], "modified_files": {}},
            "summary": {"commit_count": 0},
        }

    @patch("main.generate_issues_with_standard_llm")
    def test_generate_issues_with_llm_success(self, mock_generate_standard):
        """Test successful LLM issue generation."""
        config = {"llm": {"provider": "ollama"}}
        mock_issue = Mock()
        mock_issue.title = "Test Issue"
        mock_generate_standard.return_value = [mock_issue]

        result = main.generate_issues_with_llm(self.analysis, config)

        self.assertEqual(len(result), 1)
        mock_generate_standard.assert_called_once_with(self.analysis, config)

    @patch("main.generate_sample_issues")
    @patch("main.generate_issues_with_standard_llm")
    def test_generate_issues_with_llm_fallback(
        self, mock_generate_standard, mock_generate_sample
    ):
        """Test LLM issue generation fallback to samples."""
        config = {"llm": {"provider": "ollama"}}
        mock_generate_standard.side_effect = Exception("LLM error")

        mock_issue = Mock()
        mock_issue.title = "Sample Issue"
        mock_generate_sample.return_value = [mock_issue]

        result = main.generate_issues_with_llm(self.analysis, config)

        self.assertEqual(len(result), 1)
        mock_generate_standard.assert_called_once()
        mock_generate_sample.assert_called_once()


class TestCreateIssuesOnGitHub(unittest.TestCase):
    """Test create_issues_on_github functionality."""

    def setUp(self):
        """Set up test data."""
        self.mock_issue = Mock()
        self.mock_issue.title = "Test Issue"
        self.mock_issue.description = "Test Description"
        self.mock_issue.labels = ["bug", "enhancement"]

    @patch("main.Issue")
    def test_create_issues_on_github_dry_run(self, mock_issue_class):
        """Test creating issues in dry run mode."""
        config = {"github": {"token": "test_token"}}
        issues = [self.mock_issue]

        results = main.create_issues_on_github(
            issues, "test/repo", config, dry_run=True
        )

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["dry_run"])
        self.assertTrue(results[0]["would_create"])
        # Should not actually create issues
        mock_issue_class.assert_not_called()

    @patch("main.Issue")
    def test_create_issues_on_github_success(self, mock_issue_class):
        """Test successful issue creation."""
        config = {"github": {"token": "test_token"}}
        issues = [self.mock_issue]

        mock_github_issue = Mock()
        mock_github_issue.create_issue.return_value = {
            "number": 123,
            "html_url": "https://github.com/test/repo/issues/123",
        }
        mock_issue_class.return_value = mock_github_issue

        results = main.create_issues_on_github(
            issues, "test/repo", config, dry_run=False
        )

        self.assertEqual(len(results), 1)
        self.assertTrue(results[0]["created"])
        self.assertEqual(results[0]["issue_number"], 123)
        mock_issue_class.assert_called_once()

    @patch("main.Issue")
    def test_create_issues_on_github_failure(self, mock_issue_class):
        """Test issue creation failure."""
        config = {"github": {"token": "test_token"}}
        issues = [self.mock_issue]

        mock_github_issue = Mock()
        mock_github_issue.create_issue.side_effect = Exception(
            "Creation failed"
        )
        mock_issue_class.return_value = mock_github_issue

        results = main.create_issues_on_github(
            issues, "test/repo", config, dry_run=False
        )

        self.assertEqual(len(results), 1)
        self.assertIn("error", results[0])
        self.assertEqual(results[0]["error"], "Creation failed")


if __name__ == "__main__":
    unittest.main()
