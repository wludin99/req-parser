# Quickstart: Government Tender Extraction System

## Prerequisites
- Python 3.11+
- OpenAI API key (or Hugging Face account)
- Sample tender documents (PDF or text format)

## Setup Instructions

### 1. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Frontend Setup
```bash
cd frontend
npm install
```

### 3. Configuration
Create `backend/config/llm_config.yaml`:
```yaml
openai:
  api_key: "your_openai_key_here"
  model: "gpt-4o-mini"
  max_tokens: 2000
  temperature: 0.1

huggingface:
  api_key: "your_hf_key_here"
  model: "google/flan-t5-large"
  max_tokens: 1000
  temperature: 0.1

extraction:
  max_retries: 3
  retry_delay: 1.0
  chunk_size: 1000
  chunk_overlap: 200
```

### 4. Database Setup
```bash
cd backend
python -c "from src.models import create_tables; create_tables()"
```

## Running the System

### 1. Start Backend
```bash
cd backend
source venv/bin/activate
uvicorn src.main:app --reload --port 8000
```

### 2. Start Frontend
```bash
cd frontend
npm start
```

### 3. Access Application
Open http://localhost:3000 in your browser

### 4. Process Documents
- Upload PDF or text documents through the web interface
- View real-time processing status
- See extracted data and evaluation metrics
- Download results as JSON

## Usage Guide

### Document Processing
1. Place PDF or text documents in `data/sample_documents/`
2. Run extraction command with document path
3. View extracted data in JSON format
4. Check processing logs for any issues

### Ground Truth Evaluation
1. Create ground truth JSON files in `data/ground_truth/`
2. Run extraction with `--ground-truth` flag
3. View accuracy metrics and field-level comparisons
4. Review discrepancies for improvement

### Expected Behavior
- Document processing should complete within 10 seconds
- Extracted data should match the required schema
- Accuracy metrics should be calculated for ground truth comparisons
- Error messages should be clear and actionable

## Testing the System

### Test Scenarios
1. **Valid PDF Processing**: Process a well-formatted tender document
2. **Text File Processing**: Process a .txt file with tender information
3. **Ground Truth Evaluation**: Compare extracted data with known correct values
4. **Error Handling**: Test with malformed documents or invalid files
5. **Retry Logic**: Test with temporary LLM service issues

### Success Criteria
- All documents are processed successfully
- Extracted data matches the required schema
- Ground truth evaluation provides accurate metrics
- Error handling provides clear feedback
- Processing completes within time constraints

## Sample Data Structure

### Input Document
Place tender documents in `data/sample_documents/` with clear naming:
- `tender_001.pdf`
- `tender_002.txt`
- `tender_003.pdf`

### Ground Truth Format
Create `data/ground_truth/tender_001.json`:
```json
{
  "tender_reference": "EU-EN-2024-056",
  "publication_date": "2024-06-14",
  "contracting_authority": {
    "name": "Ministry of Energy Transition",
    "address": "12 Rue de Rivoli, 75001 Paris, France"
  },
  "subject": "Supply and installation of solar photovoltaic systems...",
  "description": "The Ministry seeks suppliers capable of delivering...",
  "estimated_budget_eur": 2500000.0,
  "eligibility_requirements": [
    "At least 3 prior contracts of similar scope in the last 5 years.",
    "Certification in ISO 14001 (Environmental Management).",
    "Proof of financial capacity."
  ],
  "tender_deadline": "2024-07-30 17:00 CET",
  "contact": {
    "name": "Marie Dubois",
    "email": "marie.dubois@transition.gouv.fr"
  }
}
```

## Troubleshooting

### Common Issues
- **API Key Errors**: Check configuration files and environment variables
- **Document Processing Fails**: Verify file format and content
- **Low Accuracy**: Review ground truth data and extraction prompts
- **Timeout Errors**: Check network connection and API limits

### Performance Notes
- First document processing may take longer due to model loading
- Large documents (>10MB) may require chunking
- Network latency affects LLM API response times
- Ground truth evaluation adds processing time but provides quality metrics
