# Tender Extraction Backend

Backend API for extracting structured data from government tender documents using LLM processing.

## Features

- **Document Processing**: Extract text from PDF and text documents
- **LLM Integration**: Support for OpenAI GPT-4o mini and Hugging Face models (DeepSeek-V3-0324)
- **Structured Data Extraction**: Extract tender information using AI models
- **Ground Truth Evaluation**: Compare extracted data against known correct data
- **Real-time Updates**: WebSocket support for processing status updates
- **Database Storage**: SQLite database for storing processing results
- **RESTful API**: Clean API endpoints for frontend integration

## Architecture

### Core Components

- **Document Processor**: Handles PDF and text file processing
- **LLM Extractor**: Manages AI model integration and data extraction
- **Validator**: Validates extracted data and performs ground truth evaluation
- **Database Models**: SQLAlchemy models for data persistence
- **API Routes**: FastAPI endpoints for document processing and evaluation

### Data Models

- **TenderData**: Structured tender information extracted from documents
- **ProcessingResult**: Document processing outcomes and metadata
- **GroundTruthData**: Reference data for evaluation

## Setup

### Prerequisites

- Python 3.11+
- uv package manager

### Installation

```bash
# Install dependencies
uv sync

# Install development dependencies
uv sync --dev
```

### Environment Variables

Create a `.env` file in the backend directory:

```bash
# LLM API Keys (optional - system falls back to mock mode)
OPENAI_API_KEY=your_openai_api_key
HUGGINGFACE_API_KEY=your_huggingface_api_key

# Database (optional - defaults to SQLite)
DATABASE_URL=sqlite:///./tender_extraction.db
```

### Running the Server

```bash
# Development server with auto-reload
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Production server
uv run uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### Document Processing

- `POST /extract` - Extract structured data from uploaded document
- `POST /evaluate` - Evaluate extraction results against ground truth
- `GET /health` - Health check endpoint

### WebSocket

- `WS /ws/{document_id}` - Real-time processing updates

### Request/Response Examples

#### Extract Document

```bash
curl -X POST "http://localhost:8000/extract" \
  -F "file=@document.pdf" \
  -F "ground_truth={\"tender_reference\":\"EU-EN-2024-001\",...}"
```

#### Evaluate Results

```bash
curl -X POST "http://localhost:8000/evaluate" \
  -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc-123",
    "extracted_data": {...},
    "ground_truth": {...}
  }'
```

## Testing

### Running Tests

```bash
# Run all tests
uv run --with pytest python -m pytest

# Run specific test files
uv run --with pytest python -m pytest tests/unit/test_tender_data.py -v

# Run with coverage
uv run --with pytest python -m pytest --cov=src
```

### Test Structure

- `tests/unit/` - Unit tests for models and services
- `tests/contract/` - API contract tests
- `tests/integration/` - Integration tests
- `tests/debug/` - Debug and development tests

## Development

### Code Quality

```bash
# Format code
uv run black src tests

# Lint code
uv run flake8 src tests
```

### Database

The system uses SQLite by default with SQLAlchemy ORM. Database tables are created automatically on startup.

### Logging

Logs are written to `tender_extraction.log` and console output. Log levels can be configured in the main.py file.

## Deployment

### Docker (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install uv && uv sync

EXPOSE 8000
CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Configuration

For production deployment:

1. Set `DATABASE_URL` to a production database (PostgreSQL recommended)
2. Configure proper API keys for LLM services
3. Set up proper logging and monitoring
4. Configure CORS for your frontend domain

## Troubleshooting

### Common Issues

1. **Database Connection**: Ensure database URL is correct and accessible
2. **LLM API Limits**: System falls back to mock mode if API keys are missing or quota exceeded
3. **File Upload**: Ensure file size limits are appropriate for your use case
4. **CORS Issues**: Configure CORS middleware for your frontend domain

### Debug Mode

Enable debug logging by setting the log level to DEBUG in main.py:

```python
logging.basicConfig(level=logging.DEBUG)
```
