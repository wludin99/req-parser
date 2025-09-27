"""
TenderData model for structured tender information.

This model represents the extracted structured data from government tender documents.
"""
from pydantic import BaseModel, Field, EmailStr, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from decimal import Decimal


class ContractingAuthority(BaseModel):
    """Contracting authority information."""
    name: str = Field(..., description="Name of the contracting authority")
    address: str = Field(..., description="Full address of the contracting authority")


class Contact(BaseModel):
    """Contact information for the tender."""
    name: str = Field(..., description="Name of the contact person")
    email: EmailStr = Field(..., description="Email address of the contact person")


class TenderData(BaseModel):
    """Structured tender data extracted from documents."""
    
    # Core identification
    tender_reference: str = Field(..., description="Unique tender reference number")
    publication_date: date = Field(..., description="Date when the tender was published")
    
    # Authority information
    contracting_authority: ContractingAuthority = Field(..., description="Contracting authority details")
    
    # Tender content
    subject: str = Field(..., description="Subject/title of the tender")
    description: str = Field(..., description="Detailed description of the tender")
    
    # Financial information
    estimated_budget_eur: float = Field(..., ge=0, description="Estimated budget in EUR")
    
    # Requirements and deadlines
    eligibility_requirements: List[str] = Field(..., description="List of eligibility requirements")
    tender_deadline: str = Field(..., description="Tender submission deadline")
    
    # Contact information
    contact: Contact = Field(..., description="Contact person details")
    
    # Metadata
    confidence_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Confidence score for extraction accuracy")
    extraction_timestamp: Optional[datetime] = Field(None, description="When the data was extracted")
    source_document_id: Optional[str] = Field(None, description="ID of the source document")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "tender_reference": "EU-EN-2024-056",
                "publication_date": "2024-06-14",
                "contracting_authority": {
                    "name": "Ministry of Energy Transition",
                    "address": "12 Rue de Rivoli, 75001 Paris, France"
                },
                "subject": "Supply and installation of solar photovoltaic systems for public schools in the Île-de-France region.",
                "description": "The Ministry seeks suppliers capable of delivering and installing rooftop solar PV systems with a minimum installed capacity of 500 kW across 10 schools. The contractor is also responsible for maintenance for 5 years.",
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
                },
                "confidence_score": 0.95,
                "extraction_timestamp": "2024-09-27T21:00:00Z",
                "source_document_id": "doc-123"
            }
        }
    
    @validator('tender_reference')
    def validate_tender_reference(cls, v):
        """Validate tender reference format."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Tender reference cannot be empty')
        return v.strip()
    
    @validator('subject')
    def validate_subject(cls, v):
        """Validate subject is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Subject cannot be empty')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validate description is not empty."""
        if not v or len(v.strip()) == 0:
            raise ValueError('Description cannot be empty')
        return v.strip()
    
    @validator('eligibility_requirements')
    def validate_eligibility_requirements(cls, v):
        """Validate eligibility requirements list."""
        if not v or len(v) == 0:
            raise ValueError('At least one eligibility requirement must be specified')
        
        # Filter out empty requirements
        filtered = [req.strip() for req in v if req.strip()]
        if len(filtered) == 0:
            raise ValueError('At least one non-empty eligibility requirement must be specified')
        
        return filtered
    
    @validator('tender_deadline')
    def validate_tender_deadline(cls, v):
        """Validate tender deadline format."""
        if not v:
            raise ValueError('Tender deadline cannot be empty')
        # If it's a string, strip it; if it's already a datetime, return as-is
        if isinstance(v, str):
            return v.strip()
        return v
    
    @validator('estimated_budget_eur')
    def validate_estimated_budget(cls, v):
        """Validate estimated budget is positive."""
        if v < 0:
            raise ValueError('Estimated budget must be non-negative')
        return v
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.model_dump()
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TenderData':
        """Create model from dictionary."""
        # Convert date strings to date objects if needed
        if 'publication_date' in data and isinstance(data['publication_date'], str):
            from datetime import datetime
            data['publication_date'] = datetime.fromisoformat(data['publication_date']).date()
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'TenderData':
        """Create model from JSON string."""
        return cls.parse_raw(json_str)
    
    def get_field_accuracy(self, field_name: str) -> Optional[float]:
        """Get accuracy score for a specific field if available."""
        # This would be populated by the evaluation system
        return getattr(self, f'{field_name}_accuracy', None)
    
    def is_complete(self) -> bool:
        """Check if all required fields are populated."""
        required_fields = [
            'tender_reference', 'publication_date', 'contracting_authority',
            'subject', 'description', 'estimated_budget_eur',
            'eligibility_requirements', 'tender_deadline', 'contact'
        ]
        
        for field in required_fields:
            value = getattr(self, field)
            if value is None or (isinstance(value, str) and len(value.strip()) == 0):
                return False
            if isinstance(value, list) and len(value) == 0:
                return False
        
        return True
    
    def get_missing_fields(self) -> List[str]:
        """Get list of missing or empty required fields."""
        missing = []
        required_fields = [
            'tender_reference', 'publication_date', 'contracting_authority',
            'subject', 'description', 'estimated_budget_eur',
            'eligibility_requirements', 'tender_deadline', 'contact'
        ]
        
        for field in required_fields:
            value = getattr(self, field)
            if value is None or (isinstance(value, str) and len(value.strip()) == 0):
                missing.append(field)
            elif isinstance(value, list) and len(value) == 0:
                missing.append(field)
        
        return missing
