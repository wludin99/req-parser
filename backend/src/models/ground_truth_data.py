"""
GroundTruthData model for evaluation and validation.

This model represents the known correct data for evaluating extraction accuracy.
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, date
from decimal import Decimal

from .tender_data import TenderData, ContractingAuthority, Contact


class GroundTruthData(BaseModel):
    """Ground truth data for evaluation purposes."""
    
    # Core identification
    ground_truth_id: str = Field(..., description="Unique identifier for the ground truth data")
    document_id: str = Field(..., description="Associated document ID")
    
    # Ground truth data (same structure as TenderData)
    tender_reference: str = Field(..., description="Correct tender reference number")
    publication_date: date = Field(..., description="Correct publication date")
    contracting_authority: ContractingAuthority = Field(..., description="Correct contracting authority details")
    subject: str = Field(..., description="Correct subject/title of the tender")
    description: str = Field(..., description="Correct detailed description")
    estimated_budget_eur: float = Field(..., ge=0, description="Correct estimated budget in EUR")
    eligibility_requirements: List[str] = Field(..., description="Correct eligibility requirements")
    tender_deadline: str = Field(..., description="Correct tender deadline")
    contact: Contact = Field(..., description="Correct contact person details")
    
    # Metadata
    created_at: Optional[datetime] = Field(None, description="When the ground truth was created")
    created_by: Optional[str] = Field(None, description="Who created the ground truth data")
    source: Optional[str] = Field(None, description="Source of the ground truth data")
    version: Optional[str] = Field(None, description="Version of the ground truth data")
    
    # Evaluation settings
    evaluation_weight: Optional[float] = Field(1.0, ge=0.0, le=1.0, description="Weight for this ground truth in evaluation")
    field_weights: Optional[Dict[str, float]] = Field(None, description="Individual field weights for evaluation")
    
    # Validation rules
    strict_mode: Optional[bool] = Field(True, description="Whether to use strict validation rules")
    tolerance_settings: Optional[Dict[str, Any]] = Field(None, description="Tolerance settings for fuzzy matching")
    
    class Config:
        """Pydantic configuration."""
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            Decimal: lambda v: float(v)
        }
        schema_extra = {
            "example": {
                "ground_truth_id": "gt-123",
                "document_id": "doc-123",
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
                "created_at": "2024-09-27T21:00:00Z",
                "created_by": "evaluator@example.com",
                "source": "manual_annotation",
                "version": "1.0",
                "evaluation_weight": 1.0,
                "field_weights": {
                    "tender_reference": 1.0,
                    "publication_date": 1.0,
                    "contracting_authority": 0.9,
                    "subject": 1.0,
                    "description": 0.8,
                    "estimated_budget_eur": 1.0,
                    "eligibility_requirements": 0.9,
                    "tender_deadline": 1.0,
                    "contact": 0.8
                },
                "strict_mode": True,
                "tolerance_settings": {
                    "string_similarity_threshold": 0.8,
                    "numeric_tolerance_percentage": 0.05,
                    "date_tolerance_days": 0
                }
            }
        }
    
    def to_tender_data(self) -> TenderData:
        """Convert ground truth data to TenderData format."""
        return TenderData(
            tender_reference=self.tender_reference,
            publication_date=self.publication_date,
            contracting_authority=self.contracting_authority,
            subject=self.subject,
            description=self.description,
            estimated_budget_eur=self.estimated_budget_eur,
            eligibility_requirements=self.eligibility_requirements,
            tender_deadline=self.tender_deadline,
            contact=self.contact,
            confidence_score=1.0,  # Ground truth is always 100% confident
            extraction_timestamp=self.created_at,
            source_document_id=self.document_id
        )
    
    def get_field_weight(self, field_name: str) -> float:
        """Get evaluation weight for a specific field."""
        if self.field_weights and field_name in self.field_weights:
            return self.field_weights[field_name]
        return 1.0  # Default weight
    
    def get_tolerance_setting(self, setting_name: str, default_value: Any = None) -> Any:
        """Get tolerance setting for evaluation."""
        if self.tolerance_settings and setting_name in self.tolerance_settings:
            return self.tolerance_settings[setting_name]
        return default_value
    
    def is_strict_mode(self) -> bool:
        """Check if strict evaluation mode is enabled."""
        return self.strict_mode is True
    
    def get_evaluation_weight(self) -> float:
        """Get overall evaluation weight."""
        return self.evaluation_weight or 1.0
    
    def validate_against_extracted(self, extracted_data: TenderData) -> Dict[str, Any]:
        """Validate extracted data against ground truth."""
        validation_results = {
            "overall_match": True,
            "field_matches": {},
            "field_scores": {},
            "discrepancies": [],
            "overall_score": 0.0
        }
        
        # Compare each field
        fields_to_compare = [
            "tender_reference", "publication_date", "contracting_authority",
            "subject", "description", "estimated_budget_eur",
            "eligibility_requirements", "tender_deadline", "contact"
        ]
        
        total_score = 0.0
        total_weight = 0.0
        
        for field in fields_to_compare:
            field_weight = self.get_field_weight(field)
            field_score = self._compare_field(field, extracted_data)
            
            validation_results["field_matches"][field] = field_score == 1.0
            validation_results["field_scores"][field] = field_score
            
            if field_score < 1.0:
                validation_results["overall_match"] = False
                validation_results["discrepancies"].append({
                    "field": field,
                    "extracted_value": getattr(extracted_data, field),
                    "ground_truth_value": getattr(self, field),
                    "similarity_score": field_score
                })
            
            total_score += field_score * field_weight
            total_weight += field_weight
        
        validation_results["overall_score"] = total_score / total_weight if total_weight > 0 else 0.0
        
        return validation_results
    
    def _compare_field(self, field_name: str, extracted_data: TenderData) -> float:
        """Compare a specific field between ground truth and extracted data."""
        ground_truth_value = getattr(self, field_name)
        extracted_value = getattr(extracted_data, field_name)
        
        if ground_truth_value == extracted_value:
            return 1.0
        
        # Apply tolerance settings for fuzzy matching
        if field_name in ["tender_reference", "subject", "description"]:
            return self._string_similarity(ground_truth_value, extracted_value)
        elif field_name == "estimated_budget_eur":
            return self._numeric_similarity(ground_truth_value, extracted_value)
        elif field_name == "eligibility_requirements":
            return self._list_similarity(ground_truth_value, extracted_value)
        elif field_name == "contracting_authority":
            return self._object_similarity(ground_truth_value, extracted_value)
        elif field_name == "contact":
            return self._object_similarity(ground_truth_value, extracted_value)
        else:
            return 0.0
    
    def _string_similarity(self, str1: str, str2: str) -> float:
        """Calculate string similarity score."""
        if not str1 or not str2:
            return 0.0
        
        # Simple similarity based on common words
        words1 = set(str1.lower().split())
        words2 = set(str2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _numeric_similarity(self, num1: float, num2: float) -> float:
        """Calculate numeric similarity score."""
        if num1 == num2:
            return 1.0
        
        if num1 == 0 or num2 == 0:
            return 0.0
        
        # Calculate percentage difference
        diff = abs(num1 - num2) / max(num1, num2)
        tolerance = self.get_tolerance_setting("numeric_tolerance_percentage", 0.05)
        
        return 1.0 - min(1.0, diff / tolerance)
    
    def _list_similarity(self, list1: List[str], list2: List[str]) -> float:
        """Calculate list similarity score."""
        if not list1 or not list2:
            return 0.0
        
        # Convert to sets for comparison
        set1 = set(item.strip().lower() for item in list1)
        set2 = set(item.strip().lower() for item in list2)
        
        intersection = set1.intersection(set2)
        union = set1.union(set2)
        
        return len(intersection) / len(union) if union else 0.0
    
    def _object_similarity(self, obj1: Any, obj2: Any) -> float:
        """Calculate object similarity score."""
        if hasattr(obj1, 'dict') and hasattr(obj2, 'dict'):
            # Pydantic models
            dict1 = obj1.dict()
            dict2 = obj2.dict()
        elif isinstance(obj1, dict) and isinstance(obj2, dict):
            dict1 = obj1
            dict2 = obj2
        else:
            return 0.0
        
        if dict1 == dict2:
            return 1.0
        
        # Calculate average similarity of all fields
        total_score = 0.0
        field_count = 0
        
        for key in dict1:
            if key in dict2:
                if isinstance(dict1[key], str) and isinstance(dict2[key], str):
                    score = self._string_similarity(dict1[key], dict2[key])
                else:
                    score = 1.0 if dict1[key] == dict2[key] else 0.0
                
                total_score += score
                field_count += 1
        
        return total_score / field_count if field_count > 0 else 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert model to dictionary."""
        return self.dict()
    
    def to_json(self) -> str:
        """Convert model to JSON string."""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GroundTruthData':
        """Create model from dictionary."""
        return cls(**data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'GroundTruthData':
        """Create model from JSON string."""
        return cls.parse_raw(json_str)
    
    @classmethod
    def from_tender_data(cls, tender_data: TenderData, ground_truth_id: str, **kwargs) -> 'GroundTruthData':
        """Create ground truth data from TenderData."""
        return cls(
            ground_truth_id=ground_truth_id,
            document_id=tender_data.source_document_id or "unknown",
            tender_reference=tender_data.tender_reference,
            publication_date=tender_data.publication_date,
            contracting_authority=tender_data.contracting_authority,
            subject=tender_data.subject,
            description=tender_data.description,
            estimated_budget_eur=tender_data.estimated_budget_eur,
            eligibility_requirements=tender_data.eligibility_requirements,
            tender_deadline=tender_data.tender_deadline,
            contact=tender_data.contact,
            created_at=datetime.utcnow(),
            **kwargs
        )
