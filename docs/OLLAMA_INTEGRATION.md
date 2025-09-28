# Ollama Integration

Ticket-Master includes comprehensive integration with Ollama, a tool for running large language models locally. This integration provides Python tools for giving prompt objects to functions that interface between the app and the Ollama API.

## Overview

The Ollama integration consists of several components:

1. **Enhanced OllamaBackend** - Updated to use the official ollama Python client
2. **OllamaPromptProcessor** - High-level processor for sending prompt objects to Ollama
3. **OllamaPromptValidator** - Validator for prompt objects before sending to Ollama
4. **Factory functions** - Easy creation of Ollama tools from configuration

## Prerequisites

1. **Install Ollama**: Follow the installation instructions at [ollama.ai](https://ollama.ai)
2. **Start Ollama server**: Run `ollama serve` in a terminal
3. **Pull a model**: Install a model like `ollama pull llama3.2`

## Configuration

Add Ollama configuration to your `config.yaml`:

```yaml
llm:
  provider: "ollama"
  model: "llama3.2"
  host: "localhost"
  port: 11434
  temperature: 0.7
  max_tokens: 1000
```

## Using the Python Tools

### OllamaPromptProcessor

The `OllamaPromptProcessor` provides a high-level interface for processing prompt templates:

```python
from ticket_master.ollama_tools import create_ollama_processor
from ticket_master.prompt import PromptTemplate, PromptType

# Create processor from config
config = {
    "host": "localhost",
    "port": 11434,
    "model": "llama3.2"
}
processor = create_ollama_processor(config)

# Create a prompt template
template = PromptTemplate(
    name="issue_generator",
    prompt_type=PromptType.ISSUE_GENERATION,
    base_template="Generate {num} GitHub issues for {repo}",
    provider_variations={
        "ollama": "Create {num} actionable GitHub issues for repository {repo}"
    }
)

# Process the prompt
result = processor.process_prompt(
    template, 
    {"num": 3, "repo": "my-project"},
    temperature=0.7
)

print(result["response"])
print(result["metadata"])
```

### Generating Issues from Repository Analysis

The processor includes a specialized method for generating GitHub issues:

```python
# Repository analysis data (from ticket_master.repository)
analysis_data = {
    "repository_info": {"path": "/path/to/repo"},
    "analysis_summary": {
        "commit_count": 10,
        "files_modified": 5,
        "files_added": 2,
        "total_insertions": 100,
        "total_deletions": 50
    },
    "commits": [
        {"short_hash": "abc123", "summary": "Add feature"},
        {"short_hash": "def456", "summary": "Fix bug"}
    ]
}

# Generate issues
issues = processor.generate_issues_from_analysis(
    analysis_data,
    max_issues=5
)

for issue in issues:
    print(f"Title: {issue['title']}")
    print(f"Description: {issue['description']}")
    print(f"Labels: {issue['labels']}")
    print("---")
```

### Batch Processing

Process multiple prompts in a single call:

```python
prompts = [
    {"template": template1, "variables": {"var1": "value1"}},
    {"template": template2, "variables": {"var2": "value2"}},
    {"template": template3, "variables": {"var3": "value3"}}
]

results = processor.batch_process_prompts(prompts, temperature=0.5)
```

### Model Management

The processor includes utilities for managing Ollama models:

```python
# Check model availability
availability = processor.check_model_availability("llama3.2")
print(f"Model available: {availability['available']}")

# Install a model
result = processor.install_model("codellama:7b")
if result["success"]:
    print("Model installed successfully")

# Get model information
info = processor.get_model_info("llama3.2")
print(f"Model parameters: {info['parameters']}")
```

### OllamaPromptValidator

Validate prompts before processing:

```python
from ticket_master.ollama_tools import OllamaPromptValidator

validator = OllamaPromptValidator()

# Validate template
validation = validator.validate_prompt_template(template)
if not validation["valid"]:
    print("Template issues:", validation["issues"])

# Validate variables
var_validation = validator.validate_variables(template, variables)
if var_validation["warnings"]:
    print("Variable warnings:", var_validation["warnings"])
```

## Enhanced OllamaBackend

The `OllamaBackend` class has been updated to use the official ollama Python client with fallback to HTTP requests:

```python
from ticket_master.llm import LLM

# Create LLM with enhanced Ollama backend
llm = LLM("ollama", {
    "host": "localhost",
    "port": 11434,
    "model": "llama3.2"
})

# Generate text
response = llm.generate(
    "Explain the benefits of using Ollama for local AI",
    temperature=0.7,
    max_tokens=500
)

print(response["response"])
print(response["metadata"])
```

## Integration with Main Application

When using Ollama as the LLM provider, Ticket-Master automatically uses the enhanced Ollama tools:

```bash
# Run with Ollama integration
python main.py owner/repo --dry-run --config config.yaml
```

The application will:
1. Try to use `OllamaPromptProcessor` for optimized issue generation
2. Fall back to standard `LLM` interface if the processor fails
3. Fall back to sample issues if Ollama is not available

## Error Handling

The Ollama integration includes comprehensive error handling:

- **Connection errors**: Automatic fallback to HTTP requests or sample generation
- **Model not found**: Clear error messages with suggestions
- **Invalid responses**: Response parsing with fallback to text extraction
- **API errors**: Detailed error reporting with context

## Performance Considerations

- **Model loading**: First request may be slower as the model loads
- **Memory usage**: Larger models require more RAM
- **Response time**: Local processing is typically faster than remote APIs
- **Concurrent requests**: Ollama handles multiple requests efficiently

## Troubleshooting

### Common Issues

1. **Connection refused**: Ensure Ollama server is running (`ollama serve`)
2. **Model not found**: Install the model with `ollama pull model-name`
3. **Slow responses**: Consider using a smaller model for faster generation
4. **Out of memory**: Use a smaller model or increase system RAM

### Debug Logging

Enable debug logging to see detailed information:

```python
import logging
logging.getLogger("OllamaPromptProcessor").setLevel(logging.DEBUG)
```

Or via command line:
```bash
python main.py owner/repo --log-level DEBUG
```

## Examples

See the `tests/test_ollama_tools.py` file for comprehensive examples of using the Ollama integration tools.

## API Reference

### OllamaPromptProcessor Methods

- `process_prompt(template, variables, model=None, **options)` - Process a single prompt
- `batch_process_prompts(prompts, model=None, **options)` - Process multiple prompts
- `generate_issues_from_analysis(analysis_data, max_issues=5, model=None)` - Generate GitHub issues
- `check_model_availability(model=None)` - Check if model is available
- `install_model(model=None)` - Install/pull a model
- `get_model_info(model=None)` - Get detailed model information

### OllamaPromptValidator Methods

- `validate_prompt_template(template)` - Validate template structure
- `validate_variables(template, variables)` - Validate template variables

### Factory Functions

- `create_ollama_processor(config)` - Create processor from configuration

## Best Practices

1. **Model Selection**: Choose appropriate models for your use case (smaller for speed, larger for quality)
2. **Template Design**: Use Ollama-specific prompt variations for better results
3. **Error Handling**: Always handle potential connection and model errors
4. **Resource Management**: Monitor memory usage with large models
5. **Prompt Engineering**: Experiment with different prompt formats for optimal results