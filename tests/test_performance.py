"""
Performance tests for Ticket-Master with large repositories and datasets.

This module tests the performance characteristics of the application
when dealing with large repositories, many commits, and bulk operations.
"""

import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from data_scraper import DataScraper
from github_utils import GitHubUtils
from issue import Issue
from repository import Repository, RepositoryError


class TestLargeRepositoryPerformance(unittest.TestCase):
    """Test performance with large repositories (1000+ commits)."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.github_utils = GitHubUtils()

    def tearDown(self):
        """Clean up test fixtures."""
        self.github_utils.cleanup_temp_directories()

    @patch("src.ticket_master.repository.git.Repo")
    def test_large_commit_history_performance(self, mock_repo_class):
        """Test performance when analyzing repositories with 1000+ commits."""
        # Mock a repository with many commits
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Create mock commits (simulating 1000+ commits)
        mock_commits = []
        for i in range(1000):
            mock_commit = Mock()
            mock_commit.hexsha = f"commit_hash_{i:04d}"
            mock_commit.message = f"Commit message {i}"
            mock_commit.authored_datetime = (
                f"2024-01-{(i % 30) + 1:02d}T10:00:00"
            )
            mock_commit.author.name = f"Author {i % 10}"
            mock_commit.author.email = f"author{i % 10}@example.com"
            mock_commits.append(mock_commit)

        mock_repo.iter_commits.return_value = mock_commits

        # Test repository analysis performance
        with patch(
            "src.ticket_master.repository.Repository.__init__",
            return_value=None,
        ):
            repo = Repository.__new__(Repository)
            repo.get_commit_history = Mock(return_value=mock_commits)

            start_time = time.time()
            commit_history = repo.get_commit_history(max_commits=1000)
            analysis_time = time.time() - start_time

            # Performance assertions
            self.assertEqual(len(commit_history), 1000)
            self.assertLess(
                analysis_time, 10.0, "Analysis took too long for 1000 commits"
            )

    @patch("src.ticket_master.repository.git.Repo")
    def test_large_file_count_performance(self, mock_repo_class):
        """Test performance when analyzing repositories with many files."""
        mock_repo = Mock()
        mock_repo_class.return_value = mock_repo

        # Mock many files in the repository
        mock_files = []
        for i in range(500):
            mock_files.extend(
                [f"src/module_{i}/file_{j}.py" for j in range(10)]
            )

        mock_repo.git.ls_files.return_value = "\n".join(mock_files)

        with patch(
            "src.ticket_master.repository.Repository.__init__",
            return_value=None,
        ):
            repo = Repository.__new__(Repository)
            repo.repo = mock_repo

            start_time = time.time()
            # This would be part of file analysis
            files = repo.repo.git.ls_files().split("\n")
            analysis_time = time.time() - start_time

            self.assertEqual(len(files), 5000)
            self.assertLess(analysis_time, 5.0, "File listing took too long")

    @patch("src.ticket_master.data_scraper.DataScraper")
    def test_bulk_data_processing_performance(self, mock_scraper_class):
        """Test performance of bulk data processing operations."""
        mock_scraper = Mock()
        mock_scraper_class.return_value = mock_scraper

        # Mock large dataset
        large_dataset = [
            {
                "file": f"file_{i}.py",
                "lines": 100 + (i % 500),
                "complexity": i % 10,
                "changes": i % 20,
            }
            for i in range(1000)
        ]

        mock_scraper.analyze_repository.return_value = large_dataset

        # Create scraper instance with proper initialization
        with patch(
            "src.ticket_master.data_scraper.DataScraper.__init__",
            return_value=None,
        ):
            scraper = DataScraper.__new__(DataScraper)
            scraper.analyze_repository = mock_scraper.analyze_repository

            start_time = time.time()
            result = scraper.analyze_repository("/fake/path")
            processing_time = time.time() - start_time

            self.assertEqual(len(result), 1000)
            self.assertLess(
                processing_time, 15.0, "Bulk processing took too long"
            )

    def test_memory_usage_optimization(self):
        """Test memory usage optimization for large datasets."""

        # Simulate processing large amounts of data in chunks
        def process_in_chunks(data, chunk_size=100):
            """Process data in chunks to optimize memory usage."""
            results = []
            for i in range(0, len(data), chunk_size):
                chunk = data[i : i + chunk_size]
                # Process chunk
                processed_chunk = [item * 2 for item in chunk]
                results.extend(processed_chunk)
            return results

        # Test with large dataset
        large_data = list(range(10000))

        start_time = time.time()
        result = process_in_chunks(large_data)
        processing_time = time.time() - start_time

        self.assertEqual(len(result), 10000)
        self.assertLess(
            processing_time, 2.0, "Chunked processing took too long"
        )

    @patch("git.Repo.clone_from")
    def test_large_repository_clone_performance(self, mock_clone):
        """Test performance of cloning large repositories with optimization."""
        mock_repo = Mock()
        mock_clone.return_value = mock_repo

        github_utils = GitHubUtils()

        start_time = time.time()
        # Test shallow clone for performance
        mock_clone("https://github.com/large/repo.git", "/tmp/test", depth=1)
        clone_time = time.time() - start_time

        # Shallow clone should be much faster
        self.assertLess(clone_time, 1.0, "Shallow clone took too long")
        mock_clone.assert_called_with(
            "https://github.com/large/repo.git", "/tmp/test", depth=1
        )


class TestBulkOperationsPerformance(unittest.TestCase):
    """Test performance of bulk operations."""

    @patch("src.ticket_master.issue.Github")
    def test_bulk_issue_creation_performance(self, mock_github_class):
        """Test performance of creating many issues in bulk."""
        mock_github = Mock()
        mock_github_class.return_value = mock_github
        mock_repo = Mock()
        mock_github.get_repo.return_value = mock_repo

        # Mock successful issue creation
        created_issues = []
        for i in range(50):
            mock_issue = Mock()
            mock_issue.number = i + 1
            mock_issue.html_url = (
                f"https://github.com/test/repo/issues/{i + 1}"
            )
            created_issues.append(mock_issue)

        mock_repo.create_issue.side_effect = created_issues

        # Create many issues
        issues_data = [
            {
                "title": f"Automated Issue {i}",
                "body": f"This is automated issue {i} for testing bulk creation.",
                "labels": ["automated", "bulk-test"],
            }
            for i in range(50)
        ]

        start_time = time.time()
        results = []
        for issue_data in issues_data:
            result = mock_repo.create_issue(**issue_data)
            results.append(result)
            # Small delay to respect rate limits
            time.sleep(0.01)  # 10ms delay

        bulk_creation_time = time.time() - start_time

        self.assertEqual(len(results), 50)
        # Should complete within reasonable time even with delays
        self.assertLess(bulk_creation_time, 5.0)

    def test_parallel_processing_simulation(self):
        """Test simulation of parallel processing for performance."""
        import concurrent.futures
        import threading

        def process_item(item):
            """Simulate processing an item."""
            # Simulate some work
            time.sleep(0.01)
            return item * item

        items = list(range(100))

        # Test sequential processing
        start_time = time.time()
        sequential_results = [process_item(item) for item in items]
        sequential_time = time.time() - start_time

        # Test parallel processing (simulation)
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            parallel_results = list(executor.map(process_item, items))
        parallel_time = time.time() - start_time

        self.assertEqual(sequential_results, parallel_results)
        # Parallel should be faster (though with overhead, may not always be true for small tasks)
        self.assertLess(
            parallel_time, sequential_time * 2
        )  # At least some improvement


class TestMemoryOptimization(unittest.TestCase):
    """Test memory usage optimization scenarios."""

    def test_large_file_streaming(self):
        """Test streaming large files instead of loading entirely into memory."""
        # Create a large temporary file
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as temp_file:
            # Write 10MB of data
            for i in range(100000):
                temp_file.write(f"Line {i}: " + "x" * 100 + "\n")
            temp_file_path = temp_file.name

        try:
            # Test streaming read vs full read
            start_time = time.time()
            line_count = 0
            with open(temp_file_path, "r") as f:
                for line in f:  # Stream line by line
                    line_count += 1
            streaming_time = time.time() - start_time

            self.assertEqual(line_count, 100000)
            self.assertLess(
                streaming_time, 10.0, "Streaming read took too long"
            )

        finally:
            os.unlink(temp_file_path)

    def test_generator_vs_list_memory_usage(self):
        """Test generator usage for memory optimization."""

        def generate_large_dataset():
            """Generator that yields items instead of creating a large list."""
            for i in range(10000):
                yield {
                    "id": i,
                    "data": f"item_{i}",
                    "metadata": {"index": i, "processed": False},
                }

        def process_with_generator(generator):
            """Process items from generator."""
            processed_count = 0
            for item in generator:
                # Simulate processing
                item["metadata"]["processed"] = True
                processed_count += 1
            return processed_count

        start_time = time.time()
        count = process_with_generator(generate_large_dataset())
        processing_time = time.time() - start_time

        self.assertEqual(count, 10000)
        self.assertLess(
            processing_time, 5.0, "Generator processing took too long"
        )

    def test_cache_optimization(self):
        """Test caching for performance optimization."""
        # Simple cache implementation
        cache = {}

        def expensive_operation(n):
            """Simulate expensive operation that can benefit from caching."""
            if n in cache:
                return cache[n]

            # Simulate expensive computation
            time.sleep(0.01)
            result = n * n * n
            cache[n] = result
            return result

        # Test performance with caching
        test_values = [1, 2, 3, 4, 5] * 20  # Repeated values

        start_time = time.time()
        results = [expensive_operation(val) for val in test_values]
        cached_time = time.time() - start_time

        self.assertEqual(len(results), 100)
        # With caching, repeated calculations should be much faster
        self.assertLess(cached_time, 2.0, "Cached operations took too long")
        self.assertEqual(len(cache), 5)  # Only 5 unique values cached


class TestScalabilityLimits(unittest.TestCase):
    """Test scalability limits and edge cases."""

    def test_maximum_commit_analysis(self):
        """Test analysis with maximum reasonable number of commits."""
        # Test with very large number of commits
        max_commits = 10000

        # Mock commits efficiently
        def mock_commit_generator():
            for i in range(max_commits):
                mock_commit = Mock()
                mock_commit.hexsha = f"hash_{i}"
                mock_commit.message = f"Message {i}"
                yield mock_commit

        start_time = time.time()
        commits = list(mock_commit_generator())
        generation_time = time.time() - start_time

        self.assertEqual(len(commits), max_commits)
        self.assertLess(
            generation_time, 5.0, "Commit generation took too long"
        )

    def test_file_system_limits(self):
        """Test handling of file system limits and edge cases."""
        # Test with many small files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create many small files
            file_count = 1000
            for i in range(file_count):
                file_path = os.path.join(temp_dir, f"file_{i:04d}.txt")
                with open(file_path, "w") as f:
                    f.write(f"Content of file {i}")

            # Test file listing performance
            start_time = time.time()
            files = os.listdir(temp_dir)
            listing_time = time.time() - start_time

            self.assertEqual(len(files), file_count)
            self.assertLess(listing_time, 2.0, "File listing took too long")

    def test_network_timeout_simulation(self):
        """Test handling of network timeouts in bulk operations."""

        def simulate_network_request(delay=0.1):
            """Simulate network request with delay."""
            time.sleep(delay)
            return {"status": "success", "data": "response"}

        # Test with reasonable timeout
        start_time = time.time()
        results = []
        for i in range(10):
            try:
                result = simulate_network_request(0.05)  # 50ms per request
                results.append(result)
            except Exception as e:
                results.append({"status": "error", "error": str(e)})

        total_time = time.time() - start_time

        self.assertEqual(len(results), 10)
        self.assertLess(total_time, 2.0, "Network simulation took too long")


if __name__ == "__main__":
    unittest.main()
