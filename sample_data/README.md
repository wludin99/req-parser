# Sample Documents and Ground Truth Data

This directory contains sample tender documents and their corresponding ground truth data for testing and evaluation purposes.

## Files

### Sample Tender Documents
- `sample_tender_1.txt` - EU renewable energy infrastructure tender
- `sample_tender_2.txt` - UK smart city transportation tender  
- `sample_tender_3.txt` - French digital healthcare platform tender

### Ground Truth Data
- `ground_truth_1.json` - Ground truth for sample_tender_1.txt
- `ground_truth_2.json` - Ground truth for sample_tender_2.txt
- `ground_truth_3.json` - Ground truth for sample_tender_3.txt

## Usage

These sample documents can be used to:

1. **Test Document Processing**: Upload the `.txt` files to test the document processing pipeline
2. **Evaluate Extraction Accuracy**: Compare extracted data against the ground truth JSON files
3. **Performance Testing**: Use these documents to measure processing time and accuracy
4. **Development and Testing**: Use as test data during development

## Document Characteristics

### Sample 1: EU Renewable Energy Tender
- **Language**: English
- **Complexity**: Medium
- **Key Features**: Multiple eligibility requirements, detailed contact information, budget in euros
- **Challenges**: Long description, multiple requirements, specific formatting

### Sample 2: UK Smart City Tender  
- **Language**: English
- **Complexity**: Medium
- **Key Features**: UK-specific requirements, budget in pounds, technical specifications
- **Challenges**: Technical terminology, specific certification requirements

### Sample 3: French Healthcare Tender
- **Language**: English (French context)
- **Complexity**: High
- **Key Features**: Healthcare-specific requirements, high budget, technical specifications
- **Challenges**: Complex technical requirements, multiple certifications, large budget

## Ground Truth Format

Each ground truth JSON file contains the following structure:

```json
{
  "tender_reference": "string",
  "publication_date": "YYYY-MM-DD",
  "contracting_authority": {
    "name": "string",
    "address": "string"
  },
  "subject": "string",
  "description": "string",
  "estimated_budget_eur": number,
  "eligibility_requirements": ["string", ...],
  "tender_deadline": "string",
  "contact": {
    "name": "string",
    "email": "string"
  }
}
```

## Testing Scenarios

### Accuracy Testing
1. Upload each sample document
2. Extract structured data using the system
3. Compare extracted data with ground truth
4. Calculate accuracy metrics

### Performance Testing
1. Measure processing time for each document
2. Test with multiple concurrent uploads
3. Verify processing completes within 10 seconds

### Edge Case Testing
1. Test with documents of varying lengths
2. Test with different formatting styles
3. Test with missing or incomplete information

## Expected Accuracy

Based on the document complexity and content quality:

- **Sample 1**: Expected accuracy > 90%
- **Sample 2**: Expected accuracy > 85%  
- **Sample 3**: Expected accuracy > 80%

## Notes

- All documents are in English for consistency
- Budgets are normalized to EUR in ground truth
- Contact information is standardized
- Dates follow ISO format (YYYY-MM-DD)
- Requirements are listed as separate items in arrays
