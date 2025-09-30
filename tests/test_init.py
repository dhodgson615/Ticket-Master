"""
Test module for ticket_master_consolidated module.

This module tests the consolidated module and import behavior.
"""

import sys
import unittest
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestConsolidated(unittest.TestCase):
    """Test ticket_master_consolidated functionality."""

    def test_version_info(self):
        """Test version information is available."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "__version__"))
        self.assertTrue(hasattr(ticket_master_consolidated, "__author__"))
        self.assertTrue(hasattr(ticket_master_consolidated, "__description__"))

        self.assertIsInstance(ticket_master_consolidated.__version__, str)
        self.assertIsInstance(ticket_master_consolidated.__author__, str)
        self.assertIsInstance(ticket_master_consolidated.__description__, str)

    def test_import_authentication(self):
        """Test Authentication imports."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "Authentication"))
        self.assertTrue(
            hasattr(ticket_master_consolidated, "AuthenticationError")
        )
        self.assertTrue(hasattr(ticket_master_consolidated, "GitHubAuthError"))

    def test_import_branch(self):
        """Test Branch import."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "Branch"))

    def test_import_commit(self):
        """Test Commit import."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "Commit"))

    def test_import_data_scraper(self):
        """Test DataScraper import."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "DataScraper"))

    def test_import_database(self):
        """Test Database imports."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "Database"))
        self.assertTrue(hasattr(ticket_master_consolidated, "ServerDatabase"))
        self.assertTrue(hasattr(ticket_master_consolidated, "UserDatabase"))

    def test_import_github_utils(self):
        """Test GitHubUtils import."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "GitHubUtils"))

    def test_import_issue(self):
        """Test Issue import."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "Issue"))

    def test_import_llm(self):
        """Test LLM import."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "LLM"))

    def test_import_pipe(self):
        """Test Pipe imports."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "Pipe"))
        self.assertTrue(hasattr(ticket_master_consolidated, "PipelineStep"))

    def test_import_prompt(self):
        """Test Prompt imports."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "Prompt"))
        self.assertTrue(hasattr(ticket_master_consolidated, "PromptTemplate"))

    def test_import_pull_request(self):
        """Test PullRequest import."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "PullRequest"))

    def test_import_repository(self):
        """Test Repository import."""
        import ticket_master_consolidated

        self.assertTrue(hasattr(ticket_master_consolidated, "Repository"))

    def test_all_imports_work(self):
        """Test that all imports can be used."""
        import ticket_master_consolidated

        # Test that we can access classes without errors
        classes_to_test = [
            "Authentication",
            "Branch",
            "Commit",
            "DataScraper",
            "Database",
            "GitHubUtils",
            "Issue",
            "LLM",
            "Pipe",
            "Prompt",
            "PullRequest",
            "Repository",
        ]

        for class_name in classes_to_test:
            self.assertTrue(hasattr(ticket_master_consolidated, class_name))
            cls = getattr(ticket_master_consolidated, class_name)
            self.assertTrue(callable(cls))


if __name__ == "__main__":
    unittest.main()
