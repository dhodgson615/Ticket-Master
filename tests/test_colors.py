"""
Test module for colors utilities.

This module provides comprehensive tests for the colors module functionality
including ANSI color codes, terminal support detection, and formatting functions.
"""

import os
import sys
from io import StringIO
from unittest.mock import patch, MagicMock
import pytest

# Add src directory to path for imports
sys.path.insert(0, str(os.path.join(os.path.dirname(__file__), "..", "src")))

from ticket_master.colors import (
    Colors,
    supports_color,
    enable_colors,
    is_color_enabled,
    colorize,
    success,
    error,
    warning,
    info,
    header,
    highlight,
    dim,
    progress_bar,
    print_colored,
    # Global color variables
    RED,
    GREEN,
    YELLOW,
    BLUE,
    MAGENTA,
    CYAN,
    WHITE,
    GRAY,
    BOLD,
    DIM,
    ITALIC,
    UNDERLINE,
    RESET,
    END,
)


class TestColors:
    """Test cases for Colors class constants."""

    def test_text_colors(self):
        """Test that text color constants are defined correctly."""
        assert Colors.RED == "\033[91m"
        assert Colors.GREEN == "\033[92m"
        assert Colors.YELLOW == "\033[93m"
        assert Colors.BLUE == "\033[94m"
        assert Colors.MAGENTA == "\033[95m"
        assert Colors.CYAN == "\033[96m"
        assert Colors.WHITE == "\033[97m"
        assert Colors.GRAY == "\033[90m"

    def test_background_colors(self):
        """Test that background color constants are defined correctly."""
        assert Colors.BG_RED == "\033[101m"
        assert Colors.BG_GREEN == "\033[102m"
        assert Colors.BG_YELLOW == "\033[103m"
        assert Colors.BG_BLUE == "\033[104m"
        assert Colors.BG_MAGENTA == "\033[105m"
        assert Colors.BG_CYAN == "\033[106m"

    def test_text_styles(self):
        """Test that text style constants are defined correctly."""
        assert Colors.BOLD == "\033[1m"
        assert Colors.DIM == "\033[2m"
        assert Colors.ITALIC == "\033[3m"
        assert Colors.UNDERLINE == "\033[4m"
        assert Colors.BLINK == "\033[5m"
        assert Colors.REVERSE == "\033[7m"
        assert Colors.STRIKETHROUGH == "\033[9m"

    def test_reset_codes(self):
        """Test that reset codes are defined correctly."""
        assert Colors.RESET == "\033[0m"
        assert Colors.END == "\033[0m"
        assert Colors.RESET == Colors.END  # END is an alias for RESET


class TestGlobalColorVariables:
    """Test cases for global color variables."""

    def test_global_variables_match_class_constants(self):
        """Test that global variables match the Colors class constants."""
        assert RED == Colors.RED
        assert GREEN == Colors.GREEN
        assert YELLOW == Colors.YELLOW
        assert BLUE == Colors.BLUE
        assert MAGENTA == Colors.MAGENTA
        assert CYAN == Colors.CYAN
        assert WHITE == Colors.WHITE
        assert GRAY == Colors.GRAY
        assert BOLD == Colors.BOLD
        assert DIM == Colors.DIM
        assert ITALIC == Colors.ITALIC
        assert UNDERLINE == Colors.UNDERLINE
        assert RESET == Colors.RESET
        assert END == Colors.END


