# Tender Extraction Backend

Backend API for extracting structured data from government tender documents using LLM processing.

## Setup

```bash
# Install dependencies
uv sync

# Run the development server
uv run uvicorn src.main:app --reload
```

## Testing

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=src
```
