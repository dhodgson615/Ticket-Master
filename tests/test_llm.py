"""
Test module for LLM classes: LLM, LLMBackend, and related components.

This module provides comprehensive tests for LLM functionality
including provider integration, response validation, and error handling.
"""

import unittest
from unittest.mock import Mock, patch

from src.ticket_master.llm import (
    LLM,
    LLMError,
    LLMProvider,
    LLMProviderError,
    OllamaBackend,
    OpenAIBackend,
    MockBackend,
)


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

    def test_ollama_is_available(self):
        """Test Ollama availability check."""
        backend = OllamaBackend({"host": "localhost", "port": 11434})

        # Since ollama client is available in our environment, we expect it to use the client
        # The test will mock the client's list method
        if hasattr(backend, "client") and backend.client:
            with patch.object(backend.client, "list") as mock_list:
                # Test available
                mock_list.return_value = {"models": []}
                self.assertTrue(backend.is_available())

                # Test not available
                mock_list.side_effect = Exception("Connection failed")
                self.assertFalse(backend.is_available())
        else:
            # If client is not available, it should fall back to requests
            with patch("src.ticket_master.llm.requests.get") as mock_get:
                mock_response = Mock()
                mock_response.status_code = 200
                mock_get.return_value = mock_response
                self.assertTrue(backend.is_available())

                mock_get.side_effect = Exception("Connection failed")
                self.assertFalse(backend.is_available())

    def test_openai_backend_init(self):
        """Test OpenAIBackend initialization."""
        config = {"api_key": "test-api-key", "model": "gpt-4"}

        backend = OpenAIBackend(config)

        self.assertEqual(backend.api_key, "test-api-key")
        self.assertEqual(backend.model, "gpt-4")
        self.assertEqual(backend.base_url, "https://api.openai.com/v1")

    def test_openai_backend_init_missing_api_key(self):
        """Test OpenAIBackend initialization without API key."""
        config = {"model": "gpt-4"}

        with self.assertRaises(LLMProviderError) as context:
            OpenAIBackend(config)

        self.assertIn("API key is required", str(context.exception))

    @patch("src.ticket_master.llm.requests.get")
    def test_openai_is_available(self, mock_get):
        """Test OpenAI availability check."""
        backend = OpenAIBackend({"api_key": "test-key"})

        # Test available
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertTrue(backend.is_available())

        # Test not available (reset mock and set side effect)
        mock_get.reset_mock()
        mock_get.side_effect = Exception("Connection failed")
        self.assertFalse(backend.is_available())

    @patch("src.ticket_master.llm.requests.post")
    def test_openai_generate(self, mock_post):
        """Test OpenAI text generation."""
        backend = OpenAIBackend(
            {"api_key": "test-key", "model": "gpt-3.5-turbo"}
        )

        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated text response"}}]
        }
        mock_post.return_value = mock_response

        result = backend.generate("Test prompt")

        self.assertEqual(result, "Generated text response")
        mock_post.assert_called_once()

        # Verify the request was made with correct parameters
        call_args = mock_post.call_args
        self.assertIn("Authorization", call_args[1]["headers"])
        self.assertEqual(call_args[1]["json"]["model"], "gpt-3.5-turbo")
        self.assertEqual(
            call_args[1]["json"]["messages"][0]["content"], "Test prompt"
        )

    @patch("src.ticket_master.llm.requests.post")
    def test_openai_generate_error(self, mock_post):
        """Test OpenAI text generation with API error."""
        backend = OpenAIBackend({"api_key": "test-key"})

        # Mock error response
        mock_post.side_effect = Exception("API Error")

        with self.assertRaises(LLMProviderError) as context:
            backend.generate("Test prompt")

        self.assertIn("API request failed", str(context.exception))

    def test_mock_backend_init(self):
        """Test MockBackend initialization."""
        config = {"model": "test-mock-model"}

        backend = MockBackend(config)

        self.assertEqual(backend.model, "test-mock-model")

    def test_mock_backend_init_defaults(self):
        """Test MockBackend initialization with defaults."""
        backend = MockBackend({})

        self.assertEqual(backend.model, "mock-model")

    def test_mock_backend_is_available(self):
        """Test MockBackend availability (should always be True)."""
        backend = MockBackend({})

        self.assertTrue(backend.is_available())

    def test_mock_backend_get_model_info(self):
        """Test MockBackend model info."""
        backend = MockBackend({"model": "test-mock"})

        info = backend.get_model_info()

        self.assertEqual(info["name"], "test-mock")
        self.assertEqual(info["provider"], "mock")
        self.assertEqual(info["status"], "available")
        self.assertIn("description", info)

    def test_mock_backend_generate_json_prompt(self):
        """Test MockBackend generation with JSON prompt."""
        backend = MockBackend({})

        prompt = "Generate some issues in JSON format"
        response = backend.generate(prompt)

        self.assertIsInstance(response, str)
        self.assertIn("title", response)
        self.assertIn("description", response)
        # Should return JSON-like content for issue generation
        self.assertTrue(response.startswith("[") or response.startswith("{"))

    def test_mock_backend_generate_general_prompt(self):
        """Test MockBackend generation with general prompt."""
        backend = MockBackend({})

        prompt = "What is the weather like?"
        response = backend.generate(prompt)

        self.assertIsInstance(response, str)
        self.assertIn("mock response", response.lower())


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

    def test_openai_initialization(self):
        """Test LLM initialization with OpenAI provider."""
        config = {"api_key": "test-key", "model": "gpt-4"}
        llm = LLM(LLMProvider.OPENAI, config)

        self.assertEqual(llm.provider, LLMProvider.OPENAI)
        self.assertEqual(llm.metadata["provider"], "openai")
        self.assertEqual(llm.metadata["model"], "gpt-4")

    def test_llm_generate_end_to_end(self):
        """Test end-to-end LLM generation workflow."""
        config = {"api_key": "test-key", "model": "gpt-3.5-turbo"}
        llm = LLM(LLMProvider.OPENAI, config)

        with patch("src.ticket_master.llm.requests.post") as mock_post:
            # Mock successful response
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "choices": [
                    {
                        "message": {
                            "content": "This is a test response from OpenAI API"
                        }
                    }
                ]
            }
            mock_post.return_value = mock_response

            result = llm.generate("Test prompt")

            # Verify response structure
            self.assertIn("response", result)
            self.assertIn("metadata", result)
            self.assertIn("validation", result)

            self.assertEqual(
                result["response"], "This is a test response from OpenAI API"
            )
            self.assertEqual(result["metadata"]["provider"], "openai")
            self.assertTrue(result["validation"]["is_valid"])

    def test_mock_llm_integration(self):
        """Test complete Mock LLM integration."""
        config = {"model": "test-mock"}
        llm = LLM("mock", config)

        self.assertEqual(llm.provider, LLMProvider.MOCK)
        self.assertTrue(llm.is_available())

        # Test generation
        prompt = "Generate some issues in JSON format"
        result = llm.generate(prompt)

        # Verify response structure
        self.assertIn("response", result)
        self.assertIn("metadata", result)
        self.assertIn("validation", result)

        # Verify metadata
        self.assertEqual(result["metadata"]["provider"], "mock")
        self.assertEqual(result["metadata"]["model"], "test-mock")
        self.assertTrue(result["metadata"]["is_primary"])

        # Verify response content
        response = result["response"]
        self.assertIsInstance(response, str)
        self.assertIn("title", response)
        self.assertIn("description", response)


