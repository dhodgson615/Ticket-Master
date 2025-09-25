# Contributing to Ticket-Master

Thank you for your interest in contributing to Ticket-Master! This document provides guidelines and information for contributors.

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/Ticket-Master.git
cd Ticket-Master
```

2. Set up the development environment:
```bash
make setup
```

3. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

## Development Workflow

### Before Making Changes

1. Make sure all tests pass:
```bash
make test
```

2. Ensure code quality:
```bash
make ci
```

### Making Changes

1. Write tests for new functionality
2. Follow existing code style and patterns
3. Update documentation as needed
4. Ensure all tests pass

### Code Quality Standards

This project uses:
- **Black** for code formatting (79 character line limit)
- **flake8** for linting
- **mypy** for type checking
- **pytest** for testing with coverage

Run all checks with:
```bash
make ci
```

### Submitting Changes

1. Push your changes to your fork:
```bash
git push origin feature/your-feature-name
```

2. Create a Pull Request with:
   - Clear description of changes
   - Reference to any related issues
   - Screenshots for UI changes (if applicable)

## CI/CD Pipeline

All pull requests are automatically tested using GitHub Actions:

- **Multi-version Python testing** (3.9, 3.10, 3.11, 3.12)
- **Code formatting** with Black
- **Linting** with flake8
- **Type checking** with mypy
- **Security scanning** with Bandit and Safety
- **Test coverage** reporting

The CI pipeline must pass before merging.

## Issue Guidelines

When creating issues:

1. Use the provided issue templates when available
2. Provide clear reproduction steps for bugs
3. Include relevant system information
4. Search existing issues first to avoid duplicates

## Security

If you discover a security vulnerability, please report it privately by emailing the maintainers rather than opening a public issue.

## Questions?

Feel free to open an issue for questions about contributing or join the discussions in existing issues and pull requests.