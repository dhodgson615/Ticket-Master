"""
Test module for data scraper class: DataScraper.

This module provides comprehensive tests for data scraper functionality
including repository analysis, file structure scanning, and content analysis.
"""

import sys
import unittest
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_scraper import DataScraper, DataScraperError


class TestDataScraper(unittest.TestCase):
    """Test DataScraper functionality."""

    def setUp(self):
        """Set up test data scraper with current repository."""
        # Use the current repository for testing
        self.repo_path = Path(__file__).parent.parent
        self.scraper = DataScraper(self.repo_path, use_cache=False)

    def test_init_valid_repo(self):
        """Test DataScraper initialization with valid repository."""
        self.assertEqual(self.scraper.repo_path, self.repo_path.resolve())
        self.assertIsNotNone(self.scraper.repository)

    def test_init_invalid_repo(self):
        """Test DataScraper initialization with invalid repository."""
        with self.assertRaises(DataScraperError):
            DataScraper("/nonexistent/path")

    def test_scrape_repository_info(self):
        """Test repository information scraping."""
        info = self.scraper.scrape_repository_info()

        self.assertIn("absolute_path", info)
        self.assertIn("size_info", info)
        self.assertEqual(info["absolute_path"], str(self.repo_path.resolve()))

    def test_scrape_file_structure(self):
        """Test file structure analysis."""
        structure = self.scraper.scrape_file_structure()

        self.assertIn("total_files", structure)
        self.assertIn("file_types", structure)
        self.assertIn("directories", structure)
        self.assertGreater(structure["total_files"], 0)

    def test_scrape_content_analysis(self):
        """Test content analysis."""
        analysis = self.scraper.scrape_content_analysis()

        self.assertIn("programming_languages", analysis)
        self.assertIn("configuration_files", analysis)

        # Should detect Python files
        self.assertIn("Python", analysis["programming_languages"])


if __name__ == "__main__":
    unittest.main()
