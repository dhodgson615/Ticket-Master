"""
Test module for pipe classes: Pipe, PipelineStep, and related components.

This module provides comprehensive tests for pipeline functionality
including step execution, validation, and stage management.
"""

import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

# TODO: remove once src is a package
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.ticket_master_consolidated import (Pipe, PipeError,
                                            PipeExecutionError, PipelineStep,
                                            PipeStage, PipeValidationError,
                                            PromptTemplate, PromptType)


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
        self.assertEqual(step.template, template)
        self.assertEqual(step.llm, self.mock_llm)

    def test_init_with_custom_stage(self):
        """Test PipelineStep initialization with custom stage."""
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
        step = PipelineStep(
            "test_step", self.mock_llm, template, PipeStage.INPUT
        )

        self.assertEqual(step.stage, PipeStage.INPUT)

    def test_init_with_validation_function(self):
        """Test PipelineStep initialization with validation function."""
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        def custom_validator(result):
            return result.get("response") is not None

        step = PipelineStep(
            "test_step",
            self.mock_llm,
            template,
            validation_fn=custom_validator,
        )

        self.assertEqual(step.validation_fn, custom_validator)

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
        self.assertIn("execution_time", result)
        self.assertIn("timestamp", result)

    def test_execute_with_validation_success(self):
        """Test step execution with successful validation."""
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        def validator(result):
            return result.get("response") == "Generated response"

        step = PipelineStep(
            "test_step", self.mock_llm, template, validation_fn=validator
        )

        result = step.execute({})

        self.assertTrue(result["success"])
        self.assertTrue(result["validation_passed"])

    def test_execute_with_validation_failure(self):
        """Test step execution with failed validation."""
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        def validator(result):
            return False  # Always fail

        step = PipelineStep(
            "test_step", self.mock_llm, template, validation_fn=validator
        )

        result = step.execute({})

        self.assertTrue(result["success"])  # Execution succeeds
        self.assertFalse(result["validation_passed"])  # But validation fails

    def test_execute_with_llm_error(self):
        """Test step execution when LLM raises an error."""
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
        self.mock_llm.generate.side_effect = Exception("LLM Error")

        step = PipelineStep("test_step", self.mock_llm, template)

        result = step.execute({})

        self.assertFalse(result["success"])
        self.assertIn("error", result)
        self.assertEqual(result["step_name"], "test_step")

    def test_execute_with_validation_exception(self):
        """Test step execution when validation function raises exception."""
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        def faulty_validator(result):
            raise ValueError("Validation error")

        step = PipelineStep(
            "test_step",
            self.mock_llm,
            template,
            validation_fn=faulty_validator,
        )

        result = step.execute({})

        self.assertTrue(result["success"])  # Execution succeeds
        self.assertFalse(
            result["validation_passed"]
        )  # Validation fails due to exception

    def test_str_method(self):
        """Test __str__ method."""
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")
        step = PipelineStep(
            "test_step", self.mock_llm, template, PipeStage.INPUT
        )

        str_repr = str(step)
        self.assertIn("test_step", str_repr)
        self.assertIn("INPUT", str_repr)


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
        self.assertEqual(pipe.input_llm, self.mock_input_llm)
        self.assertEqual(pipe.output_llm, self.mock_output_llm)

    def test_init_with_optional_params(self):
        """Test Pipe initialization with optional parameters."""
        pipe = Pipe(
            "test_pipeline",
            self.mock_input_llm,
            self.mock_output_llm,
            description="Test description",
            max_steps=10,
        )

        self.assertEqual(pipe.description, "Test description")
        self.assertEqual(pipe.max_steps, 10)

    def test_add_step(self):
        """Test adding steps to pipeline."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template, PipeStage.INPUT)

        self.assertEqual(len(pipe.steps), 1)
        self.assertEqual(pipe.steps[0].name, "step1")
        self.assertEqual(pipe.steps[0].stage, PipeStage.INPUT)

    def test_add_step_with_validation(self):
        """Test adding step with validation function."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        def validator(result):
            return True

        pipe.add_step(
            "step1", self.mock_input_llm, template, validation_fn=validator
        )

        self.assertEqual(len(pipe.steps), 1)
        self.assertEqual(pipe.steps[0].validation_fn, validator)

    def test_add_step_duplicate_name(self):
        """Test adding step with duplicate name."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template)

        with self.assertRaises(PipeValidationError):
            pipe.add_step("step1", self.mock_input_llm, template)

    def test_add_step_max_steps_exceeded(self):
        """Test adding step when max steps is exceeded."""
        pipe = Pipe(
            "test_pipeline",
            self.mock_input_llm,
            self.mock_output_llm,
            max_steps=1,
        )
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template)

        with self.assertRaises(PipeValidationError):
            pipe.add_step("step2", self.mock_input_llm, template)

    def test_execute_empty_pipeline(self):
        """Test executing empty pipeline."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)

        with self.assertRaises(PipeExecutionError):
            pipe.execute({})

    def test_execute_single_step(self):
        """Test executing pipeline with single step."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template)

        result = pipe.execute({})

        self.assertTrue(result["success"])
        self.assertEqual(len(result["step_results"]), 1)
        self.assertIn("execution_time", result)
        self.assertIn("timestamp", result)

    def test_execute_multiple_steps(self):
        """Test executing pipeline with multiple steps."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template1 = PromptTemplate(
            "test1", PromptType.ISSUE_GENERATION, "Test 1"
        )
        template2 = PromptTemplate(
            "test2", PromptType.ISSUE_GENERATION, "Test 2"
        )

        pipe.add_step("step1", self.mock_input_llm, template1, PipeStage.INPUT)
        pipe.add_step(
            "step2", self.mock_output_llm, template2, PipeStage.OUTPUT
        )

        result = pipe.execute({})

        self.assertTrue(result["success"])
        self.assertEqual(len(result["step_results"]), 2)

    def test_execute_with_step_failure(self):
        """Test executing pipeline when step fails."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        # Make LLM fail
        self.mock_input_llm.generate.side_effect = Exception("LLM Error")

        pipe.add_step("step1", self.mock_input_llm, template)

        result = pipe.execute({})

        self.assertFalse(result["success"])
        self.assertIn("error", result)

    def test_validate_pipeline(self):
        """Test pipeline validation."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)

        validation = pipe.validate_pipeline()
        self.assertFalse(validation["is_valid"])  # No steps
        self.assertIn("Pipeline has no steps", validation["issues"])

    def test_validate_pipeline_with_steps(self):
        """Test pipeline validation with valid steps."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template, PipeStage.INPUT)
        pipe.add_step(
            "step2", self.mock_output_llm, template, PipeStage.OUTPUT
        )

        validation = pipe.validate_pipeline()
        self.assertTrue(validation["is_valid"])

    def test_validate_pipeline_missing_input_stage(self):
        """Test validation when INPUT stage is missing."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step(
            "step1", self.mock_output_llm, template, PipeStage.OUTPUT
        )

        validation = pipe.validate_pipeline()
        self.assertFalse(validation["is_valid"])
        self.assertIn("Missing INPUT stage", validation["issues"])

    def test_validate_pipeline_missing_output_stage(self):
        """Test validation when OUTPUT stage is missing."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template, PipeStage.INPUT)

        validation = pipe.validate_pipeline()
        self.assertFalse(validation["is_valid"])
        self.assertIn("Missing OUTPUT stage", validation["issues"])

    def test_get_step_names(self):
        """Test getting step names."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template)
        pipe.add_step("step2", self.mock_output_llm, template)

        names = pipe.get_step_names()
        self.assertEqual(names, ["step1", "step2"])

    def test_get_steps_by_stage(self):
        """Test getting steps by stage."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step(
            "input_step", self.mock_input_llm, template, PipeStage.INPUT
        )
        pipe.add_step(
            "output_step", self.mock_output_llm, template, PipeStage.OUTPUT
        )

        input_steps = pipe.get_steps_by_stage(PipeStage.INPUT)
        output_steps = pipe.get_steps_by_stage(PipeStage.OUTPUT)

        self.assertEqual(len(input_steps), 1)
        self.assertEqual(len(output_steps), 1)
        self.assertEqual(input_steps[0].name, "input_step")
        self.assertEqual(output_steps[0].name, "output_step")

    def test_remove_step(self):
        """Test removing a step."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template)
        pipe.add_step("step2", self.mock_output_llm, template)

        result = pipe.remove_step("step1")

        self.assertTrue(result)
        self.assertEqual(len(pipe.steps), 1)
        self.assertEqual(pipe.steps[0].name, "step2")

    def test_remove_step_nonexistent(self):
        """Test removing a non-existent step."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)

        result = pipe.remove_step("nonexistent")

        self.assertFalse(result)

    def test_clear_steps(self):
        """Test clearing all steps."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template)
        pipe.add_step("step2", self.mock_output_llm, template)

        pipe.clear_steps()

        self.assertEqual(len(pipe.steps), 0)

    def test_to_dict(self):
        """Test converting pipeline to dictionary."""
        pipe = Pipe(
            "test_pipeline",
            self.mock_input_llm,
            self.mock_output_llm,
            description="Test description",
        )
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        pipe.add_step("step1", self.mock_input_llm, template, PipeStage.INPUT)

        result = pipe.to_dict()

        self.assertEqual(result["name"], "test_pipeline")
        self.assertEqual(result["description"], "Test description")
        self.assertEqual(len(result["steps"]), 1)
        self.assertIn("input_llm_provider", result)
        self.assertIn("output_llm_provider", result)

    def test_len_method(self):
        """Test __len__ method."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)
        template = PromptTemplate("test", PromptType.ISSUE_GENERATION, "Test")

        self.assertEqual(len(pipe), 0)

        pipe.add_step("step1", self.mock_input_llm, template)
        self.assertEqual(len(pipe), 1)

    def test_str_method(self):
        """Test __str__ method."""
        pipe = Pipe("test_pipeline", self.mock_input_llm, self.mock_output_llm)

        str_repr = str(pipe)
        self.assertIn("test_pipeline", str_repr)
        self.assertIn("0 steps", str_repr)

    def test_repr_method(self):
        """Test __repr__ method."""
        pipe = Pipe(
            "test_pipeline",
            self.mock_input_llm,
            self.mock_output_llm,
            description="Test description",
        )

        repr_str = repr(pipe)
        self.assertIn("Pipe", repr_str)
        self.assertIn("test_pipeline", repr_str)


class TestPipeExceptions(unittest.TestCase):
    """Test pipe exception classes."""

    def test_pipe_error(self):
        """Test PipeError exception."""
        with self.assertRaises(PipeError):
            raise PipeError("Test error")

    def test_pipe_validation_error(self):
        """Test PipeValidationError exception."""
        with self.assertRaises(PipeValidationError):
            raise PipeValidationError("Validation error")

    def test_pipe_execution_error(self):
        """Test PipeExecutionError exception."""
        with self.assertRaises(PipeExecutionError):
            raise PipeExecutionError("Execution error")


class TestPipeStage(unittest.TestCase):
    """Test PipeStage enum."""

    def test_pipe_stage_values(self):
        """Test PipeStage enum values."""
        self.assertEqual(PipeStage.INPUT.value, "input")
        self.assertEqual(PipeStage.INTERMEDIATE.value, "intermediate")
        self.assertEqual(PipeStage.OUTPUT.value, "output")
        self.assertEqual(PipeStage.VALIDATION.value, "validation")


if __name__ == "__main__":
    unittest.main()
