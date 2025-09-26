"""
Test module for remaining new classes not yet covered by dedicated test files.

This module provides comprehensive tests for classes that don't yet have
their own dedicated test files. As the project grows, tests should be moved
to dedicated files following the pattern: file.py -> test_file.py
"""

import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from src.ticket_master.data_scraper import DataScraper, DataScraperError
from src.ticket_master.database import (Database, DatabaseError,
                                        ServerDatabase, UserDatabase)
from src.ticket_master.llm import LLM, LLMError, LLMProvider, OllamaBackend
from src.ticket_master.pipe import Pipe, PipeError, PipelineStep, PipeStage
from src.ticket_master.prompt import (Prompt, PromptError, PromptTemplate,
                                      PromptType)


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


class TestPromptTemplate(unittest.TestCase):
    """Test PromptTemplate functionality."""

    def test_init_valid_template(self):
        """Test PromptTemplate initialization with valid data."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}",
        )

        self.assertEqual(template.name, "test_template")
        self.assertEqual(template.prompt_type, PromptType.ISSUE_GENERATION)
        self.assertEqual(
            template.base_template,
            "Generate {num_issues} issues for {repo_name}",
        )

    def test_init_string_prompt_type(self):
        """Test PromptTemplate initialization with string prompt type."""
        template = PromptTemplate(
            name="test_template",
            prompt_type="issue_generation",
            base_template="Test template",
        )

        self.assertEqual(template.prompt_type, PromptType.ISSUE_GENERATION)

    def test_render_basic(self):
        """Test basic template rendering."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}",
        )

        variables = {"num_issues": 3, "repo_name": "test-repo"}
        rendered = template.render(variables)

        self.assertEqual(rendered, "Generate 3 issues for test-repo")

    def test_render_missing_variable(self):
        """Test template rendering with missing variable."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}",
        )

        variables = {"num_issues": 3}  # Missing repo_name

        with self.assertRaises(Exception):  # Should raise PromptTemplateError
            template.render(variables)

    def test_get_required_variables(self):
        """Test extraction of required variables."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name} in {language}",
        )

        required_vars = template.get_required_variables()
        self.assertEqual(
            set(required_vars), {"num_issues", "repo_name", "language"}
        )

    def test_provider_variations(self):
        """Test provider-specific template variations."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Base: {value}",
            provider_variations={
                "ollama": "Ollama: {value}",
                "openai": "OpenAI: {value}",
            },
        )

        variables = {"value": "test"}

        # Test base template
        base_result = template.render(variables)
        self.assertEqual(base_result, "Base: test")

        # Test provider variations
        ollama_result = template.render(variables, "ollama")
        self.assertEqual(ollama_result, "Ollama: test")

        openai_result = template.render(variables, "openai")
        self.assertEqual(openai_result, "OpenAI: test")


class TestPrompt(unittest.TestCase):
    """Test Prompt container functionality."""

    def setUp(self):
        """Set up test prompt container."""
        self.prompt = Prompt(default_provider="ollama")

    def test_init(self):
        """Test Prompt initialization."""
        self.assertEqual(self.prompt.default_provider, "ollama")
        self.assertEqual(len(self.prompt.templates), 0)

    def test_add_template(self):
        """Test adding templates to the container."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Test template",
        )

        self.prompt.add_template(template)
        self.assertEqual(len(self.prompt.templates), 1)
        self.assertIn("test_template", self.prompt)

    def test_get_template(self):
        """Test retrieving templates from the container."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Test template",
        )

        self.prompt.add_template(template)
        retrieved = self.prompt.get_template("test_template")

        self.assertIs(retrieved, template)
        self.assertIsNone(self.prompt.get_template("nonexistent"))

    def test_render_template(self):
        """Test rendering templates through the container."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues",
        )

        self.prompt.add_template(template)
        rendered = self.prompt.render_template("test_template", {"num": 5})

        self.assertEqual(rendered, "Generate 5 issues")

    def test_list_templates(self):
        """Test listing templates."""
        template1 = PromptTemplate(
            "template1", PromptType.ISSUE_GENERATION, "Test 1"
        )
        template2 = PromptTemplate(
            "template2", PromptType.CODE_ANALYSIS, "Test 2"
        )

        self.prompt.add_template(template1)
        self.prompt.add_template(template2)

        all_templates = self.prompt.list_templates()
        self.assertEqual(set(all_templates), {"template1", "template2"})

        issue_templates = self.prompt.list_templates(
            PromptType.ISSUE_GENERATION
        )
        self.assertEqual(issue_templates, ["template1"])

    def test_create_builtin_templates(self):
        """Test creation of built-in templates."""
        self.prompt.create_builtin_templates()

        self.assertGreater(len(self.prompt.templates), 0)
        self.assertIn("basic_issue_generation", self.prompt)


