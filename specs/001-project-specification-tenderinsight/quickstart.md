# Quickstart: TenderInsight MVP

## Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key (or Hugging Face account)

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

### 3. Environment Configuration
Create `backend/.env`:
```
OPENAI_API_KEY=your_openai_key_here
HUGGINGFACE_API_KEY=your_hf_key_here
DATABASE_URL=sqlite:///./tenders.db
```

## Running the Application

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

## Usage Guide

### Upload a Document
1. Click "Upload Document" button
2. Select a PDF or text file
3. Wait for processing to complete
4. View extracted information in the table

### View Tender Details
1. Click on any tender row in the table
2. View full details including original file reference
3. See processing status and metadata

### Expected Behavior
- File uploads should complete within 5 seconds
- Extracted data appears in table immediately after processing
- Error messages display clearly if processing fails
- All tenders persist between browser sessions

## Testing the Application

### Test Scenarios
1. **Valid PDF Upload**: Upload a PDF with clear tender information
2. **Text File Upload**: Upload a .txt file with tender details
3. **Invalid File Type**: Try uploading an image file (should show error)
4. **Large Document**: Upload a large PDF to test processing time
5. **Network Error**: Test with invalid API keys to see error handling

### Success Criteria
- All file types are validated correctly
- Extracted data is accurate and complete
- Real-time status updates work during processing
- Error handling provides clear user feedback
- Application runs smoothly on local machine

## Troubleshooting

### Common Issues
- **API Key Errors**: Check environment variables are set correctly
- **Database Issues**: Ensure SQLite file permissions are correct
- **Port Conflicts**: Change ports in package.json and main.py if needed
- **File Upload Fails**: Check file size limits and supported formats

### Performance Notes
- First document processing may take longer due to model loading
- Subsequent uploads should be faster
- Large documents (>10MB) may take longer to process
- Network latency affects LLM API response times
