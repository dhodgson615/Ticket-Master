"""
Ollama integration tools for Ticket-Master.

This module provides high-level Python tools for interfacing between the
application and the Ollama API using prompt objects.
"""

import json
import logging
import time
from typing import Any, Dict, List, Optional, Union

try:
    import ollama
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ollama>=0.3.0,<0.4.0"])
    import ollama

from .prompt import PromptTemplate, PromptType


class OllamaToolsError(Exception):
    """Custom exception for Ollama tools errors."""
    pass


class OllamaPromptProcessor:
    """
    High-level processor for sending prompt objects to Ollama API.
    
    This class provides a clean interface for converting prompt templates
    into Ollama API calls with proper error handling and response processing.
    """
    
    def __init__(self, host: str = "localhost", port: int = 11434, model: str = "llama3.2"):
        """
        Initialize the Ollama prompt processor.
        
        Args:
            host: Ollama server host
            port: Ollama server port
            model: Default model to use
        """
        self.client = ollama.Client(host=f"http://{host}:{port}")
        self.model = model
        self.logger = logging.getLogger(self.__class__.__name__)
        
    def process_prompt(
        self,
        prompt_template: PromptTemplate,
        variables: Dict[str, Any],
        model: Optional[str] = None,
        **options
    ) -> Dict[str, Any]:
        """
        Process a prompt template through Ollama API.
        
        Args:
            prompt_template: The prompt template to process
            variables: Variables to substitute in the template
            model: Model to use (defaults to instance model)
            **options: Additional options for Ollama generate call
            
        Returns:
            Dictionary containing response and metadata
            
        Raises:
            OllamaToolsError: If processing fails
        """
        try:
            # Render the prompt for Ollama
            rendered_prompt = prompt_template.render(variables, provider="ollama")
            target_model = model or self.model
            
            self.logger.info(f"Processing prompt with model: {target_model}")
            self.logger.debug(f"Rendered prompt: {rendered_prompt[:200]}...")
            
            start_time = time.time()
            
            # Prepare options for ollama client
            generation_options = {}
            if "temperature" in options:
                generation_options["temperature"] = options["temperature"]
            if "num_predict" in options:
                generation_options["num_predict"] = options["num_predict"]
            if "max_tokens" in options:
                generation_options["num_predict"] = options["max_tokens"]
            if "top_k" in options:
                generation_options["top_k"] = options["top_k"]
            if "top_p" in options:
                generation_options["top_p"] = options["top_p"]
            
            # Send to Ollama
            response = self.client.generate(
                model=target_model,
                prompt=rendered_prompt,
                stream=False,
                options=generation_options if generation_options else None
            )
            
            processing_time = time.time() - start_time
            
            return {
                "response": response.get("response", "").strip(),
                "metadata": {
                    "model": target_model,
                    "prompt_type": prompt_template.prompt_type.value if prompt_template.prompt_type else "unknown",
                    "template_name": prompt_template.name,
                    "processing_time": processing_time,
                    "prompt_length": len(rendered_prompt),
                    "response_length": len(response.get("response", "")),
                    "total_duration": response.get("total_duration", 0),
                    "load_duration": response.get("load_duration", 0),
                    "prompt_eval_count": response.get("prompt_eval_count", 0),
                    "eval_count": response.get("eval_count", 0),
                    "eval_duration": response.get("eval_duration", 0),
                },
                "raw_response": response
            }
            
        except ollama.ResponseError as e:
            self.logger.error(f"Ollama API error: {e}")
            raise OllamaToolsError(f"Ollama API error: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error processing prompt: {e}")
            raise OllamaToolsError(f"Failed to process prompt: {e}")
    
    def batch_process_prompts(
        self,
        prompts: List[Dict[str, Any]],
        model: Optional[str] = None,
        **options
    ) -> List[Dict[str, Any]]:
        """
        Process multiple prompts in batch.
        
        Args:
            prompts: List of prompt dictionaries with 'template' and 'variables' keys
            model: Model to use for all prompts
            **options: Additional options for Ollama generate calls
            
        Returns:
            List of response dictionaries
        """
        results = []
        
        for i, prompt_data in enumerate(prompts):
            try:
                template = prompt_data["template"]
                variables = prompt_data.get("variables", {})
                
                result = self.process_prompt(template, variables, model, **options)
                result["batch_index"] = i
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Failed to process prompt {i}: {e}")
                results.append({
                    "batch_index": i,
                    "error": str(e),
                    "template_name": prompt_data.get("template", PromptTemplate("unknown", None, "")).name
                })
        
        return results
    
    def generate_issues_from_analysis(
        self,
        analysis_data: Dict[str, Any],
        max_issues: int = 5,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate GitHub issues from repository analysis using Ollama.
        
        Args:
            analysis_data: Repository analysis data
            max_issues: Maximum number of issues to generate
            model: Model to use for generation
            
        Returns:
            List of generated issue dictionaries
        """
        from .prompt import Prompt
        
        # Get the issue generation template
        prompt_manager = Prompt()
        prompt_manager.create_builtin_templates()  # Ensure built-in templates are created
        template = prompt_manager.get_template("basic_issue_generation")
        
        if not template:
            raise OllamaToolsError("Issue generation template not found")
        
        # Prepare template variables
        variables = {
            "repo_path": analysis_data.get("repository_info", {}).get("path", "unknown"),
            "commit_count": analysis_data.get("analysis_summary", {}).get("commit_count", 0),
            "modified_files_count": analysis_data.get("analysis_summary", {}).get("files_modified", 0),
            "new_files_count": analysis_data.get("analysis_summary", {}).get("files_added", 0),
            "num_issues": max_issues,
            "recent_changes": self._format_recent_changes(analysis_data.get("commits", [])),
            "file_changes_summary": self._format_file_changes_summary(analysis_data.get("analysis_summary", {})),
        }
        
        # Process the prompt
        result = self.process_prompt(
            template,
            variables,
            model,
            temperature=0.7,
            options={"num_predict": 2000}
        )
        
        # Parse the response to extract issues
        try:
            issues = self._parse_issues_response(result["response"])
            
            # Add metadata to each issue
            for issue in issues:
                issue["_generation_metadata"] = {
                    "model": result["metadata"]["model"],
                    "template": result["metadata"]["template_name"],
                    "processing_time": result["metadata"]["processing_time"]
                }
            
            return issues[:max_issues]
            
        except Exception as e:
            self.logger.error(f"Failed to parse issues from response: {e}")
            raise OllamaToolsError(f"Failed to parse generated issues: {e}")
    
    def _format_recent_changes(self, commits: List[Dict]) -> str:
        """Format recent commits for prompt context."""
        if not commits:
            return "No recent commits available"
        
        formatted = []
        for commit in commits[:5]:  # Only show first 5 commits
            short_hash = commit.get("short_hash", "unknown")
            summary = commit.get("summary", commit.get("message", "No message"))
            formatted.append(f"- {short_hash}: {summary}")
        
        return "\n".join(formatted)
    
    def _format_file_changes_summary(self, summary: Dict) -> str:
        """Format file changes summary for prompt context."""
        modified = summary.get("files_modified", 0)
        added = summary.get("files_added", 0)
        insertions = summary.get("total_insertions", 0)
        deletions = summary.get("total_deletions", 0)
        
        return f"Modified: {modified} files, Added: {added} files, Changes: +{insertions}/-{deletions} lines"
    
    def _parse_issues_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse Ollama response to extract issue data."""
        issues = []
        
        # Try JSON parsing first
        try:
            # Clean the response
            cleaned = response.strip()
            if cleaned.startswith("```json"):
                cleaned = cleaned[7:]
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
            cleaned = cleaned.strip()
            
            # Parse as JSON
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                issues = parsed
            elif isinstance(parsed, dict):
                issues = [parsed]
            
        except json.JSONDecodeError:
            # Fall back to text parsing
            self.logger.debug("JSON parsing failed, attempting text parsing")
            issues = self._parse_issues_from_text(response)
        
        # Validate and clean issues
        validated_issues = []
        for issue in issues:
            if isinstance(issue, dict) and "title" in issue and "description" in issue:
                validated_issues.append({
                    "title": str(issue["title"]).strip(),
                    "description": str(issue["description"]).strip(),
                    "labels": issue.get("labels", []),
                    "assignees": issue.get("assignees", [])
                })
        
        return validated_issues
    
    def _parse_issues_from_text(self, text: str) -> List[Dict[str, Any]]:
        """Parse issues from structured text response."""
        issues = []
        lines = text.split('\n')
        current_issue = {}
        
        for line in lines:
            line = line.strip()
            if line.startswith("TITLE:"):
                if current_issue:
                    issues.append(current_issue)
                current_issue = {"title": line[6:].strip()}
            elif line.startswith("DESCRIPTION:"):
                current_issue["description"] = line[12:].strip()
            elif line.startswith("LABELS:"):
                labels_str = line[7:].strip()
                current_issue["labels"] = [label.strip() for label in labels_str.split(",") if label.strip()]
        
        if current_issue and "title" in current_issue:
            issues.append(current_issue)
        
        return issues
    
    def check_model_availability(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if a model is available in Ollama.
        
        Args:
            model: Model name to check (defaults to instance model)
            
        Returns:
            Dictionary with availability information
        """
        target_model = model or self.model
        
        try:
            models = self.client.list()
            available_models = [m["name"] for m in models.get("models", [])]
            
            is_available = any(target_model in model_name for model_name in available_models)
            
            return {
                "model": target_model,
                "available": is_available,
                "available_models": available_models,
                "exact_match": target_model in available_models
            }
            
        except Exception as e:
            self.logger.error(f"Failed to check model availability: {e}")
            return {
                "model": target_model,
                "available": False,
                "error": str(e)
            }
    
    def install_model(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Install a model in Ollama.
        
        Args:
            model: Model name to install (defaults to instance model)
            
        Returns:
            Dictionary with installation results
        """
        target_model = model or self.model
        
        try:
            self.logger.info(f"Installing model: {target_model}")
            
            # Use ollama.pull with progress tracking
            response = self.client.pull(target_model)
            
            return {
                "model": target_model,
                "success": True,
                "status": "installed",
                "response": response
            }
            
        except Exception as e:
            self.logger.error(f"Failed to install model {target_model}: {e}")
            return {
                "model": target_model,
                "success": False,
                "error": str(e)
            }
    
    def get_model_info(self, model: Optional[str] = None) -> Dict[str, Any]:
        """
        Get detailed information about a model.
        
        Args:
            model: Model name to get info for (defaults to instance model)
            
        Returns:
            Dictionary with model information
        """
        target_model = model or self.model
        
        try:
            # Get model details
            model_info = self.client.show(target_model)
            
            return {
                "model": target_model,
                "available": True,
                "details": model_info,
                "parameters": model_info.get("parameters", {}),
                "template": model_info.get("template", ""),
                "system": model_info.get("system", ""),
                "modified_at": model_info.get("modified_at", "")
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get model info for {target_model}: {e}")
            return {
                "model": target_model,
                "available": False,
                "error": str(e)
            }


class OllamaPromptValidator:
    """
    Validator for prompt objects before sending to Ollama.
    
    This class ensures prompts are well-formed and optimized for Ollama.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_prompt_template(self, template: PromptTemplate) -> Dict[str, Any]:
        """
        Validate a prompt template for Ollama compatibility.
        
        Args:
            template: The prompt template to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Check if template has Ollama-specific variation
        if not template.provider_variations or "ollama" not in template.provider_variations:
            warnings.append("No Ollama-specific prompt variation defined")
        
        # Check prompt length (Ollama typically works better with shorter prompts)
        base_length = len(template.base_template)
        if base_length > 4000:
            warnings.append(f"Prompt template is quite long ({base_length} chars), consider shortening")
        
        # Check for required placeholders
        if template.prompt_type == PromptType.ISSUE_GENERATION:
            required_vars = ["num_issues", "repo_path"]
            missing_vars = []
            for var in required_vars:
                if f"{{{var}}}" not in template.base_template:
                    missing_vars.append(var)
            if missing_vars:
                issues.append(f"Missing required variables for issue generation: {missing_vars}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "template_name": template.name,
            "template_type": template.prompt_type.value if template.prompt_type else "unknown"
        }
    
    def validate_variables(self, template: PromptTemplate, variables: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate variables for a prompt template.
        
        Args:
            template: The prompt template
            variables: Variables to validate
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        warnings = []
        
        # Find placeholders in template
        import re
        placeholders = re.findall(r'\{(\w+)\}', template.base_template)
        
        # Check for missing variables
        missing = [var for var in placeholders if var not in variables]
        if missing:
            issues.append(f"Missing required variables: {missing}")
        
        # Check for unused variables
        unused = [var for var in variables.keys() if var not in placeholders]
        if unused:
            warnings.append(f"Unused variables provided: {unused}")
        
        # Validate variable types and content
        for var_name, var_value in variables.items():
            if var_value is None:
                warnings.append(f"Variable '{var_name}' is None")
            elif isinstance(var_value, str) and len(var_value) == 0:
                warnings.append(f"Variable '{var_name}' is empty string")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "placeholders_found": placeholders,
            "variables_provided": list(variables.keys())
        }


def create_ollama_processor(config: Dict[str, Any]) -> OllamaPromptProcessor:
    """
    Factory function to create an OllamaPromptProcessor from configuration.
    
    Args:
        config: Configuration dictionary with Ollama settings
        
    Returns:
        Configured OllamaPromptProcessor instance
    """
    host = config.get("host", "localhost")
    port = config.get("port", 11434)
    model = config.get("model", "llama3.2")
    
    return OllamaPromptProcessor(host=host, port=port, model=model)