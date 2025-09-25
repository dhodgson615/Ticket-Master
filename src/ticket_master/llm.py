"""
LLM module for Large Language Model integration and management.

This module provides the LLM class and related components for integrating
with multiple LLM providers (Ollama, OpenAI, etc.) with proper error handling,
response validation, and fallback mechanisms.
"""

import json
import logging
import subprocess
import sys
import time
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union

# Import with fallback installation
try:
    import requests
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "requests>=2.31.0"]
    )
    import requests


class LLMError(Exception):
    """Custom exception for LLM-related errors."""

    pass


class LLMProviderError(LLMError):
    """Exception for LLM provider-specific errors."""

    pass


class LLMValidationError(LLMError):
    """Exception for LLM response validation errors."""

    pass


class LLMProvider(Enum):
    """Supported LLM providers."""

    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    LOCAL = "local"


class LLMBackend(ABC):
    """Abstract base class for LLM backend implementations.

    This class defines the interface that all LLM backends must implement
    to ensure consistent behavior across different providers.
    """

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the LLM backend.

        Args:
            config: Configuration dictionary for the backend
        """
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using the LLM.

        Args:
            prompt: Input prompt for the LLM
            **kwargs: Additional parameters for generation

        Returns:
            Generated text response

        Raises:
            LLMProviderError: If generation fails
        """
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the LLM backend is available.

        Returns:
            True if backend is available, False otherwise
        """
        pass

    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model.

        Returns:
            Dictionary containing model information
        """
        pass


class OllamaBackend(LLMBackend):
    """Ollama LLM backend implementation."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize Ollama backend.

        Args:
            config: Configuration dictionary with 'host', 'port', 'model' keys
        """
        super().__init__(config)
        self.host = config.get("host", "localhost")
        self.port = config.get("port", 11434)
        self.model = config.get("model", "llama2")
        self.base_url = f"http://{self.host}:{self.port}"

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using Ollama API.

        Args:
            prompt: Input prompt for the LLM
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text response

        Raises:
            LLMProviderError: If generation fails
        """
        try:
            payload = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                **kwargs,
            }

            response = requests.post(
                f"{self.base_url}/api/generate",
                json=payload,
                timeout=kwargs.get("timeout", 60),
            )
            response.raise_for_status()

            result = response.json()
            return result.get("response", "").strip()

        except requests.RequestException as e:
            raise LLMProviderError(f"Ollama API error: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise LLMProviderError(f"Invalid Ollama response format: {e}")

    def is_available(self) -> bool:
        """Check if Ollama service is available.

        Returns:
            True if Ollama is available, False otherwise
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current Ollama model.

        Returns:
            Dictionary containing model information
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()

            models = response.json().get("models", [])
            current_model = next(
                (model for model in models if model["name"] == self.model),
                None,
            )

            if current_model:
                return {
                    "name": current_model["name"],
                    "size": current_model.get("size", "unknown"),
                    "modified_at": current_model.get("modified_at", "unknown"),
                    "provider": "ollama",
                }

            return {
                "name": self.model,
                "provider": "ollama",
                "status": "not_found",
            }

        except requests.RequestException as e:
            self.logger.warning(f"Failed to get model info: {e}")
            return {"name": self.model, "provider": "ollama", "error": str(e)}

    def install_model(self, model_name: Optional[str] = None) -> Dict[str, Any]:
        """Install or pull a model from Ollama.

        Args:
            model_name: Name of the model to install (defaults to self.model)

        Returns:
            Dictionary containing installation result
        """
        target_model = model_name or self.model
        
        try:
            self.logger.info(f"Installing Ollama model: {target_model}")
            
            payload = {"name": target_model}
            response = requests.post(
                f"{self.base_url}/api/pull",
                json=payload,
                stream=True,  # Use streaming for progress updates
                timeout=300,  # 5 minutes for model download
            )
            
            response.raise_for_status()
            
            # Parse streaming response to get final status
            last_line = ""
            for line in response.iter_lines(decode_unicode=True):
                if line:
                    try:
                        data = json.loads(line)
                        if data.get("status"):
                            last_line = data["status"]
                            self.logger.debug(f"Pull status: {last_line}")
                    except json.JSONDecodeError:
                        continue
            
            # Check if installation was successful
            if "success" in last_line.lower() or "complete" in last_line.lower():
                self.logger.info(f"Successfully installed model: {target_model}")
                return {
                    "success": True,
                    "model": target_model,
                    "status": "installed",
                    "message": last_line
                }
            else:
                return {
                    "success": False,
                    "model": target_model,
                    "status": "failed",
                    "message": last_line or "Installation failed"
                }
                
        except requests.RequestException as e:
            error_msg = f"Failed to install model {target_model}: {e}"
            self.logger.error(error_msg)
            return {
                "success": False,
                "model": target_model,
                "status": "error",
                "error": str(e)
            }

    def list_available_models(self) -> Dict[str, Any]:
        """List all available models on the Ollama instance.

        Returns:
            Dictionary containing available models information
        """
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=10)
            response.raise_for_status()
            
            models_data = response.json()
            models = models_data.get("models", [])
            
            return {
                "success": True,
                "models": [
                    {
                        "name": model["name"],
                        "size": model.get("size", "unknown"),
                        "modified_at": model.get("modified_at", "unknown"),
                    }
                    for model in models
                ],
                "count": len(models)
            }
            
        except requests.RequestException as e:
            self.logger.error(f"Failed to list models: {e}")
            return {
                "success": False,
                "error": str(e),
                "models": [],
                "count": 0
            }