class TestLLMBackend(unittest.TestCase):
    """Test LLM backend functionality."""

    def test_ollama_backend_init(self):
        """Test OllamaBackend initialization."""
        config = {"host": "localhost", "port": 11434, "model": "llama2"}

        backend = OllamaBackend(config)

        self.assertEqual(backend.host, "localhost")
        self.assertEqual(backend.port, 11434)
        self.assertEqual(backend.model, "llama2")
        self.assertEqual(backend.base_url, "http://localhost:11434")

    @patch("src.ticket_master.llm.requests.get")
    def test_ollama_is_available(self, mock_get):
        """Test Ollama availability check."""
        backend = OllamaBackend({"host": "localhost", "port": 11434})

        # Test available
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertTrue(backend.is_available())

        # Test not available (reset mock and set side effect)
        mock_get.reset_mock()
        mock_get.side_effect = Exception("Connection failed")
        self.assertFalse(backend.is_available())


class TestLLM(unittest.TestCase):
    """Test LLM main class functionality."""

    def test_init_with_string_provider(self):
        """Test LLM initialization with string provider."""
        config = {"host": "localhost", "model": "test"}
        llm = LLM("ollama", config)

        self.assertEqual(llm.provider, LLMProvider.OLLAMA)
        self.assertEqual(llm.metadata["provider"], "ollama")

    def test_init_with_enum_provider(self):
        """Test LLM initialization with enum provider."""
        config = {"host": "localhost", "model": "test"}
        llm = LLM(LLMProvider.OLLAMA, config)

        self.assertEqual(llm.provider, LLMProvider.OLLAMA)

    def test_init_invalid_provider(self):
        """Test LLM initialization with invalid provider."""
        config = {"model": "test"}

        with self.assertRaises(LLMError):
            LLM("invalid_provider", config)

    def test_metadata(self):
        """Test LLM metadata."""
        config = {"model": "test_model"}
        llm = LLM(LLMProvider.OLLAMA, config)

        metadata = llm.get_metadata()
        self.assertEqual(metadata["provider"], "ollama")
        self.assertEqual(metadata["model"], "test_model")
        self.assertIn("initialized_at", metadata)


class TestPipelineStep(unittest.TestCase):
    """Test PipelineStep functionality."""

    def setUp(self):
        """Set up test pipeline step."""
        self.mock_llm = Mock()
        self.mock_llm.provider.value = "ollama"
        self.mock_llm.generate.return_value = {
            "response": "Generated response",
            "metadata": {"provider": "ollama"},
        }

    def test_init(self):
        """Test PipelineStep initialization."""
        template = PromptTemplate(
            "test", PromptType.ISSUE_GENERATION, "Test {value}"
        )
        step = PipelineStep("test_step", self.mock_llm, template)

        self.assertEqual(step.name, "test_step")
        self.assertEqual(step.stage, PipeStage.INTERMEDIATE)

    def test_execute_basic(self):
        """Test basic step execution."""
        template = PromptTemplate(
            "test", PromptType.ISSUE_GENERATION, "Generate {count} issues"
        )
        step = PipelineStep("test_step", self.mock_llm, template)

        variables = {"count": 3}
        result = step.execute(variables)

        self.assertTrue(result["success"])
        self.assertEqual(result["response"], "Generated response")
        self.assertEqual(result["step_name"], "test_step")


class TestPipe(unittest.TestCase):
    """Test Pipe functionality."""

    def setUp(self):
        """Set up test pipeline."""
        self.mock_input_llm = Mock()
        self.mock_input_llm.provider.value = "ollama"
        self.mock_input_llm.generate.return_value = {
            "response": "Input response",
            "metadata": {"provider": "ollama"},
        }

        self.mock_output_llm = Mock()
        self.mock_output_llm.provider.value = "openai"
        self.mock_output_llm.generate.return_value = {
            "response": "Output response",
            "metadata": {"provider": "openai"},
        }

    def test_init(self):
        """Test Pipe initialization."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)

        self.assertEqual(pipe.name, "test_pipeline")
        self.assertEqual(len(pipe.steps), 0)

    def test_add_step(self):
        """Test adding steps to pipeline."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template, PipeStage.INPUT)

        self.assertEqual(len(pipe.steps), 1)
        self.assertEqual(pipe.steps[0].name, "step1")
        self.assertEqual(pipe.steps[0].stage, PipeStage.INPUT)

    def test_validate_pipeline(self):
        """Test pipeline validation."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)

        validation = pipe.validate_pipeline()
        self.assertFalse(validation["is_valid"])  # No steps
        self.assertIn("Pipeline has no steps", validation["issues"])


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
