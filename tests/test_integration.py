import tempfile
import unittest
from pathlib import Path

from main import (create_issues_on_github, generate_issues_with_llm,
                  generate_sample_issues, load_config)


class TestEndToEndIntegration(unittest.TestCase):
    """Test complete end-to-end functionality."""

    def setUp(self):
        """Set up test environment."""
        self.test_config = {
            "github": {
                "token": "dummy_token",
                "default_labels": ["automated", "test"],
            },
            "repository": {
                "max_commits": 5,
                "ignore_patterns": [".git", "__pycache__"],
            },
            "issue_generation": {
                "max_issues": 2,
                "min_description_length": 50,
            },
            "llm": {
                "provider": "mock",
                "model": "test-model",
                "temperature": 0.7,
                "max_tokens": 1000,
            },
        }

    def test_sample_issue_generation_pipeline(self):
        """Test complete pipeline using sample issue generation."""
        # Create minimal analysis data
        analysis = {
            "repository_info": {"name": "test-repo", "active_branch": "main"},
            "commits": [
                {
                    "hash": "abc123",
                    "short_hash": "abc123",
                    "summary": "Test commit",
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                    },
                    "committer": {
                        "name": "Test User",
                        "email": "test@example.com",
                    },
                    "message": "Test commit message",
                    "date": "2023-01-01T00:00:00",
                    "files_changed": 1,
                    "insertions": 10,
                    "deletions": 5,
                }
            ],
            "file_changes": {
                "modified_files": {},
                "new_files": [],
                "deleted_files": [],
                "renamed_files": [],
                "summary": {
                    "total_files": 1,
                    "total_insertions": 10,
                    "total_deletions": 5,
                },
            },
            "analysis_summary": {
                "commit_count": 1,
                "files_modified": 1,
                "files_added": 0,
                "total_insertions": 10,
                "total_deletions": 5,
            },
        }

        # Test sample issue generation
        issues = generate_sample_issues(analysis, self.test_config)

        # Verify results
        self.assertIsInstance(issues, list)
        self.assertGreater(len(issues), 0)

        # Check first issue
        first_issue = issues[0]
        self.assertIsNotNone(first_issue.title)
        self.assertIsNotNone(first_issue.description)
        self.assertIsInstance(first_issue.labels, list)
        self.assertIn("automated", first_issue.labels)

    def test_llm_issue_generation_pipeline(self):
        """Test complete pipeline using LLM issue generation."""
        # Create minimal analysis data
        analysis = {
            "repository_info": {"name": "test-repo", "active_branch": "main"},
            "commits": [
                {
                    "hash": "abc123",
                    "short_hash": "abc123",
                    "summary": "Add new feature",
                    "author": {
                        "name": "Test User",
                        "email": "test@example.com",
                    },
                    "committer": {
                        "name": "Test User",
                        "email": "test@example.com",
                    },
                    "message": "Add new feature implementation",
                    "date": "2023-01-01T00:00:00",
                    "files_changed": 3,
                    "insertions": 50,
                    "deletions": 10,
                }
            ],
            "file_changes": {
                "modified_files": {
                    "src/main.py": {
                        "changes": 2,
                        "insertions": 30,
                        "deletions": 5,
                        "commits": ["abc123"],
                    }
                },
                "new_files": ["src/feature.py"],
                "deleted_files": [],
                "renamed_files": [],
                "summary": {
                    "total_files": 2,
                    "total_insertions": 50,
                    "total_deletions": 10,
                },
            },
            "analysis_summary": {
                "commit_count": 1,
                "files_modified": 1,
                "files_added": 1,
                "total_insertions": 50,
                "total_deletions": 10,
            },
        }

        # Test LLM issue generation
        issues = generate_issues_with_llm(analysis, self.test_config)

        # Verify results
        self.assertIsInstance(issues, list)
        self.assertGreater(len(issues), 0)
        self.assertLessEqual(
            len(issues), self.test_config["issue_generation"]["max_issues"]
        )

        # Check issue structure
        for issue in issues:
            self.assertIsNotNone(issue.title)
            self.assertIsNotNone(issue.description)
            self.assertTrue(
                len(issue.description)
                >= self.test_config["issue_generation"][
                    "min_description_length"
                ]
            )
            self.assertIsInstance(issue.labels, list)

    def test_config_loading_with_mock_provider(self):
        """Test configuration loading with mock provider."""
        # Create temporary config file
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".yaml", delete=False
        ) as f:
            f.write(
                """
github:
  token: null
  default_labels: ["test", "automated"]

llm:
  provider: "mock"
  model: "test-model"

issue_generation:
  max_issues: 3
"""
            )
            config_path = f.name

        try:
            # Load config
            config = load_config(config_path)

            # Verify config structure
            self.assertIn("github", config)
            self.assertIn("llm", config)
            self.assertIn("issue_generation", config)

            # Verify mock provider config
            self.assertEqual(config["llm"]["provider"], "mock")
            self.assertEqual(config["llm"]["model"], "test-model")
            self.assertEqual(config["issue_generation"]["max_issues"], 3)

        finally:
            # Clean up
            Path(config_path).unlink()

    def test_dry_run_issue_processing(self):
        """Test dry run issue processing workflow."""
        from ticket_master import Issue

        # Create test issues
        issues = [
            Issue(
                title="Test Issue 1",
                description="This is a test issue for dry run processing.",
                labels=["test", "automated"],
            ),
            Issue(
                title="Test Issue 2",
                description="This is another test issue with longer description for validation.",
                labels=["test", "enhancement"],
            ),
        ]

        # Test dry run processing
        results = create_issues_on_github(
            issues=issues,
            repo_name="test/repo",
            config=self.test_config,
            dry_run=True,
        )

        # Verify results
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), len(issues))

        for result in results:
            self.assertIn("dry_run", result)
            self.assertIn("title", result)
            self.assertTrue(result["dry_run"])
            self.assertIn("would_create", result)


if __name__ == "__main__":
    unittest.main()
