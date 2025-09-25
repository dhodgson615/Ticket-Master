"""
Test module for main script functionality.

This module provides comprehensive tests for the main CLI interface
including argument parsing, configuration loading, and issue generation.
"""

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            test_config = {
                "github": {"default_labels": ["test"]},
                "issue_generation": {"max_issues": 10}
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
                {"short_hash": "def456", "summary": "Another commit"}
            ],
            "file_changes": {
                "new_files": ["test.py", "another.py"],
                "modified_files": {
                    "main.py": {"changes": 5, "insertions": 10, "deletions": 2}
                }
            },
            "analysis_summary": {
                "commit_count": 2,
                "files_modified": 6,
                "files_added": 2,
                "total_insertions": 15,
                "total_deletions": 3
            }
        }
        
        self.config = {
            "github": {"default_labels": ["enhancement", "automated"]},
            "issue_generation": {"max_issues": 5}
        }

    def test_generate_sample_issues_basic(self):
        """Test basic issue generation."""
        issues = main.generate_sample_issues(self.analysis, self.config)
        
        self.assertIsInstance(issues, list)
        self.assertLessEqual(len(issues), self.config["issue_generation"]["max_issues"])
        
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
                "total_deletions": 0
            }
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
        with patch('sys.argv', ['main.py', '--help']):
            with self.assertRaises(SystemExit) as cm:
                main.main()
            self.assertEqual(cm.exception.code, 0)  # Help should exit with 0


if __name__ == "__main__":
    unittest.main()