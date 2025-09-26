"""
DataScraper module for repository information extraction and analysis.

This module provides the DataScraper class for comprehensively gathering
all information from a repository to build detailed Repository objects
with enhanced metadata, analysis capabilities, and caching support.
"""

import json
import logging
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

try:
    pass
except ImportError:
    import subprocess
    import sys

    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "GitPython>=3.1.40"]
    )

    from git import Repo, InvalidGitRepositoryError

from .database import DatabaseError, UserDatabase
from .repository import Repository, RepositoryError


class DataScraperError(Exception):
    """Custom exception for data scraper errors."""

    pass


class DataScraper:
    """Class for comprehensive repository information extraction.

    This class provides methods to extract and analyze all relevant information
    from a repository, including Git history, file content, structure analysis,
    dependency information, and build detailed Repository objects with caching.

    Attributes:
        repo_path: Path to the repository
        repository: Repository instance for Git operations
        cache_db: Optional database for caching analysis results
        logger: Logger instance for this class
        _analysis_cache: In-memory cache for analysis results
    """

    def __init__(
        self,
        repo_path: Union[str, Path],
        use_cache: bool = True,
        cache_expiry_hours: int = 24,
    ) -> None:
        """Initialize the DataScraper with repository path.

        Args:
            repo_path: Path to the Git repository
            use_cache: Whether to use database caching for analysis results
            cache_expiry_hours: Cache expiry time in hours

        Raises:
            DataScraperError: If repository path is invalid
        """
        self.repo_path = Path(repo_path).resolve()
        if not self.repo_path.exists():
            raise DataScraperError(
                f"Repository path does not exist: {self.repo_path}"
            )

        try:
            self.repository = Repository(str(self.repo_path))

        except RepositoryError as e:
            raise DataScraperError(f"Invalid repository: {e}")

        self.use_cache = use_cache
        self.cache_expiry_hours = cache_expiry_hours
        self.cache_db: Optional[UserDatabase] = None
        self.logger = logging.getLogger(self.__class__.__name__)
        self._analysis_cache: Dict[str, Any] = {}

        # Initialize cache database if requested
        if self.use_cache:
            try:
                self.cache_db = UserDatabase()
                with self.cache_db:
                    self.cache_db.create_tables()

            except DatabaseError as e:
                self.logger.warning(
                    f"Failed to initialize cache database: {e}"
                )

                self.use_cache = False

    def scrape_all(self, max_commits: int = 100) -> Dict[str, Any]:
        """Perform comprehensive repository analysis and data extraction.

        Args:
            max_commits: Maximum number of commits to analyze

        Returns:
            Dictionary containing all extracted repository information

        Raises:
            DataScraperError: If scraping fails
        """
        self.logger.info(
            f"Starting comprehensive repository analysis: {self.repo_path}"
        )

        start_time = time.time()

        try:
            # Check cache first
            cache_key = f"full_analysis_{max_commits}"
            cached_result = self._get_from_cache(cache_key)

            if cached_result:
                self.logger.info("Using cached analysis results")
                return cached_result

            analysis_result = {
                "repository_info": self.scrape_repository_info(),
                "git_analysis": self.scrape_git_history(max_commits),
                "file_structure": self.scrape_file_structure(),
                "content_analysis": self.scrape_content_analysis(),
                "dependency_info": self.scrape_dependencies(),
                "build_info": self.scrape_build_configuration(),
                "quality_metrics": self.analyze_code_quality(),
                "activity_patterns": self.analyze_activity_patterns(),
                "metadata": {
                    "scraped_at": datetime.now().isoformat(),
                    "scraper_version": "1.0",
                    "analysis_time": 0,  # Will be updated below
                    "max_commits": max_commits,
                },
            }

            analysis_time = time.time() - start_time
            analysis_result["metadata"]["analysis_time"] = analysis_time

            # Cache the result
            self._store_in_cache(cache_key, analysis_result)

            self.logger.info(
                f"Completed repository analysis in {analysis_time:.2f}s"
            )

            return analysis_result

        except Exception as e:
            raise DataScraperError(f"Failed to scrape repository: {e}")

    def scrape_repository_info(self) -> Dict[str, Any]:
        """Extract basic repository information and metadata.

        Returns:
            Dictionary containing repository information
        """
        try:
            repo_info = self.repository.get_repository_info()

            # Enhance with additional metadata
            enhanced_info = {
                **repo_info,
                "absolute_path": str(self.repo_path),
                "size_info": self._calculate_repository_size(),
                "git_config": self._extract_git_config(),
                "remotes": self._extract_remote_info(),
            }

            return enhanced_info

        except Exception as e:
            self.logger.error(f"Failed to scrape repository info: {e}")
            return {"error": str(e)}

    def scrape_git_history(self, max_commits: int = 100) -> Dict[str, Any]:
        """Extract comprehensive Git history and analysis.

        Args:
            max_commits: Maximum number of commits to analyze

        Returns:
            Dictionary containing Git history analysis
        """
        try:
            commits = self.repository.get_commit_history(max_count=max_commits)
            file_changes = self.repository.get_file_changes(
                max_commits=max_commits
            )

            # Analyze commit patterns
            commit_analysis = self._analyze_commits(commits)

            # Analyze contributor patterns
            contributor_analysis = self._analyze_contributors(commits)

            # Analyze branching patterns
            branching_analysis = self._analyze_branches()

            return {
                "commits": commits,
                "file_changes": file_changes,
                "commit_analysis": commit_analysis,
                "contributor_analysis": contributor_analysis,
                "branching_analysis": branching_analysis,
                "total_analyzed_commits": len(commits),
            }

        except Exception as e:
            self.logger.error(f"Failed to scrape Git history: {e}")
            return {"error": str(e)}

    def scrape_file_structure(self) -> Dict[str, Any]:
        """Analyze repository file structure and organization.

        Returns:
            Dictionary containing file structure analysis
        """
        try:
            structure = {
                "total_files": 0,
                "directories": [],
                "file_types": {},
                "large_files": [],
                "empty_directories": [],
                "hidden_files": [],
                "symlinks": [],
            }

            for item in self.repo_path.rglob("*"):
                if self.repository.is_ignored(
                    str(item.relative_to(self.repo_path))
                ):
                    continue

                if item.is_file():
                    structure["total_files"] += 1

                    # Analyze file type
                    file_ext = item.suffix.lower()
                    structure["file_types"][file_ext] = (
                        structure["file_types"].get(file_ext, 0) + 1
                    )

                    # Check for large files (>1MB)
                    if item.stat().st_size > 1024 * 1024:
                        structure["large_files"].append(
                            {
                                "path": str(item.relative_to(self.repo_path)),
                                "size": item.stat().st_size,
                            }
                        )

                    # Check for hidden files
                    if item.name.startswith("."):
                        structure["hidden_files"].append(
                            str(item.relative_to(self.repo_path))
                        )

                    # Check for symlinks
                    if item.is_symlink():
                        structure["symlinks"].append(
                            str(item.relative_to(self.repo_path))
                        )

                elif item.is_dir():
                    rel_path = str(item.relative_to(self.repo_path))
                    structure["directories"].append(rel_path)

                    # Check for empty directories
                    if not any(item.iterdir()):
                        structure["empty_directories"].append(rel_path)

            # Sort large files by size
            structure["large_files"].sort(
                key=lambda x: x["size"], reverse=True
            )

            return structure

        except Exception as e:
            self.logger.error(f"Failed to scrape file structure: {e}")
            return {"error": str(e)}

    def scrape_content_analysis(self) -> Dict[str, Any]:
        """Analyze repository content for patterns and characteristics.

        Returns:
            Dictionary containing content analysis
        """
        try:
            analysis = {
                "programming_languages": {},
                "documentation_files": [],
                "configuration_files": [],
                "test_files": [],
                "build_files": [],
                "readme_info": None,
                "license_info": None,
            }

            # File type mappings for language detection
            language_extensions = {
                ".py": "Python",
                ".js": "JavaScript",
                ".ts": "TypeScript",
                ".java": "Java",
                ".cpp": "C++",
                ".c": "C",
                ".go": "Go",
                ".rs": "Rust",
                ".rb": "Ruby",
                ".php": "PHP",
                ".cs": "C#",
                ".swift": "Swift",
                ".kt": "Kotlin",
                ".scala": "Scala",
                ".html": "HTML",
                ".css": "CSS",
                ".sql": "SQL",
                ".sh": "Shell",
                ".yaml": "YAML",
                ".yml": "YAML",
                ".json": "JSON",
                ".xml": "XML",
                ".md": "Markdown",
            }

            for item in self.repo_path.rglob("*"):
                if not item.is_file() or self.repository.is_ignored(
                    str(item.relative_to(self.repo_path))
                ):
                    continue

                rel_path = str(item.relative_to(self.repo_path))
                file_ext = item.suffix.lower()
                file_name = item.name.lower()

                # Language detection
                if file_ext in language_extensions:
                    lang = language_extensions[file_ext]

                    if lang not in analysis["programming_languages"]:
                        analysis["programming_languages"][lang] = {
                            "files": [],
                            "total_lines": 0,
                        }

                    analysis["programming_languages"][lang]["files"].append(
                        rel_path
                    )

                    # Count lines if reasonable file size
                    if item.stat().st_size < 10 * 1024 * 1024:  # <10MB
                        try:
                            with open(
                                item, "r", encoding="utf-8", errors="ignore"
                            ) as f:
                                lines = sum(1 for line in f)
                            analysis["programming_languages"][lang][
                                "total_lines"
                            ] += lines

                        except Exception:  # TODO: specify exception
                            pass

                # Special file detection
                if file_name in [
                    "readme.md",
                    "readme.txt",
                    "readme.rst",
                    "readme",
                ]:
                    analysis["readme_info"] = self._analyze_readme(item)

                elif file_name in [
                    "license",
                    "license.txt",
                    "license.md",
                    "copying",
                ]:
                    analysis["license_info"] = self._analyze_license(item)

                elif any(
                    test_pattern in file_name
                    for test_pattern in ["test_", "_test", "test.", "spec."]
                ):
                    analysis["test_files"].append(rel_path)

                elif file_name in [
                    "makefile",
                    "dockerfile",
                    "docker-compose.yml",
                    "requirements.txt",
                    "package.json",
                    "pom.xml",
                    "build.gradle",
                    "cargo.toml",
                ]:
                    analysis["build_files"].append(rel_path)

                elif file_ext in [
                    ".yml",
                    ".yaml",
                    ".json",
                    ".toml",
                    ".ini",
                    ".cfg",
                    ".conf",
                ]:
                    analysis["configuration_files"].append(rel_path)

                elif (
                    file_ext in [".md", ".rst", ".txt"]
                    and "readme" not in file_name
                ):
                    analysis["documentation_files"].append(rel_path)

            return analysis

        except Exception as e:
            self.logger.error(f"Failed to scrape content analysis: {e}")
            return {"error": str(e)}

    def scrape_dependencies(self) -> Dict[str, Any]:
        """Extract dependency information from various package managers.

        Returns:
            Dictionary containing dependency information
        """
        dependencies = {
            "python": self._extract_python_dependencies(),
            "javascript": self._extract_javascript_dependencies(),
            "java": self._extract_java_dependencies(),
            "go": self._extract_go_dependencies(),
            "rust": self._extract_rust_dependencies(),
        }

        # Filter out empty results
        return {k: v for k, v in dependencies.items() if v}

    def scrape_build_configuration(self) -> Dict[str, Any]:
        """Extract build and CI/CD configuration information.

        Returns:
            Dictionary containing build configuration
        """
        build_info = {
            "ci_cd": self._extract_ci_config(),
            "containerization": self._extract_container_config(),
            "build_systems": self._extract_build_systems(),
        }

        return {k: v for k, v in build_info.items() if v}

    def analyze_code_quality(self) -> Dict[str, Any]:
        """Analyze code quality metrics and patterns.

        Returns:
            Dictionary containing code quality analysis
        """
        try:
            quality_metrics = {
                "file_size_distribution": self._analyze_file_sizes(),
                "complexity_indicators": self._analyze_complexity(),
                "documentation_coverage": self._analyze_documentation_coverage(),
                "test_coverage_indicators": self._analyze_test_indicators(),
            }

            return quality_metrics

        except Exception as e:
            self.logger.error(f"Failed to analyze code quality: {e}")
            return {"error": str(e)}

    def analyze_activity_patterns(self) -> Dict[str, Any]:
        """Analyze repository activity patterns and trends.

        Returns:
            Dictionary containing activity pattern analysis
        """
        try:
            # Get recent commits for analysis
            commits = self.repository.get_commit_history(max_count=200)

            if not commits:
                return {"error": "No commits found"}

            patterns = {
                "commit_frequency": self._analyze_commit_frequency(commits),
                "time_patterns": self._analyze_time_patterns(commits),
                "file_hotspots": self._analyze_file_hotspots(commits),
                "contributor_activity": self._analyze_contributor_activity(
                    commits
                ),
            }

            return patterns

        except Exception as e:
            self.logger.error(f"Failed to analyze activity patterns: {e}")
            return {"error": str(e)}

    def _get_from_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get analysis result from cache.

        Args:
            cache_key: Cache key to lookup

        Returns:
            Cached result or None if not found/expired
        """
        if not self.use_cache or not self.cache_db:
            return None

        try:
            with self.cache_db:
                return self.cache_db.get_cached_repository_data(
                    str(self.repo_path), cache_key
                )

        except DatabaseError:
            return None

    def _store_in_cache(self, cache_key: str, data: Dict[str, Any]) -> None:
        """Store analysis result in cache.

        Args:
            cache_key: Cache key
            data: Data to cache
        """
        if not self.use_cache or not self.cache_db:
            return

        try:
            with self.cache_db:
                self.cache_db.cache_repository_data(
                    str(self.repo_path),
                    cache_key,
                    data,
                    self.cache_expiry_hours,
                )

        except DatabaseError as e:
            self.logger.warning(f"Failed to cache data: {e}")

    def _calculate_repository_size(self) -> Dict[str, Any]:
        """Calculate repository size statistics."""
        total_size = 0
        file_count = 0

        for item in self.repo_path.rglob("*"):
            if item.is_file() and not self.repository.is_ignored(
                str(item.relative_to(self.repo_path))
            ):
                total_size += item.stat().st_size
                file_count += 1

        return {
            "total_bytes": total_size,
            "total_mb": round(total_size / (1024 * 1024), 2),
            "file_count": file_count,
            "average_file_size": (
                round(total_size / file_count, 2) if file_count > 0 else 0
            ),
        }

    def _extract_git_config(self) -> Dict[str, Any]:
        """Extract Git configuration information."""
        try:
            config = {}
            config_reader = self.repository.repo.config_reader()

            # Extract common config values
            try:
                config["user_name"] = config_reader.get_value("user", "name")

            except Exception:
                pass

            try:
                config["user_email"] = config_reader.get_value("user", "email")

            except Exception:
                pass

            return config
        except Exception:
            return {}

    def _extract_remote_info(self) -> List[Dict[str, str]]:
        """Extract information about Git remotes."""
        try:
            remotes = []
            for remote in self.repository.repo.remotes:
                remotes.append(
                    {
                        "name": remote.name,
                        "url": next(iter(remote.urls), "unknown"),
                    }
                )

            return remotes

        except Exception:
            return []

    def _analyze_commits(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze commit patterns and statistics."""
        if not commits:
            return {}

        # Calculate commit statistics
        commit_messages = [commit["summary"] for commit in commits]

        return {
            "total_commits": len(commits),
            "average_message_length": sum(len(msg) for msg in commit_messages)
            / len(commit_messages),
            "recent_activity_days": self._calculate_activity_span(commits),
            "commit_size_stats": self._analyze_commit_sizes(commits),
        }

    def _analyze_contributors(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze contributor patterns."""
        contributors = {}

        for commit in commits:
            author = commit.get("author", "Unknown")

            if author not in contributors:
                contributors[author] = {
                    "commits": 0,
                    "first_commit": commit["date"],
                    "last_commit": commit["date"],
                }

            contributors[author]["commits"] += 1

            if commit["date"] > contributors[author]["last_commit"]:
                contributors[author]["last_commit"] = commit["date"]

            if commit["date"] < contributors[author]["first_commit"]:
                contributors[author]["first_commit"] = commit["date"]

        return {
            "total_contributors": len(contributors),
            "top_contributors": sorted(
                contributors.items(),
                key=lambda x: x[1]["commits"],
                reverse=True,
            )[:5],
            "contributor_details": contributors,
        }

    def _analyze_branches(self) -> Dict[str, Any]:
        """Analyze branching patterns."""
        try:
            branches = list(self.repository.repo.branches)

            return {
                "total_branches": len(branches),
                "branch_names": [branch.name for branch in branches],
                "current_branch": self.repository.repo.active_branch.name,
            }

        except Exception:
            return {"error": "Could not analyze branches"}

    # Placeholder methods for dependency extraction (these would be implemented based on specific needs)
    def _extract_python_dependencies(self) -> Optional[Dict[str, Any]]:
        """Extract Python dependencies from requirements.txt, setup.py, pyproject.toml."""
        req_file = self.repo_path / "requirements.txt"

        if req_file.exists():
            try:
                with open(req_file, "r") as f:
                    deps = [
                        line.strip()
                        for line in f
                        if line.strip() and not line.startswith("#")
                    ]

                return {"file": "requirements.txt", "dependencies": deps}

            except Exception:
                pass

        return None

    def _extract_javascript_dependencies(self) -> Optional[Dict[str, Any]]:
        """Extract JavaScript dependencies from package.json."""
        package_file = self.repo_path / "package.json"

        if package_file.exists():
            try:
                with open(package_file, "r") as f:
                    package_data = json.load(f)

                return {
                    "file": "package.json",
                    "dependencies": package_data.get("dependencies", {}),
                    "devDependencies": package_data.get("devDependencies", {}),
                }

            except Exception:  # TODO: specify exception
                pass

        return None

    def _extract_java_dependencies(self) -> Optional[Dict[str, Any]]:
        """Extract Java dependencies from pom.xml or build.gradle."""
        # Simplified implementation - would need XML/Gradle parsing
        if (self.repo_path / "pom.xml").exists():
            return {"file": "pom.xml", "build_system": "maven"}

        elif (self.repo_path / "build.gradle").exists():
            return {"file": "build.gradle", "build_system": "gradle"}

        return None

    def _extract_go_dependencies(self) -> Optional[Dict[str, Any]]:
        """Extract Go dependencies from go.mod."""
        go_mod = self.repo_path / "go.mod"

        if go_mod.exists():
            return {"file": "go.mod", "build_system": "go_modules"}

        return None

    def _extract_rust_dependencies(self) -> Optional[Dict[str, Any]]:
        """Extract Rust dependencies from Cargo.toml."""
        cargo_toml = self.repo_path / "Cargo.toml"

        if cargo_toml.exists():
            return {"file": "Cargo.toml", "build_system": "cargo"}

        return None

    def _extract_ci_config(self) -> Optional[Dict[str, Any]]:
        """Extract CI/CD configuration."""
        ci_configs = []

        # GitHub Actions
        gh_actions_dir = self.repo_path / ".github" / "workflows"

        if gh_actions_dir.exists():
            workflows = list(gh_actions_dir.glob("*.yml")) + list(
                gh_actions_dir.glob("*.yaml")
            )

            if workflows:
                ci_configs.append(
                    {
                        "type": "github_actions",
                        "files": [f.name for f in workflows],
                    }
                )

        # GitLab CI
        gitlab_ci = self.repo_path / ".gitlab-ci.yml"

        if gitlab_ci.exists():
            ci_configs.append(
                {"type": "gitlab_ci", "files": [".gitlab-ci.yml"]}
            )

        # Travis CI
        travis_ci = self.repo_path / ".travis.yml"

        if travis_ci.exists():
            ci_configs.append({"type": "travis_ci", "files": [".travis.yml"]})

        return {"configurations": ci_configs} if ci_configs else None

    def _extract_container_config(self) -> Optional[Dict[str, Any]]:
        """Extract containerization configuration."""
        containers = []

        if (self.repo_path / "Dockerfile").exists():
            containers.append("Dockerfile")

        if (self.repo_path / "docker-compose.yml").exists():
            containers.append("docker-compose.yml")

        return {"files": containers} if containers else None

    def _extract_build_systems(self) -> List[str]:
        """Identify build systems in use."""
        build_systems = []

        build_files = {
            "Makefile": "Make",
            "CMakeLists.txt": "CMake",
            "build.gradle": "Gradle",
            "pom.xml": "Maven",
            "package.json": "npm/yarn",
            "Cargo.toml": "Cargo",
            "setup.py": "setuptools",
        }

        for file_name, system in build_files.items():
            if (self.repo_path / file_name).exists():
                build_systems.append(system)

        return build_systems

    # Additional analysis methods would be implemented here...
    def _analyze_readme(self, readme_path: Path) -> Dict[str, Any]:
        """Analyze README file content."""
        try:
            with open(
                readme_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                content = f.read()

            return {
                "length": len(content),
                "lines": len(content.splitlines()),
                "has_installation": "install" in content.lower(),
                "has_usage": "usage" in content.lower(),
                "has_examples": "example" in content.lower(),
            }

        except Exception:  # TODO: specify exception
            return {"error": "Could not analyze README"}

    def _analyze_license(self, license_path: Path) -> Dict[str, Any]:
        """Analyze license file."""
        try:
            with open(
                license_path, "r", encoding="utf-8", errors="ignore"
            ) as f:
                content = f.read()

            # Simple license detection
            license_indicators = {
                "MIT": "MIT License",
                "Apache": "Apache License",
                "GPL": "GNU General Public License",
                "BSD": "BSD License",
            }

            detected_license = "Unknown"
            for license_type, indicator in license_indicators.items():
                if indicator.lower() in content.lower():
                    detected_license = license_type
                    break

            return {"detected_type": detected_license, "length": len(content)}

        except Exception:  # TODO: specify exception
            return {"error": "Could not analyze license"}

    def _calculate_activity_span(self, commits: List[Dict[str, Any]]) -> int:
        """Calculate the span of recent activity in days."""
        if not commits:
            return 0

        dates = [
            datetime.fromisoformat(commit["date"].replace("Z", "+00:00"))
            for commit in commits
        ]

        return (max(dates) - min(dates)).days

    def _analyze_commit_sizes(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze commit size statistics."""
        # This would analyze insertions/deletions if available
        return {"placeholder": "commit_size_analysis"}

    def _analyze_file_sizes(self) -> Dict[str, Any]:
        """Analyze file size distribution."""
        sizes = []

        for item in self.repo_path.rglob("*"):
            if item.is_file() and not self.repository.is_ignored(
                str(item.relative_to(self.repo_path))
            ):
                sizes.append(item.stat().st_size)

        if not sizes:
            return {}

        sizes.sort()

        return {
            "min": min(sizes),
            "max": max(sizes),
            "median": sizes[len(sizes) // 2],
            "average": sum(sizes) / len(sizes),
        }

    def _analyze_complexity(self) -> Dict[str, Any]:
        """Analyze code complexity indicators."""
        return {"placeholder": "complexity_analysis"}

    def _analyze_documentation_coverage(self) -> Dict[str, Any]:
        """Analyze documentation coverage."""
        return {"placeholder": "documentation_analysis"}

    def _analyze_test_indicators(self) -> Dict[str, Any]:
        """Analyze test coverage indicators."""
        return {"placeholder": "test_analysis"}

    def _analyze_commit_frequency(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze commit frequency patterns."""
        return {"placeholder": "commit_frequency_analysis"}

    def _analyze_time_patterns(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze time-based commit patterns."""
        return {"placeholder": "time_pattern_analysis"}

    def _analyze_file_hotspots(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze which files are modified most frequently."""
        return {"placeholder": "file_hotspot_analysis"}

    def _analyze_contributor_activity(
        self, commits: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze contributor activity patterns."""
        return {"placeholder": "contributor_activity_analysis"}

    def __str__(self) -> str:
        """String representation of the data scraper."""
        return f"DataScraper(repo_path='{self.repo_path}', use_cache={self.use_cache})"

    def __repr__(self) -> str:
        """Developer representation of the data scraper."""
        return (
            f"DataScraper(repo_path='{self.repo_path}', "
            f"use_cache={self.use_cache}, "
            f"cache_expiry={self.cache_expiry_hours}h)"
        )
