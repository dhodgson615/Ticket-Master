"""
Test module for pipe classes: Pipe, PipelineStep, and related components.

This module provides comprehensive tests for pipeline functionality
including step execution, validation, and stage management.
"""

import unittest
from unittest.mock import Mock

from src.ticket_master.pipe import Pipe, PipeError, PipelineStep, PipeStage
from src.ticket_master.prompt import PromptTemplate, PromptType


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


if __name__ == "__main__":
    unittest.main()
