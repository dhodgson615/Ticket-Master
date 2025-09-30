"""
Test module for database classes: Database, UserDatabase, and ServerDatabase.

This module provides comprehensive tests for database functionality
including connection management, data storage, and error handling.
"""

import shutil
import sys
import tempfile
import unittest
from pathlib import Path

# Add src directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master_consolidated import (Database, DatabaseError,
                                        ServerDatabase, UserDatabase)


class TestUserDatabase(unittest.TestCase):
    """Test UserDatabase functionality."""

    def setUp(self):
        """Set up test database."""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test.db"
        self.db = UserDatabase(str(self.db_path))

    def tearDown(self):
        """Clean up test database."""
        if self.db.is_connected():
            self.db.disconnect()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_init_default_path(self):
        """Test UserDatabase initialization with default path."""
        db = UserDatabase()
        self.assertIsInstance(db.db_path, Path)
        self.assertTrue(str(db.db_path).endswith("user_data.db"))

    def test_init_custom_path(self):
        """Test UserDatabase initialization with custom path."""
        self.assertEqual(self.db.db_path, self.db_path)

    def test_connect_disconnect(self):
        """Test database connection and disconnection."""
        self.assertFalse(self.db.is_connected())

        self.db.connect()
        self.assertTrue(self.db.is_connected())

        self.db.disconnect()
        self.assertFalse(self.db.is_connected())

    def test_context_manager(self):
        """Test database context manager."""
        with self.db as db:
            self.assertTrue(db.is_connected())
        self.assertFalse(self.db.is_connected())

    def test_create_tables(self):
        """Test table creation."""
        with self.db:
            self.db.create_tables()
            # Should not raise any exceptions

    def test_user_preferences(self):
        """Test user preference storage and retrieval."""
        with self.db:
            self.db.create_tables()

            # Test setting and getting preference
            self.db.set_user_preference("test_key", "test_value")
            value = self.db.get_user_preference("test_key")
            self.assertEqual(value, "test_value")

            # Test default value
            default_value = self.db.get_user_preference(
                "nonexistent", "default"
            )
            self.assertEqual(default_value, "default")

    def test_cache_repository_data(self):
        """Test repository data caching."""
        with self.db:
            self.db.create_tables()

            test_data = {"key": "value", "number": 42}
            self.db.cache_repository_data(
                "/test/repo", "test_cache", test_data
            )

            cached_data = self.db.get_cached_repository_data(
                "/test/repo", "test_cache"
            )
            self.assertEqual(cached_data, test_data)


if __name__ == "__main__":
    unittest.main()
