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


if __name__ == "__main__":
    unittest.main()