class TestLLMModelInstallation(unittest.TestCase):
    """Test LLM model installation functionality."""

    def test_install_model_ollama_success(self):
        """Test successful model installation with Ollama provider."""
        config = {"host": "localhost", "port": 11434, "model": "llama2"}
        llm = LLM(LLMProvider.OLLAMA, config)

        with patch.object(llm.backend, "install_model") as mock_install:
            mock_install.return_value = {
                "success": True,
                "model": "test-model",
                "status": "installed",
                "message": "Model installed successfully",
            }

            result = llm.install_model("test-model")

            self.assertTrue(result["success"])
            self.assertEqual(result["model"], "test-model")
            self.assertEqual(result["status"], "installed")
            mock_install.assert_called_once_with("test-model")

    def test_install_model_unsupported_provider(self):
        """Test model installation with unsupported provider."""
        config = {"api_key": "test-key", "model": "gpt-4"}
        llm = LLM(LLMProvider.OPENAI, config)

        result = llm.install_model("gpt-4")

        self.assertFalse(result["success"])
        self.assertIn("Automatic installation not supported", result["error"])
        self.assertEqual(result["provider"], "openai")

    def test_install_model_backend_not_supported(self):
        """Test model installation when backend doesn't support it."""
        config = {"host": "localhost", "port": 11434}

        # Create a mock backend without install_model method
        mock_backend = Mock(spec=[])  # No install_model method
        with patch("src.ticket_master.llm.OllamaBackend", return_value=mock_backend):
            llm = LLM(LLMProvider.OLLAMA, config)

            result = llm.install_model("test-model")

            self.assertFalse(result["success"])
            self.assertIn("Backend does not support model installation", result["error"])


