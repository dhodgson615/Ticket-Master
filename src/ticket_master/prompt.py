"""
Prompt module for managing prompt templates and variations.

This module provides the Prompt class for managing different prompt templates
that each LLM model will receive in different parts of the pipeline to ensure
models behave as desired with provider-specific optimizations.
"""

import logging
import subprocess
import sys
from typing import Dict, List, Optional, Any, Union
from enum import Enum
from pathlib import Path
import json
from datetime import datetime

# Import with fallback installation
try:
    import yaml
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "PyYAML>=6.0.1"])
    import yaml


class PromptError(Exception):
    """Custom exception for prompt-related errors."""

    pass


class PromptTemplateError(PromptError):
    """Exception for prompt template errors."""

    pass


class PromptType(Enum):
    """Types of prompts supported by the system."""

    ISSUE_GENERATION = "issue_generation"
    ISSUE_DESCRIPTION = "issue_description"
    CODE_ANALYSIS = "code_analysis"
    COMMIT_ANALYSIS = "commit_analysis"
    VALIDATION = "validation"
    REFINEMENT = "refinement"
    CLASSIFICATION = "classification"


class PromptTemplate:
    """Individual prompt template with variations for different providers.

    This class represents a single prompt template that can have different
    variations optimized for specific LLM providers while maintaining
    the same core functionality.

    Attributes:
        name: Template name
        prompt_type: Type of prompt (from PromptType enum)
        base_template: Base template string with placeholders
        provider_variations: Provider-specific template variations
        metadata: Template metadata and configuration
    """

    def __init__(
        self,
        name: str,
        prompt_type: Union[PromptType, str],
        base_template: str,
        provider_variations: Optional[Dict[str, str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize a prompt template.

        Args:
            name: Template name
            prompt_type: Type of prompt
            base_template: Base template string with {placeholder} syntax
            provider_variations: Optional provider-specific variations
            metadata: Optional metadata (description, version, etc.)

        Raises:
            PromptTemplateError: If template is invalid
        """
        if not name or not name.strip():
            raise PromptTemplateError("Template name cannot be empty")

        if isinstance(prompt_type, str):
            try:
                prompt_type = PromptType(prompt_type.lower())
            except ValueError:
                raise PromptTemplateError(f"Invalid prompt type: {prompt_type}")

        if not base_template or not base_template.strip():
            raise PromptTemplateError("Base template cannot be empty")

        self.name = name.strip()
        self.prompt_type = prompt_type
        self.base_template = base_template.strip()
        self.provider_variations = provider_variations or {}
        self.metadata = metadata or {}
        self.logger = logging.getLogger(f"{self.__class__.__name__}.{self.name}")

        # Add creation timestamp to metadata
        if "created_at" not in self.metadata:
            self.metadata["created_at"] = datetime.now().isoformat()

    def render(self, variables: Dict[str, Any], provider: Optional[str] = None) -> str:
        """Render the prompt template with given variables.

        Args:
            variables: Dictionary of variables to substitute in template
            provider: Optional provider name for provider-specific variation

        Returns:
            Rendered prompt string

        Raises:
            PromptTemplateError: If rendering fails
        """
        try:
            # Choose the appropriate template
            template = self.base_template
            if provider and provider in self.provider_variations:
                template = self.provider_variations[provider]
                self.logger.debug(f"Using {provider}-specific template variation")

            # Render the template
            rendered = template.format(**variables)

            self.logger.debug(
                f"Successfully rendered template '{self.name}' for provider '{provider}'"
            )
            return rendered

        except KeyError as e:
            missing_var = str(e).strip("'\"")
            raise PromptTemplateError(
                f"Missing required variable '{missing_var}' for template '{self.name}'"
            )
        except Exception as e:
            raise PromptTemplateError(f"Failed to render template '{self.name}': {e}")

    def get_required_variables(self) -> List[str]:
        """Extract required variables from the template.

        Returns:
            List of required variable names
        """
        required_vars = set()

        # Check base template
        template_vars = self._extract_variables(self.base_template)
        required_vars.update(template_vars)

        # Check provider variations
        for variation in self.provider_variations.values():
            variation_vars = self._extract_variables(variation)
            required_vars.update(variation_vars)

        return sorted(list(required_vars))

    def _extract_variables(self, template: str) -> List[str]:
        """Extract variable names from a template string.

        Args:
            template: Template string to analyze

        Returns:
            List of variable names found in the template
        """
        import re

        # Find all {variable_name} patterns
        pattern = r"\{([^}]+)\}"
        matches = re.findall(pattern, template)
        return [match.strip() for match in matches]

    def validate(self, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Validate that all required variables are provided.

        Args:
            variables: Variables to validate

        Returns:
            Validation result dictionary
        """
        required_vars = self.get_required_variables()
        provided_vars = set(variables.keys())
        missing_vars = set(required_vars) - provided_vars
        extra_vars = provided_vars - set(required_vars)

        return {
            "is_valid": len(missing_vars) == 0,
            "required_variables": required_vars,
            "provided_variables": list(provided_vars),
            "missing_variables": list(missing_vars),
            "extra_variables": list(extra_vars),
        }

    def add_provider_variation(self, provider: str, template: str) -> None:
        """Add a provider-specific template variation.

        Args:
            provider: Provider name (e.g., 'ollama', 'openai')
            template: Provider-specific template string
        """
        if not provider or not provider.strip():
            raise PromptTemplateError("Provider name cannot be empty")

        if not template or not template.strip():
            raise PromptTemplateError("Provider template cannot be empty")

        self.provider_variations[provider.lower()] = template.strip()
        self.logger.info(f"Added {provider} variation to template '{self.name}'")

    def to_dict(self) -> Dict[str, Any]:
        """Convert template to dictionary for serialization.

        Returns:
            Dictionary representation of the template
        """
        return {
            "name": self.name,
            "prompt_type": self.prompt_type.value,
            "base_template": self.base_template,
            "provider_variations": self.provider_variations,
            "metadata": self.metadata,
            "required_variables": self.get_required_variables(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PromptTemplate":
        """Create template from dictionary.

        Args:
            data: Dictionary containing template data

        Returns:
            PromptTemplate instance

        Raises:
            PromptTemplateError: If data is invalid
        """
        try:
            return cls(
                name=data["name"],
                prompt_type=data["prompt_type"],
                base_template=data["base_template"],
                provider_variations=data.get("provider_variations"),
                metadata=data.get("metadata"),
            )
        except KeyError as e:
            raise PromptTemplateError(f"Missing required field in template data: {e}")

    def __str__(self) -> str:
        """String representation of the template."""
        return f"PromptTemplate(name='{self.name}', type={self.prompt_type.value})"

    def __repr__(self) -> str:
        """Developer representation of the template."""
        return (
            f"PromptTemplate(name='{self.name}', type={self.prompt_type.value}, "
            f"variations={len(self.provider_variations)})"
        )


class Prompt:
    """Container for managing multiple prompt templates.

    This class acts as a container for all the slightly different prompts
    that each model will receive in a given part of the pipeline to ensure
    that models behave as desired with provider-specific optimizations.

    Attributes:
        templates: Dictionary of prompt templates by name
        default_provider: Default provider for template selection
        logger: Logger instance for this class
    """

    def __init__(self, default_provider: Optional[str] = None) -> None:
        """Initialize the prompt container.

        Args:
            default_provider: Default provider name for template selection
        """
        self.templates: Dict[str, PromptTemplate] = {}
        self.default_provider = default_provider
        self.logger = logging.getLogger(self.__class__.__name__)

    def add_template(self, template: PromptTemplate) -> None:
        """Add a prompt template to the container.

        Args:
            template: PromptTemplate instance to add

        Raises:
            PromptError: If template name already exists
        """
        if template.name in self.templates:
            raise PromptError(f"Template '{template.name}' already exists")

        self.templates[template.name] = template
        self.logger.info(
            f"Added template '{template.name}' of type {template.prompt_type.value}"
        )

    def get_template(self, name: str) -> Optional[PromptTemplate]:
        """Get a template by name.

        Args:
            name: Template name

        Returns:
            PromptTemplate instance or None if not found
        """
        return self.templates.get(name)

    def render_template(
        self, name: str, variables: Dict[str, Any], provider: Optional[str] = None
    ) -> str:
        """Render a specific template with variables.

        Args:
            name: Template name
            variables: Variables for template rendering
            provider: Optional provider name (uses default if not specified)

        Returns:
            Rendered prompt string

        Raises:
            PromptError: If template not found or rendering fails
        """
        template = self.get_template(name)
        if not template:
            raise PromptError(f"Template '{name}' not found")

        provider = provider or self.default_provider
        return template.render(variables, provider)

    def list_templates(self, prompt_type: Optional[PromptType] = None) -> List[str]:
        """List available template names, optionally filtered by type.

        Args:
            prompt_type: Optional filter by prompt type

        Returns:
            List of template names
        """
        if prompt_type is None:
            return list(self.templates.keys())

        return [
            name
            for name, template in self.templates.items()
            if template.prompt_type == prompt_type
        ]

    def get_templates_by_type(self, prompt_type: PromptType) -> List[PromptTemplate]:
        """Get all templates of a specific type.

        Args:
            prompt_type: Type of prompts to retrieve

        Returns:
            List of PromptTemplate instances
        """
        return [
            template
            for template in self.templates.values()
            if template.prompt_type == prompt_type
        ]

    def validate_template(self, name: str, variables: Dict[str, Any]) -> Dict[str, Any]:
        """Validate variables for a specific template.

        Args:
            name: Template name
            variables: Variables to validate

        Returns:
            Validation result dictionary

        Raises:
            PromptError: If template not found
        """
        template = self.get_template(name)
        if not template:
            raise PromptError(f"Template '{name}' not found")

        return template.validate(variables)

    def load_templates_from_file(self, file_path: Union[str, Path]) -> int:
        """Load templates from a YAML or JSON file.

        Args:
            file_path: Path to the templates file

        Returns:
            Number of templates loaded

        Raises:
            PromptError: If file cannot be loaded or contains invalid data
        """
        file_path = Path(file_path)

        if not file_path.exists():
            raise PromptError(f"Template file not found: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                if file_path.suffix.lower() == ".json":
                    data = json.load(f)
                else:  # Assume YAML
                    data = yaml.safe_load(f)

            if not isinstance(data, dict) or "templates" not in data:
                raise PromptError("Invalid template file format")

            loaded_count = 0
            for template_data in data["templates"]:
                try:
                    template = PromptTemplate.from_dict(template_data)
                    self.add_template(template)
                    loaded_count += 1
                except (PromptError, PromptTemplateError) as e:
                    self.logger.warning(f"Failed to load template: {e}")

            self.logger.info(f"Loaded {loaded_count} templates from {file_path}")
            return loaded_count

        except (json.JSONDecodeError, yaml.YAMLError) as e:
            raise PromptError(f"Failed to parse template file: {e}")
        except Exception as e:
            raise PromptError(f"Failed to load templates: {e}")

    def save_templates_to_file(self, file_path: Union[str, Path]) -> None:
        """Save all templates to a YAML or JSON file.

        Args:
            file_path: Path to save the templates file

        Raises:
            PromptError: If file cannot be saved
        """
        file_path = Path(file_path)

        # Ensure parent directory exists
        file_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "metadata": {
                "created_at": datetime.now().isoformat(),
                "template_count": len(self.templates),
                "default_provider": self.default_provider,
            },
            "templates": [template.to_dict() for template in self.templates.values()],
        }

        try:
            with open(file_path, "w", encoding="utf-8") as f:
                if file_path.suffix.lower() == ".json":
                    json.dump(data, f, indent=2, ensure_ascii=False)
                else:  # Default to YAML
                    yaml.dump(data, f, default_flow_style=False, allow_unicode=True)

            self.logger.info(f"Saved {len(self.templates)} templates to {file_path}")

        except Exception as e:
            raise PromptError(f"Failed to save templates: {e}")

    def create_builtin_templates(self) -> None:
        """Create a set of built-in templates for common use cases."""

        # Issue generation template
        issue_gen_template = PromptTemplate(
            name="basic_issue_generation",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="""Based on the following repository analysis, generate {num_issues} GitHub issues with titles and descriptions.

Repository Information:
- Path: {repo_path}
- Recent commits: {commit_count}
- Modified files: {modified_files_count}
- New files: {new_files_count}

Recent Changes:
{recent_changes}

File Changes Summary:
{file_changes_summary}

Please generate relevant issues that would help improve the codebase, such as:
- Documentation updates
- Code reviews for frequently modified files
- Testing improvements
- Refactoring opportunities

Format each issue as:
TITLE: [Issue title]
DESCRIPTION: [Detailed issue description]
LABELS: [Comma-separated labels]

Generate {num_issues} issues:""",
            provider_variations={
                "ollama": """You are a helpful assistant that analyzes code repositories and suggests GitHub issues.

Repository Analysis:
- Path: {repo_path}
- Recent commits: {commit_count}
- Modified files: {modified_files_count}
- New files: {new_files_count}

Recent Changes:
{recent_changes}

File Changes Summary:
{file_changes_summary}

Based on this analysis, suggest {num_issues} practical GitHub issues. Focus on:
1. Documentation improvements
2. Code quality enhancements
3. Testing needs
4. Maintenance tasks

Format each issue exactly as:
TITLE: [clear, actionable title]
DESCRIPTION: [detailed description with context]
LABELS: [relevant labels]

Issues:""",
                "openai": """You are an expert software development assistant. Analyze the provided repository information and generate {num_issues} high-quality GitHub issues.

## Repository Analysis
- **Path**: {repo_path}
- **Recent Commits**: {commit_count}
- **Modified Files**: {modified_files_count}
- **New Files**: {new_files_count}

## Recent Activity
{recent_changes}

## File Changes
{file_changes_summary}

## Task
Generate {num_issues} actionable GitHub issues that would genuinely improve this codebase. Consider:
- Documentation gaps
- Code quality concerns
- Testing coverage
- Technical debt
- Performance optimizations

## Output Format
For each issue, provide:
TITLE: [Concise, actionable title]
DESCRIPTION: [Comprehensive description with rationale and acceptance criteria]
LABELS: [Appropriate labels like 'documentation', 'enhancement', 'bug', etc.]

Generate the issues:""",
            },
            metadata={
                "description": "Basic template for generating GitHub issues from repository analysis",
                "version": "1.0",
                "category": "issue_generation",
            },
        )

        # Issue description template
        issue_desc_template = PromptTemplate(
            name="detailed_issue_description",
            prompt_type=PromptType.ISSUE_DESCRIPTION,
            base_template="""Expand the following issue title into a detailed GitHub issue description:

Title: {issue_title}

Context:
{context}

Please create a comprehensive issue description that includes:
- Problem statement
- Current situation
- Proposed solution
- Acceptance criteria
- Additional context

Description:""",
            provider_variations={
                "ollama": """Create a detailed GitHub issue description for: {issue_title}

Context: {context}

The description should include:
1. Clear problem statement
2. Current state
3. Proposed changes
4. Success criteria

Description:""",
                "openai": """Transform this issue title into a comprehensive GitHub issue description:

**Title**: {issue_title}

**Context**: {context}

Create a well-structured issue description with:
- **Problem Statement**: What needs to be addressed
- **Current Situation**: What exists today
- **Proposed Solution**: Recommended approach
- **Acceptance Criteria**: Definition of done
- **Additional Notes**: Any relevant context

**Issue Description**:""",
            },
        )

        # Code analysis template
        code_analysis_template = PromptTemplate(
            name="code_analysis",
            prompt_type=PromptType.CODE_ANALYSIS,
            base_template="""Analyze the following code changes and provide insights:

File: {file_path}
Changes: {changes}

Code Diff:
{diff}

Please analyze:
1. Code quality
2. Potential issues
3. Improvement suggestions
4. Testing needs

Analysis:""",
            metadata={
                "description": "Template for analyzing code changes and diffs",
                "version": "1.0",
            },
        )

        # Add templates to container
        self.add_template(issue_gen_template)
        self.add_template(issue_desc_template)
        self.add_template(code_analysis_template)

        self.logger.info("Created built-in prompt templates")

    def __len__(self) -> int:
        """Return number of templates."""
        return len(self.templates)

    def __contains__(self, name: str) -> bool:
        """Check if template exists."""
        return name in self.templates

    def __str__(self) -> str:
        """String representation of the prompt container."""
        return f"Prompt(templates={len(self.templates)}, default_provider={self.default_provider})"

    def __repr__(self) -> str:
        """Developer representation of the prompt container."""
        return (
            f"Prompt(templates={len(self.templates)}, "
            f"default_provider={self.default_provider}, "
            f"types={set(t.prompt_type.value for t in self.templates.values())})"
        )
