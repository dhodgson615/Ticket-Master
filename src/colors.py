import os
import sys
from typing import Any


# Global color variables - ANSI escape codes
# These can be used throughout the application for consistent coloring
class Colors:
    """Global color constants using ANSI escape codes."""

    # Text colors
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    GRAY = "\033[90m"

    # Background colors
    BG_RED = "\033[101m"
    BG_GREEN = "\033[102m"
    BG_YELLOW = "\033[103m"
    BG_BLUE = "\033[104m"
    BG_MAGENTA = "\033[105m"
    BG_CYAN = "\033[106m"

    # Text styles
    BOLD = "\033[1m"
    DIM = "\033[2m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    BLINK = "\033[5m"
    REVERSE = "\033[7m"
    STRIKETHROUGH = "\033[9m"

    # Reset
    RESET = "\033[0m"
    END = "\033[0m"  # Alias for RESET


# Global variables for easy access
RED = Colors.RED
GREEN = Colors.GREEN
YELLOW = Colors.YELLOW
BLUE = Colors.BLUE
MAGENTA = Colors.MAGENTA
CYAN = Colors.CYAN
WHITE = Colors.WHITE
GRAY = Colors.GRAY
BOLD = Colors.BOLD
DIM = Colors.DIM
ITALIC = Colors.ITALIC
UNDERLINE = Colors.UNDERLINE
RESET = Colors.RESET
END = Colors.END


def supports_color() -> bool:
    """
    Check if the terminal supports color output.

    Returns:
        True if colors are supported, False otherwise
    """
    # Check if we're in a TTY
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False

    # Check environment variables that indicate color support
    term = os.environ.get("TERM", "").lower()
    if term in ["dumb", "unknown"]:
        return False

    # Check for common color-supporting terminals
    if any(
        term.endswith(suffix) for suffix in ["color", "256color", "truecolor"]
    ):
        return True

    # Check for NO_COLOR environment variable (https://no-color.org/)
    if os.environ.get("NO_COLOR"):
        return False

    # Check for FORCE_COLOR environment variable
    if os.environ.get("FORCE_COLOR"):
        return True

    # Default to True for most modern terminals
    return True


# Global flag to control color output
_COLOR_ENABLED = supports_color()


def enable_colors(enabled: bool = True) -> None:
    """
    Enable or disable color output globally.

    Args:
        enabled: Whether to enable colors
    """
    global _COLOR_ENABLED
    _COLOR_ENABLED = enabled


def is_color_enabled() -> bool:
    """
    Check if colors are currently enabled.

    Returns:
        True if colors are enabled, False otherwise
    """
    return _COLOR_ENABLED


def colorize(text: str, color: str = "", style: str = "") -> str:
    """
    Apply color and/or style to text.

    Args:
        text: Text to colorize
        color: Color code (e.g., Colors.RED)
        style: Style code (e.g., Colors.BOLD)

    Returns:
        Colorized text if colors are enabled, plain text otherwise
    """
    if not _COLOR_ENABLED:
        return text

    return f"{style}{color}{text}{Colors.RESET}"


def success(text: str, bold: bool = False) -> str:
    """
    Format text as success message (green).

    Args:
        text: Text to format
        bold: Whether to make text bold

    Returns:
        Formatted success text
    """
    style = Colors.BOLD if bold else ""
    return colorize(text, Colors.GREEN, style)


def error(text: str, bold: bool = False) -> str:
    """
    Format text as error message (red).

    Args:
        text: Text to format
        bold: Whether to make text bold

    Returns:
        Formatted error text
    """
    style = Colors.BOLD if bold else ""
    return colorize(text, Colors.RED, style)


def warning(text: str, bold: bool = False) -> str:
    """
    Format text as warning message (yellow).

    Args:
        text: Text to format
        bold: Whether to make text bold

    Returns:
        Formatted warning text
    """
    style = Colors.BOLD if bold else ""
    return colorize(text, Colors.YELLOW, style)


def info(text: str, bold: bool = False) -> str:
    """
    Format text as info message (blue).

    Args:
        text: Text to format
        bold: Whether to make text bold

    Returns:
        Formatted info text
    """
    style = Colors.BOLD if bold else ""
    return colorize(text, Colors.BLUE, style)


def header(text: str, color: str = Colors.CYAN) -> str:
    """
    Format text as header (bold, colored).

    Args:
        text: Text to format
        color: Color to use (default: cyan)

    Returns:
        Formatted header text
    """
    return colorize(text, color, Colors.BOLD)


def highlight(text: str, color: str = Colors.MAGENTA) -> str:
    """
    Highlight text with a color.

    Args:
        text: Text to highlight
        color: Color to use (default: magenta)

    Returns:
        Highlighted text
    """
    return colorize(text, color)


def dim(text: str) -> str:
    """
    Make text dimmed/faded.

    Args:
        text: Text to dim

    Returns:
        Dimmed text
    """
    return colorize(text, "", Colors.DIM)


def progress_bar(
    completed: int, total: int, width: int = 40, color: str = Colors.GREEN
) -> str:
    """Create a colored progress bar.

    Args:
        completed (int): Number of completed items.
        total (int): Total number of items.
        width (int): Width of the progress bar in characters.
        color (str): Color for the completed portion.

    Returns:
        str: Formatted progress bar.

    Raises:
        ValueError: If width is less than 1.

    Example:
        >>> progress_bar(5, 10, width=10)
        '[\033[92m█████\033[0m░░░░░] 50.0%'
    """
    if width < 1:
        raise ValueError("Progress bar width must be at least 1")

    if total == 0:
        return f"[{' ' * width}] 0%"

    percent: float = completed / total

    if width == 1:
        filled: int = 1 if percent >= 1.0 else 0

    else:
        filled: int = min(int(width * percent), width)

    remaining: int = width - filled
    bar_filled: str = colorize("█" * filled, color) if filled > 0 else ""
    bar_empty: str = "░" * remaining
    percentage: str = f"{percent:.1%}"

    return f"[{bar_filled}{bar_empty}] {percentage}"


def print_colored(
    text: Any, color: str = "", style: str = "", **kwargs
) -> None:
    """
    Print text with color and style.

    Args:
        text: Text to print
        color: Color code
        style: Style code
        **kwargs: Additional arguments passed to print()
    """
    colored_text = colorize(str(text), color, style)
    print(colored_text, **kwargs)