class TestSupportsColor:
    """Test cases for supports_color function."""

    @patch('sys.stdout')
    def test_supports_color_no_tty(self, mock_stdout):
        """Test that supports_color returns False when not in a TTY."""
        mock_stdout.isatty.return_value = False
        assert supports_color() is False

    @patch('sys.stdout')
    def test_supports_color_no_isatty_method(self, mock_stdout):
        """Test that supports_color handles missing isatty method."""
        del mock_stdout.isatty
        assert supports_color() is False

    @patch('sys.stdout')
    @patch.dict(os.environ, {'TERM': 'dumb'})
    def test_supports_color_dumb_terminal(self, mock_stdout):
        """Test that supports_color returns False for dumb terminals."""
        mock_stdout.isatty.return_value = True
        assert supports_color() is False

    @patch('sys.stdout')
    @patch.dict(os.environ, {'TERM': 'unknown'})
    def test_supports_color_unknown_terminal(self, mock_stdout):
        """Test that supports_color returns False for unknown terminals."""
        mock_stdout.isatty.return_value = True
        assert supports_color() is False

    @patch('sys.stdout')
    @patch.dict(os.environ, {'TERM': 'xterm-256color'})
    def test_supports_color_256color_terminal(self, mock_stdout):
        """Test that supports_color returns True for 256color terminals."""
        mock_stdout.isatty.return_value = True
        assert supports_color() is True

    @patch('sys.stdout')
    @patch.dict(os.environ, {'TERM': 'xterm-color'})
    def test_supports_color_color_terminal(self, mock_stdout):
        """Test that supports_color returns True for color terminals."""
        mock_stdout.isatty.return_value = True
        assert supports_color() is True

    @patch('sys.stdout')
    @patch.dict(os.environ, {'TERM': 'xterm-truecolor'})
    def test_supports_color_truecolor_terminal(self, mock_stdout):
        """Test that supports_color returns True for truecolor terminals."""
        mock_stdout.isatty.return_value = True
        assert supports_color() is True

    @patch('sys.stdout')
    @patch.dict(os.environ, {'NO_COLOR': '1', 'TERM': 'xterm-256color'})
    def test_supports_color_no_color_env(self, mock_stdout):
        """Test that NO_COLOR environment variable disables colors."""
        mock_stdout.isatty.return_value = True
        assert supports_color() is False

    @patch('sys.stdout')
    @patch.dict(os.environ, {'FORCE_COLOR': '1', 'TERM': 'dumb'})
    def test_supports_color_force_color_env(self, mock_stdout):
        """Test that FORCE_COLOR environment variable enables colors."""
        mock_stdout.isatty.return_value = True
        assert supports_color() is True

    @patch('sys.stdout')
    @patch.dict(os.environ, {'TERM': 'xterm'})
    def test_supports_color_default_true(self, mock_stdout):
        """Test that supports_color defaults to True for modern terminals."""
        mock_stdout.isatty.return_value = True
        assert supports_color() is True


class TestColorControl:
    """Test cases for color control functions."""

    def test_enable_colors_true(self):
        """Test enabling colors."""
        enable_colors(True)
        assert is_color_enabled() is True

    def test_enable_colors_false(self):
        """Test disabling colors."""
        enable_colors(False)
        assert is_color_enabled() is False

    def test_enable_colors_default_true(self):
        """Test that enable_colors defaults to True."""
        enable_colors()
        assert is_color_enabled() is True

    def test_is_color_enabled_returns_current_state(self):
        """Test that is_color_enabled returns the current state."""
        enable_colors(True)
        assert is_color_enabled() is True
        
        enable_colors(False)
        assert is_color_enabled() is False


class TestColorize:
    """Test cases for colorize function."""

    def test_colorize_with_colors_enabled(self):
        """Test colorize function when colors are enabled."""
        enable_colors(True)
        result = colorize("test", Colors.RED, Colors.BOLD)
        expected = f"{Colors.BOLD}{Colors.RED}test{Colors.RESET}"
        assert result == expected

    def test_colorize_with_colors_disabled(self):
        """Test colorize function when colors are disabled."""
        enable_colors(False)
        result = colorize("test", Colors.RED, Colors.BOLD)
        assert result == "test"

    def test_colorize_only_color(self):
        """Test colorize function with only color."""
        enable_colors(True)
        result = colorize("test", Colors.GREEN)
        expected = f"{Colors.GREEN}test{Colors.RESET}"
        assert result == expected

    def test_colorize_only_style(self):
        """Test colorize function with only style."""
        enable_colors(True)
        result = colorize("test", style=Colors.ITALIC)
        expected = f"{Colors.ITALIC}test{Colors.RESET}"
        assert result == expected

    def test_colorize_no_color_no_style(self):
        """Test colorize function with no color or style."""
        enable_colors(True)
        result = colorize("test")
        expected = f"test{Colors.RESET}"
        assert result == expected