class OpenAIBackend(LLMBackend):
    """OpenAI LLM backend implementation."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize OpenAI backend.

        Args:
            config: Configuration dictionary with 'api_key', 'model' keys
        """
        super().__init__(config)
        self.api_key = config.get("api_key")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.base_url = config.get("base_url", "https://api.openai.com/v1")
        
        if not self.api_key:
            raise LLMProviderError("OpenAI API key is required")

    def generate(self, prompt: str, **kwargs) -> str:
        """Generate text using OpenAI API.

        Args:
            prompt: Input prompt for the LLM
            **kwargs: Additional parameters (temperature, max_tokens, etc.)

        Returns:
            Generated text response

        Raises:
            LLMProviderError: If generation fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Prepare the request payload
            payload = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": kwargs.get("temperature", 0.7),
                "max_tokens": kwargs.get("max_tokens", 1000),
                **{k: v for k, v in kwargs.items() if k not in ["temperature", "max_tokens", "timeout"]}
            }

            response = requests.post(
                f"{self.base_url}/chat/completions",
                json=payload,
                headers=headers,
                timeout=kwargs.get("timeout", 60),
            )
            response.raise_for_status()

            result = response.json()
            
            if "choices" not in result or not result["choices"]:
                raise LLMProviderError("No response choices returned from OpenAI API")
                
            content = result["choices"][0]["message"]["content"]
            return content.strip() if content else ""

        except requests.RequestException as e:
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = error_detail.get('error', {}).get('message', str(e))
                    raise LLMProviderError(f"OpenAI API error: {error_msg}")
                except (json.JSONDecodeError, AttributeError):
                    pass
            raise LLMProviderError(f"OpenAI API request failed: {e}")
        except (KeyError, json.JSONDecodeError) as e:
            raise LLMProviderError(f"Invalid OpenAI response format: {e}")
        except Exception as e:
            raise LLMProviderError(f"OpenAI API request failed: {e}")

    def is_available(self) -> bool:
        """Check if OpenAI API is available.

        Returns:
            True if OpenAI API is available, False otherwise
        """
        if not self.api_key:
            return False
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Test with a simple models list request
            response = requests.get(
                f"{self.base_url}/models",
                headers=headers,
                timeout=10
            )
            return response.status_code == 200
        except requests.RequestException:
            return False
        except Exception:
            return False

    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information.

        Returns:
            Dictionary containing model information
        """
        if not self.is_available():
            return {
                "name": self.model,
                "provider": "openai",
                "status": "unavailable",
                "error": "API key not set or API not accessible"
            }
            
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(
                f"{self.base_url}/models/{self.model}",
                headers=headers,
                timeout=10
            )
            
            if response.status_code == 200:
                model_data = response.json()
                return {
                    "name": model_data.get("id", self.model),
                    "provider": "openai",
                    "owned_by": model_data.get("owned_by", "unknown"),
                    "created": model_data.get("created", "unknown"),
                    "status": "available"
                }
            else:
                return {
                    "name": self.model,
                    "provider": "openai",
                    "status": "model_not_found"
                }
                
        except requests.RequestException as e:
            self.logger.warning(f"Failed to get model info: {e}")
            return {
                "name": self.model,
                "provider": "openai",
                "error": str(e),
                "status": "error"
            }


