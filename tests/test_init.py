import sys
import unittest
from pathlib import Path

# TODO: Consider using a more robust dependency management approach
# such as poetry or pipenv for better handling of dependencies.
# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


class TestInit(unittest.TestCase):
    """Test __init__.py functionality."""

    def test_version_info(self):
        """Test version information is available."""
        import src

        self.assertTrue(hasattr(src, "__version__"))
        self.assertTrue(hasattr(src, "__author__"))
        self.assertTrue(hasattr(src, "__description__"))

        self.assertIsInstance(src.__version__, str)
        self.assertIsInstance(src.__author__, str)
        self.assertIsInstance(src.__description__, str)

    def test_import_authentication(self):
        """Test Authentication imports."""
        import src

        self.assertTrue(hasattr(src, "Authentication"))
        self.assertTrue(hasattr(src, "AuthenticationError"))
        self.assertTrue(hasattr(src, "GitHubAuthError"))

    def test_import_branch(self):
        """Test Branch import."""
        import src

        self.assertTrue(hasattr(src, "Branch"))

    def test_import_commit(self):
        """Test Commit import."""
        import src

        self.assertTrue(hasattr(src, "Commit"))

    def test_import_data_scraper(self):
        """Test DataScraper import."""
        import src

        self.assertTrue(hasattr(src, "DataScraper"))

    def test_import_database(self):
        """Test Database imports."""
        import src

        self.assertTrue(hasattr(src, "Database"))
        self.assertTrue(hasattr(src, "ServerDatabase"))
        self.assertTrue(hasattr(src, "UserDatabase"))

    def test_import_github_utils(self):
        """Test GitHubUtils import."""
        import src

        self.assertTrue(hasattr(src, "GitHubUtils"))

    def test_import_issue(self):
        """Test Issue import."""
        import src

        self.assertTrue(hasattr(src, "Issue"))

    def test_import_llm(self):
        """Test LLM import."""
        import src

        self.assertTrue(hasattr(src, "LLM"))

    def test_import_ollama_tools(self):
        """Test OllamaTools import."""
        import src

        self.assertTrue(hasattr(src, "OllamaTools"))

    def test_import_pipe(self):
        """Test Pipe imports."""
        import src

        self.assertTrue(hasattr(src, "Pipe"))
        self.assertTrue(hasattr(src, "PipelineStep"))

    def test_import_prompt(self):
        """Test Prompt imports."""
        import src

        self.assertTrue(hasattr(src, "Prompt"))
        self.assertTrue(hasattr(src, "PromptTemplate"))

    def test_import_pull_request(self):
        """Test PullRequest import."""
        import src

        self.assertTrue(hasattr(src, "PullRequest"))

    def test_import_repository(self):
        """Test Repository import."""
        import src

        self.assertTrue(hasattr(src, "Repository"))

    def test_all_imports_work(self):
        """Test that all imports can be used."""
        import src

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
            self.assertTrue(hasattr(src, class_name))
            cls = getattr(src, class_name)
            self.assertTrue(callable(cls))


if __name__ == "__main__":
    unittest.main()
