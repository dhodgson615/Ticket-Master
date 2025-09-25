"""
Database module for data operations and storage.

This module provides the Database base class and its subclasses for handling
both local user data and server data operations with proper connection management,
error handling, and security considerations.
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import sqlite3

# Import with fallback installation - placeholder
# (yaml not needed in current implementation)


class DatabaseError(Exception):
    """Custom exception for database-related errors."""

    pass


class ConnectionError(DatabaseError):
    """Exception for database connection errors."""

    pass


class Database(ABC):
    """Abstract base class for database operations.

    This class provides the foundation for handling database operations
    with proper connection management, error handling, and security
    considerations for both user local data and server data.

    Attributes:
        connection_string: Database connection string or path
        logger: Logger instance for this class
        _connection: Active database connection (if any)
    """

    def __init__(self, connection_string: str) -> None:
        """Initialize the Database with connection information.

        Args:
            connection_string: Database connection string or file path

        Raises:
            DatabaseError: If connection string is invalid
        """
        if not connection_string or not connection_string.strip():
            raise DatabaseError("Connection string cannot be empty")

        self.connection_string = connection_string.strip()
        self.logger = logging.getLogger(self.__class__.__name__)
        self._connection: Optional[Any] = None

    @abstractmethod
    def connect(self) -> None:
        """Establish connection to the database.

        Raises:
            ConnectionError: If unable to connect to database
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """Close the database connection."""
        pass

    @abstractmethod
    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a database query.

        Args:
            query: SQL query to execute
            params: Optional parameters for the query

        Returns:
            List of result dictionaries

        Raises:
            DatabaseError: If query execution fails
        """
        pass

    @abstractmethod
    def execute_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
        """Execute a database command (INSERT, UPDATE, DELETE).

        Args:
            command: SQL command to execute
            params: Optional parameters for the command

        Returns:
            Number of affected rows

        Raises:
            DatabaseError: If command execution fails
        """
        pass

    @abstractmethod
    def create_tables(self) -> None:
        """Create necessary database tables."""
        pass

    def is_connected(self) -> bool:
        """Check if database connection is active.

        Returns:
            True if connected, False otherwise
        """
        return self._connection is not None

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()

    def __str__(self) -> str:
        """String representation of the database."""
        return f"{self.__class__.__name__}(connection_string='{self.connection_string}')"

    def __repr__(self) -> str:
        """Developer representation of the database."""
        return f"{self.__class__.__name__}(connection_string='{self.connection_string}', connected={self.is_connected()})"


class UserDatabase(Database):
    """Database subclass for local user computational data management.

    This class handles local SQLite database operations for storing user
    preferences, cached data, analysis results, and other local computational
    data with file-based storage and proper error handling.

    Attributes:
        db_path: Path to the SQLite database file
    """

    def __init__(self, db_path: Optional[str] = None) -> None:
        """Initialize the UserDatabase with optional database path.

        Args:
            db_path: Path to SQLite database file (default: ~/.ticket_master/user_data.db)

        Raises:
            DatabaseError: If database path is invalid
        """
        if db_path is None:
            # Use default path in user's home directory
            home_dir = Path.home()
            app_dir = home_dir / ".ticket_master"
            app_dir.mkdir(exist_ok=True)
            db_path = str(app_dir / "user_data.db")

        self.db_path = Path(db_path)
        super().__init__(str(self.db_path))

        # Ensure parent directory exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> None:
        """Establish connection to the SQLite database.

        Raises:
            ConnectionError: If unable to connect to database
        """
        try:
            self._connection = sqlite3.connect(str(self.db_path))
            self._connection.row_factory = (
                sqlite3.Row
            )  # Enable column access by name
            self.logger.info(f"Connected to user database: {self.db_path}")
        except sqlite3.Error as e:
            raise ConnectionError(f"Failed to connect to user database: {e}")

    def disconnect(self) -> None:
        """Close the SQLite database connection."""
        if self._connection:
            try:
                self._connection.close()
                self._connection = None
                self.logger.info("Disconnected from user database")
            except sqlite3.Error as e:
                self.logger.warning(f"Error closing database connection: {e}")

    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SELECT query on the SQLite database.

        Args:
            query: SQL query to execute
            params: Optional parameters for the query

        Returns:
            List of result dictionaries

        Raises:
            DatabaseError: If query execution fails
        """
        if not self._connection:
            raise DatabaseError("Not connected to database")

        try:
            cursor = self._connection.cursor()
            if params:
                # Convert dict params to tuple for named parameters
                if isinstance(params, dict):
                    cursor.execute(query, params)
                else:
                    cursor.execute(query, params)
            else:
                cursor.execute(query)

            results = cursor.fetchall()
            return [dict(row) for row in results]

        except sqlite3.Error as e:
            raise DatabaseError(f"Query execution failed: {e}")

    def execute_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
        """Execute a command (INSERT, UPDATE, DELETE) on the SQLite database.

        Args:
            command: SQL command to execute
            params: Optional parameters for the command

        Returns:
            Number of affected rows

        Raises:
            DatabaseError: If command execution fails
        """
        if not self._connection:
            raise DatabaseError("Not connected to database")

        try:
            cursor = self._connection.cursor()
            if params:
                # Convert dict params to list for positional parameters in this case
                if isinstance(params, dict):
                    cursor.execute(command, params)
                else:
                    cursor.execute(command, params)
            else:
                cursor.execute(command)

            self._connection.commit()
            return cursor.rowcount

        except sqlite3.Error as e:
            self._connection.rollback()
            raise DatabaseError(f"Command execution failed: {e}")

    def create_tables(self) -> None:
        """Create necessary tables for user data storage."""
        tables = [
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS repository_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_path TEXT NOT NULL,
                cache_key TEXT NOT NULL,
                cache_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                expires_at TIMESTAMP,
                UNIQUE(repo_path, cache_key)
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_path TEXT NOT NULL,
                analysis_type TEXT NOT NULL,
                result_data TEXT NOT NULL,
                metadata TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS generated_issues (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repo_path TEXT NOT NULL,
                issue_title TEXT NOT NULL,
                issue_description TEXT NOT NULL,
                labels TEXT,
                assignees TEXT,
                github_issue_number INTEGER,
                github_issue_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT DEFAULT 'draft'
            )
            """,
        ]

        for table_sql in tables:
            try:
                self.execute_command(table_sql)
                self.logger.debug(f"Created/verified table")
            except DatabaseError as e:
                self.logger.error(f"Failed to create table: {e}")
                raise

    def get_user_preference(
        self, key: str, default: Optional[str] = None
    ) -> Optional[str]:
        """Get user preference value.

        Args:
            key: Preference key
            default: Default value if key not found

        Returns:
            Preference value or default
        """
        try:
            results = self.execute_query(
                "SELECT value FROM user_preferences WHERE key = :key",
                {"key": key},
            )
            return results[0]["value"] if results else default
        except DatabaseError:
            return default

    def set_user_preference(self, key: str, value: str) -> None:
        """Set user preference value.

        Args:
            key: Preference key
            value: Preference value
        """
        self.execute_command(
            """
            INSERT OR REPLACE INTO user_preferences (key, value, updated_at)
            VALUES (:key, :value, CURRENT_TIMESTAMP)
            """,
            {"key": key, "value": value},
        )

    def cache_repository_data(
        self,
        repo_path: str,
        cache_key: str,
        data: Dict[str, Any],
        expires_in_hours: int = 24,
    ) -> None:
        """Cache repository analysis data.

        Args:
            repo_path: Repository path
            cache_key: Cache key identifier
            data: Data to cache
            expires_in_hours: Cache expiration time in hours
        """
        self.execute_command(
            """
            INSERT OR REPLACE INTO repository_cache 
            (repo_path, cache_key, cache_data, created_at, expires_at)
            VALUES (:repo_path, :cache_key, :cache_data, CURRENT_TIMESTAMP, datetime('now', '+{} hours'))
            """.format(
                expires_in_hours
            ),
            {
                "repo_path": repo_path,
                "cache_key": cache_key,
                "cache_data": json.dumps(data),
            },
        )

    def get_cached_repository_data(
        self, repo_path: str, cache_key: str
    ) -> Optional[Dict[str, Any]]:
        """Get cached repository data if not expired.

        Args:
            repo_path: Repository path
            cache_key: Cache key identifier

        Returns:
            Cached data if valid, None otherwise
        """
        try:
            results = self.execute_query(
                """
                SELECT cache_data FROM repository_cache 
                WHERE repo_path = :repo_path AND cache_key = :cache_key AND 
                (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                """,
                {"repo_path": repo_path, "cache_key": cache_key},
            )

            if results:
                return json.loads(results[0]["cache_data"])
            return None

        except (DatabaseError, json.JSONDecodeError):
            return None


class ServerDatabase(Database):
    """Database subclass for server data management.

    This class handles server-based database operations for storing shared data,
    user management, analytics, and other server-side data with proper connection
    pooling and security considerations.

    Note: This is a placeholder implementation that would be extended for
    specific server database systems (PostgreSQL, MySQL, etc.).
    """

    def __init__(self, connection_string: str, pool_size: int = 5) -> None:
        """Initialize the ServerDatabase with connection details.

        Args:
            connection_string: Database connection string
            pool_size: Connection pool size

        Raises:
            DatabaseError: If connection string is invalid
        """
        super().__init__(connection_string)
        self.pool_size = pool_size
        self._connection_pool: Optional[Any] = None

    def connect(self) -> None:
        """Establish connection to the server database.

        Note: This is a placeholder implementation. In a real scenario,
        this would connect to PostgreSQL, MySQL, or another server database.

        Raises:
            ConnectionError: If unable to connect to database
        """
        # Placeholder implementation
        self.logger.warning("ServerDatabase is a placeholder implementation")
        self._connection = "placeholder_connection"

    def disconnect(self) -> None:
        """Close the server database connection."""
        if self._connection:
            self._connection = None
            self.logger.info("Disconnected from server database")

    def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Execute a SELECT query on the server database.

        Args:
            query: SQL query to execute
            params: Optional parameters for the query

        Returns:
            List of result dictionaries

        Raises:
            DatabaseError: If query execution fails
        """
        # Placeholder implementation
        self.logger.warning(
            "ServerDatabase query execution is not implemented"
        )
        return []

    def execute_command(
        self, command: str, params: Optional[Dict[str, Any]] = None
    ) -> int:
        """Execute a command on the server database.

        Args:
            command: SQL command to execute
            params: Optional parameters for the command

        Returns:
            Number of affected rows

        Raises:
            DatabaseError: If command execution fails
        """
        # Placeholder implementation
        self.logger.warning(
            "ServerDatabase command execution is not implemented"
        )
        return 0

    def create_tables(self) -> None:
        """Create necessary tables for server data storage."""
        # Placeholder implementation
        self.logger.warning("ServerDatabase table creation is not implemented")
        pass
