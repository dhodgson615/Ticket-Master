import logging
import time
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

# TODO: Consider using a more robust dependency management approach
# such as poetry or pipenv for better handling of dependencies.
try:
    from llm import LLM as LLM
except ImportError:
    from llm import LLM as LLM

try:
    from prompt import Prompt as Prompt
    from prompt import PromptTemplate as PromptTemplate
except ImportError:
    from prompt import Prompt as Prompt
    from prompt import PromptTemplate as PromptTemplate


class PipeError(Exception):
    """Custom exception for pipe-related errors."""

    pass


class PipeValidationError(PipeError):
    """Exception for pipe validation errors."""

    pass


class PipeExecutionError(PipeError):
    """Exception for pipe execution errors."""

    pass


class PipeStage(Enum):
    """Stages in the LLM pipeline."""

    INPUT = "input"
    INTERMEDIATE = "intermediate"
    OUTPUT = "output"
    VALIDATION = "validation"


class PipelineStep:
    """Individual step in an LLM pipeline.

    This class represents a single step in the pipeline with an LLM,
    prompt template, and optional validation logic.

    Attributes:
        name: Step name
        llm: LLM instance for this step
        prompt_template: Prompt template to use
        stage: Pipeline stage this step belongs to
        validator: Optional validation function
        metadata: Step metadata
    """

    def __init__(
        self,
        name: str,
        llm: LLM,
        prompt_template: Union[str, PromptTemplate],
        stage: Union[PipeStage, str] = PipeStage.INTERMEDIATE,
        validator: Optional[
            Callable[[str, Dict[str, Any]], Dict[str, Any]]
        ] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a pipeline step.

        Args:
            name: Step name
            llm: LLM instance to use
            prompt_template: Prompt template name or PromptTemplate instance
            stage: Pipeline stage (input, intermediate, output, validation)
            validator: Optional validation function
            metadata: Optional step metadata

        Raises:
            PipeError: If step configuration is invalid
        """
        if not name or not name.strip():
            raise PipeError("Step name cannot be empty")

        if isinstance(stage, str):
            try:
                stage = PipeStage(stage.lower())
            except ValueError:
                raise PipeError(f"Invalid pipeline stage: {stage}")

        self.name = name.strip()
        self.llm = llm
        self.prompt_template = prompt_template
        self.stage = stage
        self.validator = validator
        self.metadata = metadata or {}
        self.logger = logging.getLogger(
            f"{self.__class__.__name__}.{self.name}"
        )

    def execute(
        self,
        variables: Dict[str, Any],
        prompt_manager: Optional[Prompt] = None,
        **llm_kwargs,
    ) -> Dict[str, Any]:
        """Execute this pipeline step.

        Args:
            variables: Variables for prompt template rendering
            prompt_manager: Optional prompt manager for template resolution
            **llm_kwargs: Additional arguments for LLM generation

        Returns:
            Dictionary containing step results and metadata

        Raises:
            PipeExecutionError: If step execution fails
        """
        try:
            start_time = time.time()

            # Resolve prompt template
            if isinstance(self.prompt_template, str):
                if not prompt_manager:
                    raise PipeExecutionError(
                        f"Prompt manager required for template '{self.prompt_template}'"
                    )

                template = prompt_manager.get_template(self.prompt_template)
                if not template:
                    raise PipeExecutionError(
                        f"Template '{self.prompt_template}' not found"
                    )
            else:
                template = self.prompt_template

            # Render prompt
            provider = self.llm.provider.value
            rendered_prompt = template.render(variables, provider)

            # Generate response
            response = self.llm.generate(rendered_prompt, **llm_kwargs)

            # Validate if validator is provided
            validation_result = None
            if self.validator:
                try:
                    validation_result = self.validator(
                        response["response"], variables
                    )
                except Exception as e:
                    self.logger.warning(
                        f"Validation failed for step '{self.name}': {e}"
                    )
                    validation_result = {"is_valid": False, "error": str(e)}

            execution_time = time.time() - start_time

            result = {
                "step_name": self.name,
                "stage": self.stage.value,
                "success": True,
                "response": response["response"],
                "llm_metadata": response["metadata"],
                "validation": validation_result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }

            self.logger.info(
                f"Successfully executed step '{self.name}' in {execution_time:.2f}s"
            )
            return result

        except Exception as e:
            error_result = {
                "step_name": self.name,
                "stage": self.stage.value,
                "success": False,
                "error": str(e),
                "execution_time": (
                    time.time() - start_time if "start_time" in locals() else 0
                ),
                "timestamp": datetime.now().isoformat(),
            }
            self.logger.error(f"Step '{self.name}' failed: {e}")
            raise PipeExecutionError(f"Step '{self.name}' failed: {e}") from e

    def __str__(self) -> str:
        """String representation of the step."""
        return f"PipelineStep(name='{self.name}', stage={self.stage.value})"


class Pipe:
    """Main class for LLM pipeline operations and orchestration.

    This class provides a way to "daisy chain" LLM outputs with proper error
    handling, allowing complex multi-step operations with input LLM, output LLM,
    and optional intermediate verification steps.

    Attributes:
        name: Pipeline name
        input_llm: LLM for input processing
        output_llm: LLM for output generation
        intermediate_llm: Optional LLM for intermediate verification
        steps: List of pipeline steps
        prompt_manager: Prompt manager for template resolution
        metadata: Pipeline metadata
        logger: Logger instance
    """

    def __init__(
        self,
        name: str,
        input_llm: LLM,
        output_llm: LLM,
        intermediate_llm: Optional[LLM] = None,
        prompt_manager: Optional[Prompt] = None,
    ) -> None:
        """Initialize the pipeline.

        Args:
            name: Pipeline name
            input_llm: LLM for input processing
            output_llm: LLM for output generation
            intermediate_llm: Optional LLM for intermediate verification
            prompt_manager: Optional prompt manager

        Raises:
            PipeError: If pipeline configuration is invalid
        """
        if not name or not name.strip():
            raise PipeError("Pipeline name cannot be empty")

        self.name = name.strip()
        self.input_llm = input_llm
        self.output_llm = output_llm
        self.intermediate_llm = intermediate_llm
        self.prompt_manager = prompt_manager or Prompt()
        self.steps: List[PipelineStep] = []
        self.metadata = {
            "created_at": datetime.now().isoformat(),
            "input_llm": str(input_llm),
            "output_llm": str(output_llm),
            "intermediate_llm": (
                str(intermediate_llm) if intermediate_llm else None
            ),
        }
        self.logger = logging.getLogger(
            f"{self.__class__.__name__}.{self.name}"
        )

    def add_step(
        self,
        name: str,
        llm: Optional[LLM] = None,
        prompt_template: Union[str, PromptTemplate] = None,
        stage: Union[PipeStage, str] = PipeStage.INTERMEDIATE,
        validator: Optional[
            Callable[[str, Dict[str, Any]], Dict[str, Any]]
        ] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> "Pipe":
        """Add a step to the pipeline.

        Args:
            name: Step name
            llm: LLM to use (defaults to appropriate pipeline LLM based on stage)
            prompt_template: Prompt template to use
            stage: Pipeline stage
            validator: Optional validation function
            metadata: Optional step metadata

        Returns:
            Self for method chaining

        Raises:
            PipeError: If step configuration is invalid
        """
        # Auto-select LLM based on stage if not provided
        if llm is None:
            if isinstance(stage, str):
                stage = PipeStage(stage.lower())

            if stage == PipeStage.INPUT:
                llm = self.input_llm

            elif stage == PipeStage.OUTPUT:
                llm = self.output_llm

            elif stage == PipeStage.VALIDATION and self.intermediate_llm:
                llm = self.intermediate_llm

            else:
                llm = self.intermediate_llm or self.input_llm

        step = PipelineStep(
            name, llm, prompt_template, stage, validator, metadata
        )

        self.steps.append(step)

        self.logger.info(f"Added step '{name}' at stage {stage}")
        return self

    def execute(
        self,
        initial_variables: Dict[str, Any],
        stop_on_error: bool = True,
        validate_intermediate: bool = True,
        **llm_kwargs,
    ) -> Dict[str, Any]:
        """Execute the complete pipeline.

        Args:
            initial_variables: Initial variables for the pipeline
            stop_on_error: Whether to stop execution on first error
            validate_intermediate: Whether to validate intermediate results
            **llm_kwargs: Additional arguments for LLM generation

        Returns:
            Dictionary containing pipeline results and metadata

        Raises:
            PipeExecutionError: If pipeline execution fails and stop_on_error is True
        """
        if not self.steps:
            raise PipeExecutionError("Pipeline has no steps to execute")

        start_time = time.time()
        pipeline_result = {
            "pipeline_name": self.name,
            "success": True,
            "steps": [],
            "variables": initial_variables.copy(),
            "errors": [],
            "start_time": datetime.now().isoformat(),
        }

        self.logger.info(
            f"Starting pipeline '{self.name}' with {len(self.steps)} steps"
        )

        # Execute steps in order
        current_variables = initial_variables.copy()

        for i, step in enumerate(self.steps):
            try:
                self.logger.debug(
                    f"Executing step {i + 1}/{len(self.steps)}: {step.name}"
                )

                # Execute step
                step_result = step.execute(
                    current_variables, self.prompt_manager, **llm_kwargs
                )

                pipeline_result["steps"].append(step_result)

                # Update variables with step output
                if step_result["success"]:
                    # Add step output to variables for next step
                    step_output_key = f"{step.name}_output"

                    current_variables[step_output_key] = step_result[
                        "response"
                    ]

                    # For output stage, also set as final output
                    if step.stage == PipeStage.OUTPUT:
                        current_variables["final_output"] = step_result[
                            "response"
                        ]

                    # Validate intermediate results if enabled
                    if (
                        validate_intermediate
                        and step.stage == PipeStage.INTERMEDIATE
                    ):
                        validation = step_result.get("validation")
                        if validation and not validation.get("is_valid", True):
                            error_msg = f"Intermediate validation failed for step '{step.name}'"
                            self.logger.warning(error_msg)

                            if stop_on_error:
                                raise PipeExecutionError(error_msg)

                            else:
                                pipeline_result["errors"].append(error_msg)

                else:
                    # Step failed
                    error_msg = f"Step '{step.name}' failed"
                    pipeline_result["errors"].append(error_msg)

                    if stop_on_error:
                        pipeline_result["success"] = False
                        break

            except Exception as e:
                error_msg = f"Pipeline step '{step.name}' failed: {e}"
                pipeline_result["errors"].append(error_msg)
                self.logger.error(error_msg)

                if stop_on_error:
                    pipeline_result["success"] = False
                    break

        # Update final results
        pipeline_result["variables"] = current_variables
        pipeline_result["execution_time"] = (
            time.time() - start_time
        )  # TODO: fix type
        pipeline_result["end_time"] = datetime.now().isoformat()

        # Pipeline succeeds if no errors or if we're not stopping on errors
        if not stop_on_error:
            pipeline_result["success"] = all(
                step.get("success", False) for step in pipeline_result["steps"]
            )

        if pipeline_result["success"]:
            self.logger.info(
                f"Pipeline '{self.name}' completed successfully in "
                f"{pipeline_result['execution_time']:.2f}s"
            )

        else:
            self.logger.error(
                f"Pipeline '{self.name}' failed with "
                f"{len(pipeline_result['errors'])} errors"
            )

        return pipeline_result

    def validate_pipeline(self) -> Dict[str, Any]:
        """Validate the pipeline configuration.

        Returns:
            Dictionary containing validation results
        """
        validation = {
            "is_valid": True,
            "issues": [],
            "warnings": [],
            "step_count": len(self.steps),
            "stages": {},
        }

        # Count steps by stage
        for stage in PipeStage:
            stage_steps = [step for step in self.steps if step.stage == stage]
            validation["stages"][stage.value] = len(stage_steps)

        # Check for common issues
        if not self.steps:
            validation["is_valid"] = False
            validation["issues"].append("Pipeline has no steps")

        # Check for input/output balance
        input_steps = validation["stages"].get("input", 0)
        output_steps = validation["stages"].get("output", 0)

        if input_steps == 0:
            validation["warnings"].append("No input steps defined")

        if output_steps == 0:
            validation["warnings"].append("No output steps defined")

        if output_steps > 1:
            validation["warnings"].append(
                "Multiple output steps may cause conflicts"
            )

        # Check LLM availability
        llms_to_check = [self.input_llm, self.output_llm]

        if self.intermediate_llm:
            llms_to_check.append(self.intermediate_llm)

        unavailable_llms = []
        for llm in llms_to_check:
            if not llm.is_available():
                unavailable_llms.append(str(llm))

        if unavailable_llms:
            validation["warnings"].append(
                f"LLMs not available: {unavailable_llms}"
            )

        return validation

    def get_step_names(self) -> List[str]:
        """Get list of step names in execution order.

        Returns:
            List of step names
        """
        return [step.name for step in self.steps]

    def get_steps_by_stage(self, stage: PipeStage) -> List[PipelineStep]:
        """Get steps filtered by stage.

        Args:
            stage: Pipeline stage to filter by

        Returns:
            List of pipeline steps for the given stage
        """
        return [step for step in self.steps if step.stage == stage]

    def remove_step(self, name: str) -> bool:
        """Remove a step from the pipeline.

        Args:
            name: Name of step to remove

        Returns:
            True if step was removed, False if not found
        """
        for i, step in enumerate(self.steps):
            if step.name == name:
                del self.steps[i]
                self.logger.info(f"Removed step '{name}' from pipeline")
                return True

        return False

    def clear_steps(self) -> None:
        """Remove all steps from the pipeline."""
        self.steps.clear()
        self.logger.info("Cleared all steps from pipeline")

    def to_dict(self) -> Dict[str, Any]:
        """Convert pipeline to dictionary for serialization.

        Returns:
            Dictionary representation of the pipeline
        """
        return {
            "name": self.name,
            "metadata": self.metadata,
            "steps": [
                {
                    "name": step.name,
                    "stage": step.stage.value,
                    "prompt_template": (
                        step.prompt_template.name
                        if isinstance(step.prompt_template, PromptTemplate)
                        else step.prompt_template
                    ),
                    "metadata": step.metadata,
                }
                for step in self.steps
            ],
            "validation": self.validate_pipeline(),
        }

    def __len__(self) -> int:
        """Return number of steps in the pipeline."""
        return len(self.steps)

    def __str__(self) -> str:
        """String representation of the pipeline."""
        return f"Pipe(name='{self.name}', steps={len(self.steps)})"

    def __repr__(self) -> str:
        """Developer representation of the pipeline."""
        stages = {}
        for step in self.steps:
            stage = step.stage.value
            stages[stage] = stages.get(stage, 0) + 1

        return (
            f"Pipe(name='{self.name}', steps={len(self.steps)}, "
            f"stages={stages})"
        )
