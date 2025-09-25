# Dockerfile for Ticket-Master
# AI-powered GitHub issue generator

# Use Python 3.12 slim image for smaller size
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY . .

# Copy example config to default config if config.yaml doesn't exist
RUN if [ ! -f config.yaml ]; then cp config.yaml.example config.yaml; fi

# Expose port (not needed for CLI app, but good practice)
EXPOSE 8000

# Default command shows help
CMD ["python", "main.py", "--help"]