class TestLLMModelAvailability(unittest.TestCase):
    """Test LLM model availability checking functionality."""

    def test_check_model_availability_available(self):
        """Test checking availability for an available model."""
        config = {"host": "localhost", "port": 11434, "model": "llama2"}
        llm = LLM(LLMProvider.OLLAMA, config)

        with patch.object(llm.backend, "get_model_info") as mock_get_info:
            mock_get_info.return_value = {
                "status": "available",
                "model": "llama2",
                "provider": "ollama",
            }

            result = llm.check_model_availability()

            self.assertTrue(result["available"])
            self.assertEqual(result["model"], "llama2")
            mock_get_info.assert_called_once()

    def test_check_model_availability_not_available(self):
        """Test checking availability for an unavailable model."""
        config = {"host": "localhost", "port": 11434, "model": "missing-model"}
        llm = LLM(LLMProvider.OLLAMA, config)

        with patch.object(llm.backend, "get_model_info") as mock_get_info:
            mock_get_info.return_value = {
                "status": "not_found",
                "model": "missing-model",
                "provider": "ollama",
            }

            result = llm.check_model_availability()

            self.assertFalse(result["available"])
            self.assertEqual(result["model"], "missing-model")

    def test_check_model_availability_with_auto_install(self):
        """Test model availability check with auto-install enabled."""
        config = {"host": "localhost", "port": 11434, "model": "test-model"}
        llm = LLM(LLMProvider.OLLAMA, config)

        with patch.object(llm.backend, "get_model_info") as mock_get_info, patch.object(
            llm, "install_model"
        ) as mock_install:
            # First call returns not available, second call returns available
            mock_get_info.side_effect = [
                {"status": "not_found", "model": "test-model"},
                {"status": "available", "model": "test-model"},
            ]
            mock_install.return_value = {"success": True}

            result = llm.check_model_availability(auto_install=True)

            self.assertTrue(result["available"])
            self.assertIn("installation", result)
            mock_install.assert_called_once_with("test-model")


class TestLLMListModels(unittest.TestCase):
    """Test LLM model listing functionality."""

    def test_list_available_models_success(self):
        """Test successful model listing."""
        config = {"host": "localhost", "port": 11434}
        llm = LLM(LLMProvider.OLLAMA, config)

        with patch.object(llm.backend, "list_available_models") as mock_list:
            mock_list.return_value = {
                "success": True,
                "models": [
                    {"name": "llama2", "size": "3.8GB"},
                    {"name": "codellama", "size": "7.2GB"},
                ],
                "count": 2,
            }

            result = llm.list_available_models()

            self.assertTrue(result["success"])
            self.assertEqual(result["count"], 2)
            self.assertEqual(len(result["models"]), 2)
            mock_list.assert_called_once()

    def test_list_available_models_failure(self):
        """Test model listing failure."""
        config = {"host": "localhost", "port": 11434}
        llm = LLM(LLMProvider.OLLAMA, config)

        with patch.object(llm.backend, "list_available_models") as mock_list:
            mock_list.return_value = {
                "success": False,
                "error": "Connection failed",
                "models": [],
                "count": 0,
            }

            result = llm.list_available_models()

            self.assertFalse(result["success"])
            self.assertIn("error", result)
            self.assertEqual(result["count"], 0)


