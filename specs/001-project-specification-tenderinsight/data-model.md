# Data Model: TenderInsight MVP

## Entities

### Tender
Represents a procurement opportunity with extracted metadata from uploaded documents.

**Fields**:
- `id`: int (Primary Key, Auto-increment)
- `title`: str (Required, Max 500 chars)
- `deadline`: str (Required, ISO date format)
- `budget`: str (Required, Max 100 chars)
- `file_url`: str (Required, File path reference)
- `uploaded_at`: datetime (Required, Auto-generated)
- `processing_status`: str (Required, Enum: 'pending', 'processing', 'completed', 'failed')
- `extraction_metadata`: str (Optional, JSON string with LLM response details)

**Validation Rules**:
- Title must not be empty
- Deadline must be valid ISO date format
- Budget must not be empty
- File URL must be valid path
- Processing status must be one of the defined enum values

**State Transitions**:
- `pending` → `processing` (when LLM processing starts)
- `processing` → `completed` (when extraction succeeds)
- `processing` → `failed` (when extraction fails)
- `failed` → `pending` (when retry is initiated)

### Document
Represents the original uploaded file with metadata about processing.

**Fields**:
- `id`: int (Primary Key, Auto-increment)
- `tender_id`: int (Foreign Key to Tender)
- `filename`: str (Required, Original filename)
- `file_type`: str (Required, Enum: 'pdf', 'txt')
- `file_size`: int (Required, Size in bytes)
- `upload_timestamp`: datetime (Required, Auto-generated)
- `processing_errors`: str (Optional, JSON string with error details)

**Validation Rules**:
- Filename must not be empty
- File type must be 'pdf' or 'txt'
- File size must be positive
- Tender ID must reference existing tender

**Relationships**:
- One-to-One with Tender (each document belongs to one tender)
- Tender can have one document

## Database Schema

```sql
CREATE TABLE tenders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(500) NOT NULL,
    deadline VARCHAR(50) NOT NULL,
    budget VARCHAR(100) NOT NULL,
    file_url VARCHAR(500) NOT NULL,
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    extraction_metadata TEXT
);

CREATE TABLE documents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tender_id INTEGER NOT NULL,
    filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(10) NOT NULL,
    file_size INTEGER NOT NULL,
    upload_timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processing_errors TEXT,
    FOREIGN KEY (tender_id) REFERENCES tenders(id)
);
```

## Data Flow

1. **Upload**: Document uploaded → Document record created → Tender record created with 'pending' status
2. **Processing**: Tender status updated to 'processing' → LLM extraction initiated
3. **Completion**: Extracted data saved to Tender → Status updated to 'completed'
4. **Error Handling**: Processing errors logged → Status updated to 'failed' → User can retry
