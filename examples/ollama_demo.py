#!/usr/bin/env python3
"""
Demonstration of Ollama integration tools for Ticket-Master.

This script shows how to use the new Python tools that interface between
the application and the Ollama API using prompt objects.
"""

import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ticket_master.ollama_tools import (OllamaPromptValidator,
                                        OllamaToolsError,
                                        create_ollama_processor)
from ticket_master.prompt import PromptTemplate, PromptType


def main():
    """Demonstrate Ollama integration features."""
    print("=" * 60)
    print("Ticket-Master Ollama Integration Demo")
    print("=" * 60)

    # Configuration
    config = {"host": "localhost", "port": 11434, "model": "llama3.2"}

    try:
        # Create Ollama processor
        print("\n1. Creating Ollama Prompt Processor...")
        processor = create_ollama_processor(config)
        print(f"   ✓ Created processor for model: {processor.model}")

        # Check if Ollama is available
        print("\n2. Checking Ollama availability...")
        try:
            if processor.client:
                print("   ✓ Ollama client initialized successfully")

                # Check model availability
                availability = processor.check_model_availability()
                if availability["available"]:
                    print(f"   ✓ Model '{availability['model']}' is available")
                else:
                    print(f"   ⚠ Model '{availability['model']}' not found")
                    print(
                        f"     Available models: {availability.get('available_models', [])}"
                    )
                    print("     You can install it with: ollama pull llama3.2")
            else:
                print("   ⚠ Ollama client not available")
                return
        except Exception as e:
            print(f"   ✗ Ollama not available: {e}")
            print("   Make sure Ollama is running with 'ollama serve'")
            return

        # Create and validate a prompt template
        print("\n3. Creating and validating prompt template...")
        template = PromptTemplate(
            name="demo_issue_generator",
            prompt_type=PromptType.ISSUE_GENERATION,
            base_template="Generate {num} GitHub issues for project {project} focusing on {focus_area}",
            provider_variations={
                "ollama": """Create {num} actionable GitHub issues for the {project} project.

Focus Area: {focus_area}

For each issue, provide:
- A clear, specific title
- A detailed description with context
- Appropriate labels
- Any relevant assignees

Format the response as JSON with this structure:
[
  {{
    "title": "Issue title",
    "description": "Detailed description",
    "labels": ["label1", "label2"],
    "assignees": []
  }}
]

Issues:"""
            },
        )

        # Validate the template
        validator = OllamaPromptValidator()
        validation = validator.validate_prompt_template(template)

        if validation["valid"]:
            print("   ✓ Prompt template is valid")
        else:
            print(f"   ⚠ Template validation issues: {validation['issues']}")

        if validation["warnings"]:
            print(f"   ⚠ Template warnings: {validation['warnings']}")

        # Validate variables
        variables = {
            "num": 3,
            "project": "Ticket-Master",
            "focus_area": "documentation and testing",
        }

        var_validation = validator.validate_variables(template, variables)
        if var_validation["valid"]:
            print("   ✓ Variables are valid")
        else:
            print(f"   ⚠ Variable issues: {var_validation['issues']}")

        # Process the prompt (this would normally require Ollama to be running)
        print("\n4. Processing prompt with Ollama...")
        print(
            "   Note: This requires Ollama to be running with the specified model"
        )

        try:
            result = processor.process_prompt(
                template, variables, temperature=0.7, top_k=40
            )

            print("   ✓ Prompt processed successfully!")
            print(f"   Response length: {len(result['response'])} characters")
            print(
                f"   Processing time: {result['metadata']['processing_time']:.2f} seconds"
            )
            print(f"   Model used: {result['metadata']['model']}")

            # Show first part of response
            response_preview = (
                result["response"][:200] + "..."
                if len(result["response"]) > 200
                else result["response"]
            )
            print(f"   Response preview: {response_preview}")

        except OllamaToolsError as e:
            print(f"   ⚠ Could not process prompt: {e}")
            print(
                "   This is expected if Ollama is not running or model is not available"
            )

        # Demo repository analysis issue generation
        print(
            "\n5. Demonstrating issue generation from repository analysis..."
        )

        # Sample analysis data (normally from Repository class)
        analysis_data = {
            "repository_info": {"path": "/example/repo"},
            "analysis_summary": {
                "commit_count": 15,
                "files_modified": 8,
                "files_added": 3,
                "total_insertions": 250,
                "total_deletions": 100,
            },
            "commits": [
                {
                    "short_hash": "a1b2c3d",
                    "summary": "Add new authentication system",
                },
                {
                    "short_hash": "e4f5g6h",
                    "summary": "Fix database connection issues",
                },
                {"short_hash": "i7j8k9l", "summary": "Update documentation"},
            ],
        }

        try:
            issues = processor.generate_issues_from_analysis(
                analysis_data, max_issues=3
            )

            print(f"   ✓ Generated {len(issues)} issues from analysis")
            for i, issue in enumerate(issues, 1):
                print(f"   Issue {i}: {issue['title']}")
                print(f"   Labels: {issue.get('labels', [])}")

        except Exception as e:
            print(f"   ⚠ Issue generation failed: {e}")
            print("   This is expected if Ollama is not running")

        # Demo batch processing
        print("\n6. Demonstrating batch processing...")

        simple_template = PromptTemplate(
            name="simple_demo",
            prompt_type=PromptType.CODE_ANALYSIS,
            base_template="Analyze: {code_snippet}",
            provider_variations={
                "ollama": "Provide a brief analysis of this code: {code_snippet}"
            },
        )

        batch_prompts = [
            {
                "template": simple_template,
                "variables": {"code_snippet": "def hello(): print('world')"},
            },
            {
                "template": simple_template,
                "variables": {"code_snippet": "class MyClass: pass"},
            },
            {
                "template": simple_template,
                "variables": {"code_snippet": "import sys; sys.exit(0)"},
            },
        ]

        try:
            batch_results = processor.batch_process_prompts(
                batch_prompts, temperature=0.3
            )

            print(f"   ✓ Processed {len(batch_results)} prompts in batch")
            for i, result in enumerate(batch_results, 1):
                if "error" in result:
                    print(f"   Prompt {i}: Failed - {result['error']}")
                else:
                    response_preview = (
                        result["response"][:50] + "..."
                        if len(result["response"]) > 50
                        else result["response"]
                    )
                    print(f"   Prompt {i}: {response_preview}")

        except Exception as e:
            print(f"   ⚠ Batch processing failed: {e}")

        print("\n" + "=" * 60)
        print("Demo completed successfully!")
        print("\nTo use Ollama integration in your application:")
        print("1. Install Ollama: https://ollama.ai")
        print("2. Start server: ollama serve")
        print("3. Install model: ollama pull llama3.2")
        print("4. Run Ticket-Master with Ollama provider")
        print("=" * 60)

    except Exception as e:
        print(f"\nDemo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