class TestLLMBackendListing(unittest.TestCase):
    """Test LLM backend listing functionality."""

    def test_list_available_backends(self):
        """Test listing available backends."""
        config = {"model": "test"}
        llm = LLM(LLMProvider.OLLAMA, config)

        backends = llm.list_available_backends()

        # Should list primary backend
        self.assertGreater(len(backends), 0)
        self.assertEqual(backends[0]["name"], "OllamaBackend")
        self.assertTrue(backends[0]["is_primary"])
        self.assertIn("is_available", backends[0])
        self.assertIn("model_info", backends[0])

    def test_list_available_backends_with_fallbacks(self):
        """Test listing backends with fallbacks configured."""
        config = {"model": "test"}
        fallback_configs = [
            {"provider": "mock", "model": "mock-model"},
            {"provider": "openai", "api_key": "test-key", "model": "gpt-4"},
        ]

        llm = LLM(LLMProvider.OLLAMA, config, fallback_configs)

        backends = llm.list_available_backends()

        # Should have primary + fallback backends
        self.assertGreaterEqual(len(backends), 2)
        primary_backend = next(b for b in backends if b["is_primary"])
        self.assertEqual(primary_backend["name"], "OllamaBackend")


class TestLLMFailureScenarios(unittest.TestCase):
    """Test LLM failure scenarios and error recovery."""

    def test_generate_with_primary_failure_fallback_success(self):
        """Test generation with primary backend failing but fallback succeeding."""
        config = {"model": "test"}
        fallback_configs = [{"provider": "mock", "model": "mock-model"}]

        llm = LLM(LLMProvider.OLLAMA, config, fallback_configs)

        with patch.object(llm.backend, "generate") as mock_primary_gen, patch.object(
            llm.fallback_backends[0], "generate"
        ) as mock_fallback_gen:
            # Primary fails, fallback succeeds
            mock_primary_gen.side_effect = LLMProviderError("Primary backend failed")
            mock_fallback_gen.return_value = "Fallback response"

            result = llm.generate("Test prompt")

            self.assertEqual(result["response"], "Fallback response")
            self.assertFalse(result["metadata"]["is_primary"])
            mock_primary_gen.assert_called()
            mock_fallback_gen.assert_called_once()

    def test_generate_all_backends_fail(self):
        """Test generation when all backends fail."""
        config = {"model": "test"}
        fallback_configs = [{"provider": "mock", "model": "mock-model"}]

        llm = LLM(LLMProvider.OLLAMA, config, fallback_configs)

        with patch.object(llm.backend, "generate") as mock_primary_gen, patch.object(
            llm.fallback_backends[0], "generate"
        ) as mock_fallback_gen:
            # Both backends fail
            mock_primary_gen.side_effect = LLMProviderError("Primary failed")
            mock_fallback_gen.side_effect = LLMProviderError("Fallback failed")

            with self.assertRaises(LLMError):
                llm.generate("Test prompt")

    def test_generate_with_retries(self):
        """Test generation with retries before success."""
        config = {"model": "test"}
        llm = LLM(LLMProvider.OLLAMA, config)

        with patch.object(llm.backend, "generate") as mock_gen:
            # Fail twice, succeed on third attempt
            mock_gen.side_effect = [
                LLMProviderError("First failure"),
                LLMProviderError("Second failure"),
                "Success on third try",
            ]

            result = llm.generate("Test prompt", max_retries=3)

            self.assertEqual(result["response"], "Success on third try")
            self.assertEqual(result["metadata"]["attempt"], 3)
            self.assertEqual(mock_gen.call_count, 3)

    def test_generate_validation_failure(self):
        """Test response validation identifying poor quality responses."""
        config = {"model": "test"}
        llm = LLM(LLMProvider.MOCK, config)

        # This will use the mock backend which generates structured responses
        result = llm.generate("Test prompt", validate_response=True)

        self.assertIn("validation", result)
        self.assertIn("is_valid", result["validation"])
        self.assertIn("quality_score", result["validation"])

    def test_response_validation_empty_response(self):
        """Test validation of empty responses."""
        config = {"model": "test"}
        llm = LLM(LLMProvider.MOCK, config)

        # Test the private validation method directly
        validation = llm._validate_response("", "Test prompt")

        self.assertFalse(validation["is_valid"])
        self.assertIn("Response is too short or empty", validation["issues"])
        self.assertEqual(validation["quality_score"], 0.0)

    def test_response_validation_repetitive_content(self):
        """Test validation of repetitive content."""
        config = {"model": "test"}
        llm = LLM(LLMProvider.MOCK, config)

        repetitive_response = "the the the the the the the the"
        validation = llm._validate_response(repetitive_response, "Test prompt")

        self.assertIn("Response appears to be repetitive", validation["issues"])
        self.assertLess(validation["quality_score"], 1.0)

    def test_response_validation_error_patterns(self):
        """Test validation detecting common error patterns."""
        config = {"model": "test"}
        llm = LLM(LLMProvider.MOCK, config)

        error_response = "I'm sorry, I cannot help with this request as an AI."
        validation = llm._validate_response(error_response, "Test prompt")

        self.assertIn("Response contains error patterns", validation["issues"][0])
        self.assertLess(validation["quality_score"], 1.0)


