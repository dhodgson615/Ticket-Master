"""
Test module for prompt classes: Prompt, PromptTemplate, and related components.

This module provides comprehensive tests for prompt functionality
including template rendering, validation, and container management.
"""

import unittest

from src.ticket_master.prompt import (Prompt, PromptError, PromptTemplate,
                                      PromptType)


class TestPromptTemplate(unittest.TestCase):
    """Test PromptTemplate functionality."""

    def test_init_valid_template(self):
        """Test PromptTemplate initialization with valid data."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}"
        )
        
        self.assertEqual(template.name, "test_template")
        self.assertEqual(template.prompt_type, PromptType.ISSUE_GENERATION)
        self.assertEqual(template.base_template, "Generate {num_issues} issues for {repo_name}")

    def test_init_string_prompt_type(self):
        """Test PromptTemplate initialization with string prompt type."""
        template = PromptTemplate(
            name="test_template",
            prompt_type="issue_generation",
            base_template="Test template"
        )
        
        self.assertEqual(template.prompt_type, PromptType.ISSUE_GENERATION)

    def test_render_basic(self):
        """Test basic template rendering."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}"
        )
        
        variables = {"num_issues": 3, "repo_name": "test-repo"}
        rendered = template.render(variables)
        
        self.assertEqual(rendered, "Generate 3 issues for test-repo")

    def test_render_missing_variable(self):
        """Test template rendering with missing variable."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name}"
        )
        
        variables = {"num_issues": 3}  # Missing repo_name
        
        with self.assertRaises(Exception):  # Should raise PromptTemplateError
            template.render(variables)

    def test_get_required_variables(self):
        """Test extraction of required variables."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num_issues} issues for {repo_name} in {language}"
        )
        
        required_vars = template.get_required_variables()
        self.assertEqual(set(required_vars), {"num_issues", "repo_name", "language"})

    def test_provider_variations(self):
        """Test provider-specific template variations."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Base: {value}",
            provider_variations={
                "ollama": "Ollama: {value}",
                "openai": "OpenAI: {value}"
            }
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
            base_template="Test template"
        )
        
        self.prompt.add_template(template)
        self.assertEqual(len(self.prompt.templates), 1)
        self.assertIn("test_template", self.prompt)

    def test_get_template(self):
        """Test retrieving templates from the container."""
        template = PromptTemplate(
            name="test_template",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Test template"
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
            base_template="Generate {num} issues"
        )
        
        self.prompt.add_template(template)
        rendered = self.prompt.render_template("test_template", {"num": 5})
        
        self.assertEqual(rendered, "Generate 5 issues")

    def test_list_templates(self):
        """Test listing templates."""
        template1 = PromptTemplate("template1", PromptType.ISSUE_GENERATION, "Test 1")
        template2 = PromptTemplate("template2", PromptType.CODE_ANALYSIS, "Test 2")
        
        self.prompt.add_template(template1)
        self.prompt.add_template(template2)
        
        all_templates = self.prompt.list_templates()
        self.assertEqual(set(all_templates), {"template1", "template2"})
        
        issue_templates = self.prompt.list_templates(PromptType.ISSUE_GENERATION)
        self.assertEqual(issue_templates, ["template1"])

    def test_create_builtin_templates(self):
        """Test creation of built-in templates."""
        self.prompt.create_builtin_templates()
        
        self.assertGreater(len(self.prompt.templates), 0)
        self.assertIn("basic_issue_generation", self.prompt)


if __name__ == "__main__":
    unittest.main()