class LLM:
    """Main LLM class for managing Large Language Model interactions.

    This class provides a unified interface for interacting with multiple
    LLM providers, handles fallback mechanisms, response validation,
    and includes relevant metadata for issue generation pipelines.

    Attributes:
        provider: Current LLM provider
        backend: Active LLM backend instance
        fallback_backends: List of fallback backend instances
        metadata: Metadata about the LLM configuration
        logger: Logger instance for this class
    """

    def __init__(
        self,
        provider: Union[LLMProvider, str],
        config: Dict[str, Any],
        fallback_configs: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Initialize the LLM with provider and configuration.

        Args:
            provider: LLM provider to use
            config: Configuration for the primary provider
            fallback_configs: Optional list of fallback provider configurations

        Raises:
            LLMError: If provider is unsupported or configuration is invalid
        """
        if isinstance(provider, str):
            try:
                provider = LLMProvider(provider.lower())
            except ValueError:
                raise LLMError(f"Unsupported LLM provider: {provider}")

        self.provider = provider
        self.logger = logging.getLogger(self.__class__.__name__)

        # Initialize primary backend
        self.backend = self._create_backend(provider, config)

        # Initialize fallback backends
        self.fallback_backends: List[LLMBackend] = []
        if fallback_configs:
            for fallback_config in fallback_configs:
                fallback_provider = fallback_config.get("provider")
                if fallback_provider:
                    try:
                        fallback_provider = LLMProvider(
                            fallback_provider.lower()
                        )
                        fallback_backend = self._create_backend(
                            fallback_provider, fallback_config
                        )
                        self.fallback_backends.append(fallback_backend)
                    except (ValueError, LLMError) as e:
                        self.logger.warning(
                            f"Failed to initialize fallback backend: {e}"
                        )

        # Store metadata
        self.metadata = {
            "provider": self.provider.value,
            "model": config.get("model", "unknown"),
            "initialized_at": datetime.now().isoformat(),
            "fallback_count": len(self.fallback_backends),
        }

    def _create_backend(
        self, provider: LLMProvider, config: Dict[str, Any]
    ) -> LLMBackend:
        """Create appropriate backend instance for the provider.

        Args:
            provider: LLM provider enum
            config: Configuration dictionary

        Returns:
            LLM backend instance

        Raises:
            LLMError: If provider is unsupported
        """
        if provider == LLMProvider.OLLAMA:
            return OllamaBackend(config)
        elif provider == LLMProvider.OPENAI:
            return OpenAIBackend(config)
        else:
            raise LLMError(
                f"Backend not implemented for provider: {provider.value}"
            )

    def generate(
        self,
        prompt: str,
        max_retries: int = 3,
        use_fallback: bool = True,
        validate_response: bool = True,
        **kwargs,
    ) -> Dict[str, Any]:
        """Generate text using the LLM with fallback and validation.

        Args:
            prompt: Input prompt for the LLM
            max_retries: Maximum number of retries per backend
            use_fallback: Whether to use fallback backends on failure
            validate_response: Whether to validate the response
            **kwargs: Additional parameters for generation

        Returns:
            Dictionary containing response, metadata, and validation info

        Raises:
            LLMError: If all backends fail
        """
        backends_to_try = [self.backend]
        if use_fallback:
            backends_to_try.extend(self.fallback_backends)

        last_error = None

        for backend_index, backend in enumerate(backends_to_try):
            is_primary = backend_index == 0

            for attempt in range(max_retries):
                try:
                    start_time = time.time()
                    response = backend.generate(prompt, **kwargs)
                    generation_time = time.time() - start_time

                    # Validate response if requested
                    validation_result = None
                    if validate_response:
                        validation_result = self._validate_response(
                            response, prompt
                        )

                    result = {
                        "response": response,
                        "metadata": {
                            "provider": backend.__class__.__name__.replace(
                                "Backend", ""
                            ).lower(),
                            "model": getattr(backend, "model", "unknown"),
                            "attempt": attempt + 1,
                            "is_primary": is_primary,
                            "generation_time": generation_time,
                            "prompt_length": len(prompt),
                            "response_length": len(response),
                            "timestamp": datetime.now().isoformat(),
                        },
                        "validation": validation_result,
                    }

                    self.logger.info(
                        f"Successfully generated response using {backend.__class__.__name__} "
                        f"(attempt {attempt + 1}/{max_retries})"
                    )
                    return result

                except LLMProviderError as e:
                    last_error = e
                    self.logger.warning(
                        f"Attempt {attempt + 1}/{max_retries} failed for "
                        f"{backend.__class__.__name__}: {e}"
                    )

                    if attempt < max_retries - 1:
                        time.sleep(2**attempt)  # Exponential backoff

            self.logger.error(
                f"All attempts failed for {backend.__class__.__name__}"
            )

        # If we get here, all backends failed
        raise LLMError(f"All LLM backends failed. Last error: {last_error}")

    def _validate_response(self, response: str, prompt: str) -> Dict[str, Any]:
        """Validate the LLM response for quality and relevance.

        Args:
            response: Generated response to validate
            prompt: Original prompt

        Returns:
            Dictionary containing validation results
        """
        validation = {
            "is_valid": True,
            "issues": [],
            "quality_score": 1.0,
            "checks": {},
        }

        # Check if response is empty or too short
        if not response or len(response.strip()) < 10:
            validation["is_valid"] = False
            validation["issues"].append("Response is too short or empty")
            validation["quality_score"] = 0.0

        # Check for repetitive content
        words = response.split()
        if len(words) > 0:
            unique_words = set(words)
            repetition_ratio = len(unique_words) / len(words)
            validation["checks"]["repetition_ratio"] = repetition_ratio

            if repetition_ratio < 0.3:  # Very repetitive
                validation["issues"].append(
                    "Response appears to be repetitive"
                )
                validation["quality_score"] *= 0.5

        # Check for common error patterns
        error_patterns = [
            "I cannot",
            "I'm sorry",
            "I don't have",
            "As an AI",
            "I apologize",
            "I'm not able to",
            "I can't help",
        ]

        response_lower = response.lower()
        found_patterns = [
            pattern
            for pattern in error_patterns
            if pattern.lower() in response_lower
        ]

        if found_patterns:
            validation["issues"].append(
                f"Response contains error patterns: {found_patterns}"
            )
            validation["quality_score"] *= 0.7

        validation["checks"]["length"] = len(response)
        validation["checks"]["word_count"] = len(words)
        validation["checks"]["error_patterns"] = found_patterns

        return validation

    def is_available(self) -> bool:
        """Check if the primary LLM backend is available.

        Returns:
            True if primary backend is available, False otherwise
        """
        return self.backend.is_available()

    def list_available_backends(self) -> List[Dict[str, Any]]:
        """List all available backends and their status.

        Returns:
            List of dictionaries containing backend information
        """
        backends_info = []

        # Check primary backend
        backends_info.append(
            {
                "name": self.backend.__class__.__name__,
                "is_primary": True,
                "is_available": self.backend.is_available(),
                "model_info": self.backend.get_model_info(),
            }
        )

        # Check fallback backends
        for backend in self.fallback_backends:
            backends_info.append(
                {
                    "name": backend.__class__.__name__,
                    "is_primary": False,
                    "is_available": backend.is_available(),
                    "model_info": backend.get_model_info(),
                }
            )

        return backends_info

    def get_metadata(self) -> Dict[str, Any]:
        """Get LLM configuration metadata.

        Returns:
            Dictionary containing metadata
        """
        return self.metadata.copy()

    def __str__(self) -> str:
        """String representation of the LLM."""
        return f"LLM(provider={self.provider.value}, model={self.metadata.get('model', 'unknown')})"

    def __repr__(self) -> str:
        """Developer representation of the LLM."""
        return (
            f"LLM(provider={self.provider.value}, "
            f"model={self.metadata.get('model', 'unknown')}, "
            f"fallbacks={len(self.fallback_backends)})"
        )