class TestOpenAIIntegration(unittest.TestCase):
    """Test OpenAI API integration and authentication."""

    def test_openai_backend_initialization(self):
        """Test OpenAI backend initialization with API key."""
        config = {"api_key": "test-api-key", "model": "gpt-4"}

        backend = OpenAIBackend(config)

        self.assertEqual(backend.api_key, "test-api-key")
        self.assertEqual(backend.model, "gpt-4")
        self.assertEqual(backend.base_url, "https://api.openai.com/v1")

    def test_openai_backend_custom_base_url(self):
        """Test OpenAI backend with custom base URL."""
        config = {
            "api_key": "test-key",
            "model": "gpt-4",
            "base_url": "https://custom.openai.proxy.com/v1",
        }

        backend = OpenAIBackend(config)

        self.assertEqual(backend.base_url, "https://custom.openai.proxy.com/v1")

    @patch("src.ticket_master.llm.requests.post")
    def test_openai_generate_success(self, mock_post):
        """Test successful OpenAI text generation."""
        config = {"api_key": "test-key", "model": "gpt-4"}
        backend = OpenAIBackend(config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "choices": [{"message": {"content": "Generated text response"}}]
        }
        mock_post.return_value = mock_response

        result = backend.generate("Test prompt")

        self.assertEqual(result, "Generated text response")
        mock_post.assert_called_once()

    @patch("src.ticket_master.llm.requests.post")
    def test_openai_generate_api_error(self, mock_post):
        """Test OpenAI API error handling."""
        config = {"api_key": "invalid-key", "model": "gpt-4"}
        backend = OpenAIBackend(config)

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {"error": {"message": "Invalid API key"}}
        mock_response.raise_for_status.side_effect = Exception("HTTP 401")
        mock_post.return_value = mock_response

        with self.assertRaises(LLMProviderError):
            backend.generate("Test prompt")

    @patch("src.ticket_master.llm.requests.get")
    def test_openai_is_available_success(self, mock_get):
        """Test OpenAI availability check success."""
        config = {"api_key": "test-key", "model": "gpt-4"}
        backend = OpenAIBackend(config)

        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        self.assertTrue(backend.is_available())

    @patch("src.ticket_master.llm.requests.get")
    def test_openai_is_available_failure(self, mock_get):
        """Test OpenAI availability check failure."""
        config = {"api_key": "invalid-key", "model": "gpt-4"}
        backend = OpenAIBackend(config)

        mock_get.side_effect = Exception("Connection failed")

        self.assertFalse(backend.is_available())


if __name__ == "__main__":
    unittest.main()