class TestFormattingFunctions:
    """Test cases for text formatting functions."""

    def setUp(self):
        """Set up test environment."""
        enable_colors(True)

    def test_success_function(self):
        """Test success formatting function."""
        enable_colors(True)
        result = success("test message")
        expected = f"{Colors.GREEN}test message{Colors.RESET}"
        assert result == expected

    def test_success_function_bold(self):
        """Test success formatting function with bold."""
        enable_colors(True)
        result = success("test message", bold=True)
        expected = f"{Colors.BOLD}{Colors.GREEN}test message{Colors.RESET}"
        assert result == expected

    def test_error_function(self):
        """Test error formatting function."""
        enable_colors(True)
        result = error("test message")
        expected = f"{Colors.RED}test message{Colors.RESET}"
        assert result == expected

    def test_error_function_bold(self):
        """Test error formatting function with bold."""
        enable_colors(True)
        result = error("test message", bold=True)
        expected = f"{Colors.BOLD}{Colors.RED}test message{Colors.RESET}"
        assert result == expected

    def test_warning_function(self):
        """Test warning formatting function."""
        enable_colors(True)
        result = warning("test message")
        expected = f"{Colors.YELLOW}test message{Colors.RESET}"
        assert result == expected

    def test_warning_function_bold(self):
        """Test warning formatting function with bold."""
        enable_colors(True)
        result = warning("test message", bold=True)
        expected = f"{Colors.BOLD}{Colors.YELLOW}test message{Colors.RESET}"
        assert result == expected

    def test_info_function(self):
        """Test info formatting function."""
        enable_colors(True)
        result = info("test message")
        expected = f"{Colors.BLUE}test message{Colors.RESET}"
        assert result == expected

    def test_info_function_bold(self):
        """Test info formatting function with bold."""
        enable_colors(True)
        result = info("test message", bold=True)
        expected = f"{Colors.BOLD}{Colors.BLUE}test message{Colors.RESET}"
        assert result == expected

    def test_header_function_default(self):
        """Test header formatting function with default color."""
        enable_colors(True)
        result = header("test message")
        expected = f"{Colors.BOLD}{Colors.CYAN}test message{Colors.RESET}"
        assert result == expected

    def test_header_function_custom_color(self):
        """Test header formatting function with custom color."""
        enable_colors(True)
        result = header("test message", Colors.MAGENTA)
        expected = f"{Colors.BOLD}{Colors.MAGENTA}test message{Colors.RESET}"
        assert result == expected

    def test_highlight_function_default(self):
        """Test highlight formatting function with default color."""
        enable_colors(True)
        result = highlight("test message")
        expected = f"{Colors.MAGENTA}test message{Colors.RESET}"
        assert result == expected

    def test_highlight_function_custom_color(self):
        """Test highlight formatting function with custom color."""
        enable_colors(True)
        result = highlight("test message", Colors.YELLOW)
        expected = f"{Colors.YELLOW}test message{Colors.RESET}"
        assert result == expected

    def test_dim_function(self):
        """Test dim formatting function."""
        enable_colors(True)
        result = dim("test message")
        expected = f"{Colors.DIM}test message{Colors.RESET}"
        assert result == expected


class TestProgressBar:
    """Test cases for progress_bar function."""

    def test_progress_bar_zero_total(self):
        """Test progress bar with zero total."""
        enable_colors(True)
        result = progress_bar(0, 0, width=10)
        expected = "[          ] 0%"
        assert result == expected

    def test_progress_bar_full_completion(self):
        """Test progress bar at full completion."""
        enable_colors(True)
        result = progress_bar(10, 10, width=10)
        expected = f"[{Colors.GREEN}██████████{Colors.RESET}] 100.0%"
        assert result == expected

    def test_progress_bar_half_completion(self):
        """Test progress bar at half completion."""
        enable_colors(True)
        result = progress_bar(5, 10, width=10)
        expected = f"[{Colors.GREEN}█████{Colors.RESET}░░░░░] 50.0%"
        assert result == expected

    def test_progress_bar_custom_color(self):
        """Test progress bar with custom color."""
        enable_colors(True)
        result = progress_bar(3, 10, width=10, color=Colors.BLUE)
        expected = f"[{Colors.BLUE}███{Colors.RESET}░░░░░░░] 30.0%"
        assert result == expected

    def test_progress_bar_custom_width(self):
        """Test progress bar with custom width."""
        enable_colors(True)
        result = progress_bar(1, 4, width=8)
        expected = f"[{Colors.GREEN}██{Colors.RESET}░░░░░░] 25.0%"
        assert result == expected

    def test_progress_bar_colors_disabled(self):
        """Test progress bar when colors are disabled."""
        enable_colors(False)
        result = progress_bar(5, 10, width=10)
        expected = "[█████░░░░░] 50.0%"
        assert result == expected


