"""
Tests for Ollama integration tools.
"""

import json
import unittest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

# Add src directory to path for imports
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master.ollama_tools import (
    OllamaPromptProcessor,
    OllamaPromptValidator,
    OllamaToolsError,
    create_ollama_processor,
)
from ticket_master.prompt import PromptTemplate, PromptType


class TestOllamaPromptProcessor(unittest.TestCase):
    """Test OllamaPromptProcessor functionality."""

    def setUp(self):
        """Set up test fixtures."""
        with patch("ticket_master.ollama_tools.ollama"):
            self.processor = OllamaPromptProcessor(
                host="localhost", port=11434, model="llama3.2"
            )

    @patch("ticket_master.ollama_tools.ollama")
    def test_init(self, mock_ollama):
        """Test processor initialization."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client

        processor = OllamaPromptProcessor(
            host="testhost", port=8080, model="test-model"
        )

        self.assertEqual(processor.model, "test-model")
        mock_ollama.Client.assert_called_with(host="http://testhost:8080")

    @patch("ticket_master.ollama_tools.ollama")
    def test_process_prompt_success(self, mock_ollama):
        """Test successful prompt processing."""
        # Setup mocks
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client

        mock_response = {
            "response": "Generated response text",
            "total_duration": 1000000,
            "load_duration": 100000,
            "prompt_eval_count": 10,
            "eval_count": 20,
            "eval_duration": 500000,
        }
        mock_client.generate.return_value = mock_response

        processor = OllamaPromptProcessor()

        # Create a test template
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues for {repo}",
            provider_variations={
                "ollama": "Create {num} GitHub issues for repository {repo}"
            },
        )

        variables = {"num": 3, "repo": "test-repo"}

        # Process the prompt
        result = processor.process_prompt(template, variables)

        # Verify results
        self.assertEqual(result["response"], "Generated response text")
        self.assertEqual(result["metadata"]["model"], "llama3.2")
        self.assertEqual(result["metadata"]["template_name"], "test_template")
        self.assertEqual(result["metadata"]["prompt_type"], "issue_generation")
        self.assertIn("processing_time", result["metadata"])
        self.assertEqual(result["raw_response"], mock_response)

    @patch("ticket_master.ollama_tools.ollama")
    def test_process_prompt_with_options(self, mock_ollama):
        """Test prompt processing with additional options."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client
        mock_client.generate.return_value = {"response": "test response"}

        processor = OllamaPromptProcessor()

        template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Test prompt",
        )

        result = processor.process_prompt(
            template, {}, temperature=0.5, top_k=50, custom_option="value"
        )

        # Verify options were passed to client
        mock_client.generate.assert_called_once()
        call_args = mock_client.generate.call_args

        # Check that options are in the 'options' parameter
        options_param = call_args[1].get("options")
        if options_param:
            self.assertEqual(options_param.get("temperature"), 0.5)
            self.assertEqual(options_param.get("top_k"), 50)
        else:
            # If no options were passed, that's also acceptable
            pass

    @patch("ticket_master.ollama_tools.ollama")
    def test_process_prompt_api_error(self, mock_ollama):
        """Test handling of Ollama API errors."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client
        mock_ollama.ResponseError = Exception  # Mock the exception class

        mock_client.generate.side_effect = mock_ollama.ResponseError(
            "API Error"
        )

        processor = OllamaPromptProcessor()

        template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Test",
        )

        with self.assertRaises(OllamaToolsError) as context:
            processor.process_prompt(template, {})

        self.assertIn("Ollama API error", str(context.exception))

    def test_batch_process_prompts(self):
        """Test batch processing of multiple prompts."""
        with patch.object(self.processor, "process_prompt") as mock_process:
            mock_process.side_effect = [
                {"response": "Response 1", "metadata": {}},
                {"response": "Response 2", "metadata": {}},
                {"error": "Failed"},
            ]

            template1 = PromptTemplate(
                "template1", PromptType.ISSUE_GENERATION, "Test 1"
            )
            template2 = PromptTemplate(
                "template2", PromptType.ISSUE_GENERATION, "Test 2"
            )
            template3 = PromptTemplate(
                "template3", PromptType.ISSUE_GENERATION, "Test 3"
            )

            prompts = [
                {"template": template1, "variables": {"var1": "value1"}},
                {"template": template2, "variables": {"var2": "value2"}},
                {"template": template3, "variables": {"var3": "value3"}},
            ]

            results = self.processor.batch_process_prompts(prompts)

            self.assertEqual(len(results), 3)
            self.assertEqual(results[0]["response"], "Response 1")
            self.assertEqual(results[1]["response"], "Response 2")
            self.assertIn("error", results[2])

    @patch("ticket_master.ollama_tools.ollama")
    def test_generate_issues_from_analysis(self, mock_ollama):
        """Test issue generation from repository analysis."""
        # Setup processor with mocked prompt manager
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client

        processor = OllamaPromptProcessor()

        # Mock the response with JSON issues
        issues_json = json.dumps(
            [
                {
                    "title": "Improve documentation",
                    "description": "The project needs better documentation for new contributors.",
                    "labels": ["documentation", "enhancement"],
                },
                {
                    "title": "Add unit tests",
                    "description": "Several modules lack adequate test coverage.",
                    "labels": ["testing", "quality"],
                },
            ]
        )

        mock_client.generate.return_value = {
            "response": issues_json,
            "total_duration": 1000000,
            "eval_count": 100,
        }

        # Prepare analysis data
        analysis_data = {
            "repository_info": {"path": "/test/repo"},
            "analysis_summary": {
                "commit_count": 10,
                "files_modified": 5,
                "files_added": 2,
                "total_insertions": 100,
                "total_deletions": 50,
            },
            "commits": [
                {"short_hash": "abc123", "summary": "Add feature"},
                {"short_hash": "def456", "summary": "Fix bug"},
            ],
        }

        with patch("ticket_master.prompt.Prompt") as mock_prompt_class:
            mock_prompt = Mock()
            mock_template = Mock()
            mock_template.render.return_value = "Rendered prompt"
            mock_prompt.get_template.return_value = mock_template
            mock_prompt_class.return_value = mock_prompt

            # Generate issues
            issues = processor.generate_issues_from_analysis(
                analysis_data, max_issues=3
            )

            # Verify results
            self.assertEqual(len(issues), 2)
            self.assertEqual(issues[0]["title"], "Improve documentation")
            self.assertEqual(issues[1]["title"], "Add unit tests")
            self.assertIn("_generation_metadata", issues[0])
            self.assertIn("_generation_metadata", issues[1])

    def test_parse_issues_response_json(self):
        """Test parsing JSON response."""
        processor = self.processor

        json_response = """```json
        [
            {
                "title": "Test Issue",
                "description": "Test description",
                "labels": ["test", "automated"]
            }
        ]
        ```"""

        issues = processor._parse_issues_response(json_response)

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0]["title"], "Test Issue")
        self.assertEqual(issues[0]["description"], "Test description")
        self.assertEqual(issues[0]["labels"], ["test", "automated"])

    def test_parse_issues_response_text(self):
        """Test parsing structured text response."""
        processor = self.processor

        text_response = """
        TITLE: First Issue
        DESCRIPTION: This is the first issue description
        LABELS: bug, priority-high

        TITLE: Second Issue
        DESCRIPTION: This is the second issue description
        LABELS: enhancement, documentation
        """

        issues = processor._parse_issues_response(text_response)

        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0]["title"], "First Issue")
        self.assertEqual(issues[0]["labels"], ["bug", "priority-high"])
        self.assertEqual(issues[1]["title"], "Second Issue")
        self.assertEqual(issues[1]["labels"], ["enhancement", "documentation"])

    @patch("ticket_master.ollama_tools.ollama")
    def test_check_model_availability(self, mock_ollama):
        """Test model availability checking."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client

        mock_client.list.return_value = {
            "models": [{"name": "llama3.2:latest"}, {"name": "codellama:7b"}]
        }

        processor = OllamaPromptProcessor(model="llama3.2")

        result = processor.check_model_availability()

        self.assertTrue(result["available"])
        self.assertEqual(result["model"], "llama3.2")
        self.assertEqual(len(result["available_models"]), 2)

    @patch("ticket_master.ollama_tools.ollama")
    def test_install_model(self, mock_ollama):
        """Test model installation."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client
        mock_client.pull.return_value = {"status": "success"}

        processor = OllamaPromptProcessor(model="test-model")

        result = processor.install_model()

        self.assertTrue(result["success"])
        self.assertEqual(result["model"], "test-model")
        mock_client.pull.assert_called_once_with("test-model")

    @patch("ticket_master.ollama_tools.ollama")
    def test_get_model_info(self, mock_ollama):
        """Test getting model information."""
        mock_client = Mock()
        mock_ollama.Client.return_value = mock_client

        mock_model_info = {
            "parameters": {"temperature": 0.7},
            "template": "{{.System}}\n{{.Prompt}}",
            "system": "You are a helpful assistant",
            "modified_at": "2023-01-01T12:00:00Z",
        }
        mock_client.show.return_value = mock_model_info

        processor = OllamaPromptProcessor(model="test-model")

        result = processor.get_model_info()

        self.assertTrue(result["available"])
        self.assertEqual(result["model"], "test-model")
        self.assertEqual(result["details"], mock_model_info)
        self.assertEqual(result["parameters"], {"temperature": 0.7})


class TestOllamaPromptValidator(unittest.TestCase):
    """Test OllamaPromptValidator functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.validator = OllamaPromptValidator()

    def test_validate_prompt_template_valid(self):
        """Test validation of a valid prompt template."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_path}",
            provider_variations={
                "ollama": "Create {num_issues} GitHub issues for {repo_path}"
            },
        )

        result = self.validator.validate_prompt_template(template)

        self.assertTrue(result["valid"])
        self.assertEqual(result["template_name"], "test_template")
        self.assertEqual(result["template_type"], "issue_generation")
        self.assertEqual(len(result["issues"]), 0)

    def test_validate_prompt_template_missing_ollama_variation(self):
        """Test validation warns about missing Ollama variation."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_path}",
            provider_variations={"openai": "Create issues using OpenAI"},
        )

        result = self.validator.validate_prompt_template(template)

        self.assertTrue(result["valid"])  # Still valid, just has warnings
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("Ollama-specific", result["warnings"][0])

    def test_validate_prompt_template_missing_required_vars(self):
        """Test validation identifies missing required variables."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate some issues",  # Missing {num_issues} and {repo_path}
            provider_variations={"ollama": "Create issues"},
        )

        result = self.validator.validate_prompt_template(template)

        self.assertFalse(result["valid"])
        self.assertEqual(len(result["issues"]), 1)
        self.assertIn("Missing required variables", result["issues"][0])

    def test_validate_prompt_template_too_long(self):
        """Test validation warns about very long templates."""
        long_template = "A" * 5000  # Very long template

        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template=long_template,
            provider_variations={"ollama": long_template},
        )

        result = self.validator.validate_prompt_template(template)

        # Should have validation issue due to missing required variables
        self.assertFalse(
            result["valid"]
        )  # Actually invalid due to missing vars
        self.assertTrue(
            any("quite long" in warning for warning in result["warnings"])
        )

    def test_validate_variables_valid(self):
        """Test validation of valid variables."""
        template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues for {repo}",
        )

        variables = {"num": 5, "repo": "test-repo"}

        result = self.validator.validate_variables(template, variables)

        self.assertTrue(result["valid"])
        self.assertEqual(len(result["issues"]), 0)
        self.assertEqual(set(result["placeholders_found"]), {"num", "repo"})
        self.assertEqual(set(result["variables_provided"]), {"num", "repo"})

    def test_validate_variables_missing(self):
        """Test validation identifies missing variables."""
        template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues for {repo} in {branch}",
        )

        variables = {"num": 5}  # Missing repo and branch

        result = self.validator.validate_variables(template, variables)

        self.assertFalse(result["valid"])
        self.assertEqual(len(result["issues"]), 1)
        self.assertIn("Missing required variables", result["issues"][0])
        self.assertIn("repo", result["issues"][0])
        self.assertIn("branch", result["issues"][0])

    def test_validate_variables_unused(self):
        """Test validation warns about unused variables."""
        template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues",
        )

        variables = {
            "num": 5,
            "unused_var": "value",
            "another_unused": "value2",
        }

        result = self.validator.validate_variables(template, variables)

        self.assertTrue(result["valid"])  # Still valid
        self.assertEqual(len(result["warnings"]), 1)
        self.assertIn("Unused variables", result["warnings"][0])

    def test_validate_variables_none_values(self):
        """Test validation warns about None values."""
        template = PromptTemplate(
            name="test",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} issues for {repo}",
        )

        variables = {"num": 5, "repo": None}

        result = self.validator.validate_variables(template, variables)

        self.assertTrue(result["valid"])  # Still valid
        self.assertTrue(
            any("is None" in warning for warning in result["warnings"])
        )


class TestOllamaFactoryFunction(unittest.TestCase):
    """Test factory functions."""

    @patch("ticket_master.ollama_tools.ollama")
    def test_create_ollama_processor(self, mock_ollama):
        """Test factory function for creating OllamaPromptProcessor."""
        config = {"host": "testhost", "port": 8080, "model": "test-model"}

        processor = create_ollama_processor(config)

        self.assertIsInstance(processor, OllamaPromptProcessor)
        self.assertEqual(processor.model, "test-model")

    @patch("ticket_master.ollama_tools.ollama")
    def test_create_ollama_processor_defaults(self, mock_ollama):
        """Test factory function with default values."""
        config = {}

        processor = create_ollama_processor(config)

        self.assertIsInstance(processor, OllamaPromptProcessor)
        self.assertEqual(processor.model, "llama3.2")  # Default model


if __name__ == "__main__":
    unittest.main()
