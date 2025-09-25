"""
Test module for LLM classes: LLM, LLMBackend, and related components.

This module provides comprehensive tests for LLM functionality
including provider integration, response validation, and error handling.
"""

import unittest
from unittest.mock import Mock, patch

from src.ticket_master.llm import LLM, LLMError, LLMProvider, OllamaBackend


class TestLLMBackend(unittest.TestCase):
    """Test LLM backend functionality."""

    def test_ollama_backend_init(self):
        """Test OllamaBackend initialization."""
        config = {
            "host": "localhost",
            "port": 11434,
            "model": "llama2"
        }
        
        backend = OllamaBackend(config)
        
        self.assertEqual(backend.host, "localhost")
        self.assertEqual(backend.port, 11434)
        self.assertEqual(backend.model, "llama2")
        self.assertEqual(backend.base_url, "http://localhost:11434")

    @patch('src.ticket_master.llm.requests.get')
    def test_ollama_is_available(self, mock_get):
        """Test Ollama availability check."""
        backend = OllamaBackend({"host": "localhost", "port": 11434})
        
        # Test available
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response
        self.assertTrue(backend.is_available())
        
        # Test not available (reset mock and set side effect)
        mock_get.reset_mock()
        mock_get.side_effect = Exception("Connection failed")
        self.assertFalse(backend.is_available())


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


if __name__ == "__main__":
    unittest.main()