class TestPrintColored:
    """Test cases for print_colored function."""

    @patch('builtins.print')
    def test_print_colored_basic(self, mock_print):
        """Test print_colored function basic usage."""
        enable_colors(True)
        print_colored("test message", Colors.RED, Colors.BOLD)
        expected = f"{Colors.BOLD}{Colors.RED}test message{Colors.RESET}"
        mock_print.assert_called_once_with(expected)

    @patch('builtins.print')
    def test_print_colored_with_kwargs(self, mock_print):
        """Test print_colored function with additional kwargs."""
        enable_colors(True)
        print_colored("test message", Colors.GREEN, end='\n', sep=' ')
        expected = f"{Colors.GREEN}test message{Colors.RESET}"
        mock_print.assert_called_once_with(expected, end='\n', sep=' ')

    @patch('builtins.print')
    def test_print_colored_non_string_input(self, mock_print):
        """Test print_colored function with non-string input."""
        enable_colors(True)
        print_colored(123, Colors.BLUE)
        expected = f"{Colors.BLUE}123{Colors.RESET}"
        mock_print.assert_called_once_with(expected)

    @patch('builtins.print')
    def test_print_colored_colors_disabled(self, mock_print):
        """Test print_colored function when colors are disabled."""
        enable_colors(False)
        print_colored("test message", Colors.RED, Colors.BOLD)
        mock_print.assert_called_once_with("test message")


class TestFormattingFunctionsColorsDisabled:
    """Test cases for formatting functions when colors are disabled."""

    def test_all_formatting_functions_colors_disabled(self):
        """Test that all formatting functions return plain text when colors are disabled."""
        enable_colors(False)
        
        test_text = "test message"
        
        assert success(test_text) == test_text
        assert success(test_text, bold=True) == test_text
        assert error(test_text) == test_text
        assert error(test_text, bold=True) == test_text
        assert warning(test_text) == test_text
        assert warning(test_text, bold=True) == test_text
        assert info(test_text) == test_text
        assert info(test_text, bold=True) == test_text
        assert header(test_text) == test_text
        assert header(test_text, Colors.RED) == test_text
        assert highlight(test_text) == test_text
        assert highlight(test_text, Colors.GREEN) == test_text
        assert dim(test_text) == test_text


class TestEdgeCases:
    """Test cases for edge cases and error conditions."""

    def test_empty_string_formatting(self):
        """Test formatting functions with empty strings."""
        enable_colors(True)
        
        assert success("") == f"{Colors.GREEN}{Colors.RESET}"
        assert error("") == f"{Colors.RED}{Colors.RESET}"
        assert warning("") == f"{Colors.YELLOW}{Colors.RESET}"
        assert info("") == f"{Colors.BLUE}{Colors.RESET}"

    def test_multiline_string_formatting(self):
        """Test formatting functions with multiline strings."""
        enable_colors(True)
        
        multiline = "line1\nline2\nline3"
        result = success(multiline)
        expected = f"{Colors.GREEN}line1\nline2\nline3{Colors.RESET}"
        assert result == expected

    def test_unicode_string_formatting(self):
        """Test formatting functions with unicode strings."""
        enable_colors(True)
        
        unicode_text = "测试 🌈 Ñiño"
        result = success(unicode_text)
        expected = f"{Colors.GREEN}测试 🌈 Ñiño{Colors.RESET}"
        assert result == expected

    def test_progress_bar_edge_cases(self):
        """Test progress bar with edge cases."""
        enable_colors(True)
        
        # Test with completed > total
        result = progress_bar(15, 10, width=10)
        expected = f"[{Colors.GREEN}██████████{Colors.RESET}] 150.0%"
        assert result == expected
        
        # Test with very small width
        result = progress_bar(1, 2, width=1)
        expected = f"[░] 50.0%"
        assert result == expected


if __name__ == "__main__":
    pytest.main([__file__])