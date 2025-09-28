# Data Model: Government Tender Extraction System

## Entities

### TenderData
Represents the structured data extracted from government tender documents.

**Fields**:
- `tender_reference`: str (Required, Max 100 chars)
- `publication_date`: str (Required, ISO date format YYYY-MM-DD)
- `contracting_authority`: dict (Required, contains name and address)
- `subject`: str (Required, Max 500 chars)
- `description`: str (Required, Max 2000 chars)
- `estimated_budget_eur`: float (Required, Positive number)
- `eligibility_requirements`: list[str] (Required, Non-empty list)
- `tender_deadline`: str (Required, ISO datetime format)
- `contact`: dict (Required, contains name and email)

**Validation Rules**:
- All fields must be present and non-empty
- Publication date must be valid ISO date format
- Estimated budget must be positive number
- Eligibility requirements must be non-empty list
- Contact must contain valid email format
- Tender deadline must be valid datetime format

**State Transitions**:
- `raw` → `validated` (when JSON validation passes)
- `validated` → `processed` (when extraction completes)
- `processed` → `evaluated` (when ground truth comparison done)

### ProcessingResult
Represents the outcome of document processing including success status and metrics.

**Fields**:
- `document_id`: str (Required, Unique identifier)
- `processing_status`: str (Required, Enum: 'pending', 'processing', 'completed', 'failed')
- `extracted_data`: TenderData (Optional, Only present if successful)
- `confidence_score`: float (Optional, 0.0-1.0 range)
- `processing_time`: float (Required, Seconds)
- `error_message`: str (Optional, Only present if failed)
- `retry_count`: int (Required, Number of retry attempts)
- `validation_errors`: list[str] (Optional, JSON validation issues)

**Validation Rules**:
- Document ID must be unique
- Processing status must be one of defined enum values
- Confidence score must be between 0.0 and 1.0
- Processing time must be positive
- Retry count must be non-negative

**State Transitions**:
- `pending` → `processing` (when extraction starts)
- `processing` → `completed` (when extraction succeeds)
- `processing` → `failed` (when extraction fails)
- `failed` → `pending` (when retry is initiated)

### GroundTruthData
Represents the known correct values for evaluation purposes.

**Fields**:
- `document_id`: str (Required, Matches ProcessingResult)
- `reference_data`: TenderData (Required, Known correct values)
- `evaluation_metrics`: dict (Required, Accuracy scores)
- `created_at`: datetime (Required, Auto-generated)

**Validation Rules**:
- Document ID must match corresponding ProcessingResult
- Reference data must be valid TenderData
- Evaluation metrics must contain accuracy scores
- Created timestamp must be valid datetime

## Database Schema

```sql
CREATE TABLE processing_results (
    document_id VARCHAR(100) PRIMARY KEY,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    extracted_data TEXT,
    confidence_score REAL,
    processing_time REAL NOT NULL,
    error_message TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    validation_errors TEXT,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE ground_truth_data (
    document_id VARCHAR(100) PRIMARY KEY,
    reference_data TEXT NOT NULL,
    evaluation_metrics TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (document_id) REFERENCES processing_results(document_id)
);
```

## Data Flow

1. **Document Upload**: Document uploaded → ProcessingResult created with 'pending' status
2. **Extraction**: Status updated to 'processing' → LLM extraction initiated
3. **Validation**: Extracted data validated against schema → Status updated based on validation
4. **Completion**: Valid data saved → Status updated to 'completed' with confidence score
5. **Evaluation**: Ground truth comparison → Evaluation metrics calculated and stored
6. **Error Handling**: Processing errors logged → Status updated to 'failed' → Retry mechanism available
