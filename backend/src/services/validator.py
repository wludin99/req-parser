"""
Validator service for data validation and evaluation.

This service validates extracted data and evaluates it against ground truth.
"""
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import json
from difflib import SequenceMatcher

from ..models.tender_data import TenderData
from ..models.ground_truth_data import GroundTruthData
from ..models.processing_result import ProcessingResult


class Validator:
    """Service for validating and evaluating extracted data."""
    
    def __init__(self, similarity_threshold: float = 0.8):
        """
        Initialize validator.
        
        Args:
            similarity_threshold: Minimum similarity score for field matching
        """
        self.similarity_threshold = similarity_threshold
    
    def validate_extracted_data(self, extracted_data: TenderData) -> Dict[str, Any]:
        """
        Validate extracted data for completeness and correctness.
        
        Args:
            extracted_data: Extracted TenderData object
            
        Returns:
            Validation result dictionary
        """
        validation_result = {
            'is_valid': True,
            'confidence_score': 0.0,
            'validation_errors': [],
            'field_validation': {},
            'completeness_score': 0.0,
            'quality_indicators': {}
        }
        
        # Check completeness
        completeness_score = self._calculate_completeness(extracted_data)
        validation_result['completeness_score'] = completeness_score
        
        # Validate individual fields
        field_validation = self._validate_fields(extracted_data)
        validation_result['field_validation'] = field_validation
        
        # Check for validation errors
        validation_errors = self._get_validation_errors(extracted_data)
        validation_result['validation_errors'] = validation_errors
        
        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(extracted_data, field_validation)
        validation_result['confidence_score'] = confidence_score
        
        # Overall validity
        validation_result['is_valid'] = len(validation_errors) == 0 and completeness_score > 0.5
        
        # Quality indicators
        validation_result['quality_indicators'] = self._get_quality_indicators(extracted_data)
        
        return validation_result
    
    def _calculate_completeness(self, extracted_data: TenderData) -> float:
        """Calculate completeness score for extracted data."""
        required_fields = [
            'tender_reference', 'publication_date', 'contracting_authority',
            'subject', 'description', 'estimated_budget_eur',
            'eligibility_requirements', 'tender_deadline', 'contact'
        ]
        
        present_fields = 0
        for field in required_fields:
            value = getattr(extracted_data, field)
            if value is not None and value != '' and value != []:
                present_fields += 1
        
        return present_fields / len(required_fields)
    
    def _validate_fields(self, extracted_data: TenderData) -> Dict[str, Dict[str, Any]]:
        """Validate individual fields."""
        field_validation = {}
        
        # Validate tender reference
        field_validation['tender_reference'] = self._validate_tender_reference(
            extracted_data.tender_reference
        )
        
        # Validate publication date
        field_validation['publication_date'] = self._validate_publication_date(
            extracted_data.publication_date
        )
        
        # Validate contracting authority
        field_validation['contracting_authority'] = self._validate_contracting_authority(
            extracted_data.contracting_authority
        )
        
        # Validate subject
        field_validation['subject'] = self._validate_subject(
            extracted_data.subject
        )
        
        # Validate description
        field_validation['description'] = self._validate_description(
            extracted_data.description
        )
        
        # Validate estimated budget
        field_validation['estimated_budget_eur'] = self._validate_estimated_budget(
            extracted_data.estimated_budget_eur
        )
        
        # Validate eligibility requirements
        field_validation['eligibility_requirements'] = self._validate_eligibility_requirements(
            extracted_data.eligibility_requirements
        )
        
        # Validate tender deadline
        field_validation['tender_deadline'] = self._validate_tender_deadline(
            extracted_data.tender_deadline
        )
        
        # Validate contact
        field_validation['contact'] = self._validate_contact(
            extracted_data.contact
        )
        
        return field_validation
    
    def _validate_tender_reference(self, tender_reference: str) -> Dict[str, Any]:
        """Validate tender reference."""
        is_valid = bool(tender_reference and len(tender_reference.strip()) > 0)
        return {
            'is_valid': is_valid,
            'score': 1.0 if is_valid else 0.0,
            'errors': [] if is_valid else ['Tender reference is empty']
        }
    
    def _validate_publication_date(self, publication_date: str) -> Dict[str, Any]:
        """Validate publication date."""
        is_valid = bool(publication_date and len(publication_date.strip()) > 0)
        return {
            'is_valid': is_valid,
            'score': 1.0 if is_valid else 0.0,
            'errors': [] if is_valid else ['Publication date is empty']
        }
    
    def _validate_contracting_authority(self, contracting_authority: Any) -> Dict[str, Any]:
        """Validate contracting authority."""
        if not contracting_authority:
            return {
                'is_valid': False,
                'score': 0.0,
                'errors': ['Contracting authority is missing']
            }
        
        name_valid = bool(contracting_authority.get('name', '').strip())
        address_valid = bool(contracting_authority.get('address', '').strip())
        
        is_valid = name_valid and address_valid
        score = (1.0 if name_valid else 0.0) + (1.0 if address_valid else 0.0)
        score = score / 2.0
        
        errors = []
        if not name_valid:
            errors.append('Contracting authority name is missing')
        if not address_valid:
            errors.append('Contracting authority address is missing')
        
        return {
            'is_valid': is_valid,
            'score': score,
            'errors': errors
        }
    
    def _validate_subject(self, subject: str) -> Dict[str, Any]:
        """Validate subject."""
        is_valid = bool(subject and len(subject.strip()) > 10)  # Minimum length check
        return {
            'is_valid': is_valid,
            'score': 1.0 if is_valid else 0.0,
            'errors': [] if is_valid else ['Subject is too short or empty']
        }
    
    def _validate_description(self, description: str) -> Dict[str, Any]:
        """Validate description."""
        is_valid = bool(description and len(description.strip()) > 20)  # Minimum length check
        return {
            'is_valid': is_valid,
            'score': 1.0 if is_valid else 0.0,
            'errors': [] if is_valid else ['Description is too short or empty']
        }
    
    def _validate_estimated_budget(self, estimated_budget: float) -> Dict[str, Any]:
        """Validate estimated budget."""
        is_valid = estimated_budget is not None and estimated_budget > 0
        return {
            'is_valid': is_valid,
            'score': 1.0 if is_valid else 0.0,
            'errors': [] if is_valid else ['Estimated budget is invalid or missing']
        }
    
    def _validate_eligibility_requirements(self, requirements: List[str]) -> Dict[str, Any]:
        """Validate eligibility requirements."""
        is_valid = bool(requirements and len(requirements) > 0)
        return {
            'is_valid': is_valid,
            'score': 1.0 if is_valid else 0.0,
            'errors': [] if is_valid else ['No eligibility requirements found']
        }
    
    def _validate_tender_deadline(self, deadline: str) -> Dict[str, Any]:
        """Validate tender deadline."""
        is_valid = bool(deadline and len(deadline.strip()) > 0)
        return {
            'is_valid': is_valid,
            'score': 1.0 if is_valid else 0.0,
            'errors': [] if is_valid else ['Tender deadline is missing']
        }
    
    def _validate_contact(self, contact: Any) -> Dict[str, Any]:
        """Validate contact information."""
        if not contact:
            return {
                'is_valid': False,
                'score': 0.0,
                'errors': ['Contact information is missing']
            }
        
        name_valid = bool(contact.get('name', '').strip())
        email_valid = bool(contact.get('email', '').strip())
        
        is_valid = name_valid and email_valid
        score = (1.0 if name_valid else 0.0) + (1.0 if email_valid else 0.0)
        score = score / 2.0
        
        errors = []
        if not name_valid:
            errors.append('Contact name is missing')
        if not email_valid:
            errors.append('Contact email is missing')
        
        return {
            'is_valid': is_valid,
            'score': score,
            'errors': errors
        }
    
    def _get_validation_errors(self, extracted_data: TenderData) -> List[str]:
        """Get all validation errors."""
        errors = []
        
        try:
            extracted_data.validate()
        except Exception as e:
            errors.append(f"Pydantic validation error: {str(e)}")
        
        return errors
    
    def _calculate_confidence_score(self, extracted_data: TenderData, field_validation: Dict[str, Dict[str, Any]]) -> float:
        """Calculate overall confidence score."""
        if not field_validation:
            return 0.0
        
        scores = [field_data['score'] for field_data in field_validation.values()]
        return sum(scores) / len(scores) if scores else 0.0
    
    def _get_quality_indicators(self, extracted_data: TenderData) -> Dict[str, Any]:
        """Get quality indicators for the extracted data."""
        return {
            'has_reference': bool(extracted_data.tender_reference),
            'has_budget': bool(extracted_data.estimated_budget_eur and extracted_data.estimated_budget_eur > 0),
            'has_requirements': bool(extracted_data.eligibility_requirements and len(extracted_data.eligibility_requirements) > 0),
            'has_contact': bool(extracted_data.contact and extracted_data.contact.get('email')),
            'description_length': len(extracted_data.description) if extracted_data.description else 0,
            'requirements_count': len(extracted_data.eligibility_requirements) if extracted_data.eligibility_requirements else 0
        }
    
    def evaluate_against_ground_truth(self, document_id: str, extracted_data: TenderData, 
                                     ground_truth: GroundTruthData) -> Dict[str, Any]:
        """
        Evaluate extracted data against ground truth.
        
        Args:
            document_id: Document identifier
            extracted_data: Extracted TenderData object
            ground_truth: GroundTruthData object
            
        Returns:
            Evaluation result dictionary
        """
        evaluation_result = {
            'document_id': document_id,
            'overall_accuracy': 0.0,
            'field_accuracy': {},
            'completeness': 0.0,
            'discrepancies': [],
            'evaluation_timestamp': datetime.utcnow().isoformat()
        }
        
        # Use ground truth validation method
        validation_results = ground_truth.validate_against_extracted(extracted_data)
        
        evaluation_result['overall_accuracy'] = validation_results['overall_score']
        evaluation_result['field_accuracy'] = validation_results['field_scores']
        evaluation_result['discrepancies'] = validation_results['discrepancies']
        
        # Calculate completeness
        completeness = self._calculate_completeness(extracted_data)
        evaluation_result['completeness'] = completeness
        
        return evaluation_result
    
    def compare_extracted_data(self, data1: TenderData, data2: TenderData) -> Dict[str, Any]:
        """
        Compare two extracted data objects.
        
        Args:
            data1: First TenderData object
            data2: Second TenderData object
            
        Returns:
            Comparison result dictionary
        """
        comparison_result = {
            'similarity_score': 0.0,
            'field_comparisons': {},
            'differences': [],
            'overall_match': False
        }
        
        # Compare each field
        fields_to_compare = [
            'tender_reference', 'publication_date', 'contracting_authority',
            'subject', 'description', 'estimated_budget_eur',
            'eligibility_requirements', 'tender_deadline', 'contact'
        ]
        
        field_scores = []
        for field in fields_to_compare:
            value1 = getattr(data1, field)
            value2 = getattr(data2, field)
            
            similarity = self._calculate_field_similarity(field, value1, value2)
            field_scores.append(similarity)
            
            comparison_result['field_comparisons'][field] = {
                'similarity': similarity,
                'value1': value1,
                'value2': value2,
                'match': similarity >= self.similarity_threshold
            }
            
            if similarity < self.similarity_threshold:
                comparison_result['differences'].append({
                    'field': field,
                    'value1': value1,
                    'value2': value2,
                    'similarity': similarity
                })
        
        comparison_result['similarity_score'] = sum(field_scores) / len(field_scores) if field_scores else 0.0
        comparison_result['overall_match'] = comparison_result['similarity_score'] >= self.similarity_threshold
        
        return comparison_result
    
    def _calculate_field_similarity(self, field_name: str, value1: Any, value2: Any) -> float:
        """Calculate similarity between two field values."""
        if value1 == value2:
            return 1.0
        
        if not value1 or not value2:
            return 0.0
        
        if isinstance(value1, str) and isinstance(value2, str):
            return SequenceMatcher(None, value1.lower(), value2.lower()).ratio()
        
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            if value1 == 0 or value2 == 0:
                return 0.0
            return 1.0 - abs(value1 - value2) / max(abs(value1), abs(value2))
        
        if isinstance(value1, list) and isinstance(value2, list):
            if not value1 or not value2:
                return 0.0
            set1 = set(str(item).lower() for item in value1)
            set2 = set(str(item).lower() for item in value2)
            intersection = set1.intersection(set2)
            union = set1.union(set2)
            return len(intersection) / len(union) if union else 0.0
        
        if isinstance(value1, dict) and isinstance(value2, dict):
            return self._calculate_dict_similarity(value1, value2)
        
        return 0.0
    
    def _calculate_dict_similarity(self, dict1: Dict[str, Any], dict2: Dict[str, Any]) -> float:
        """Calculate similarity between two dictionaries."""
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())
        
        if not keys1 or not keys2:
            return 0.0
        
        common_keys = keys1.intersection(keys2)
        if not common_keys:
            return 0.0
        
        similarities = []
        for key in common_keys:
            similarity = self._calculate_field_similarity(key, dict1[key], dict2[key])
            similarities.append(similarity)
        
        return sum(similarities) / len(similarities) if similarities else 0.0
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> Dict[str, Any]:
        """Get a summary of validation results."""
        return {
            'is_valid': validation_result['is_valid'],
            'confidence_score': validation_result['confidence_score'],
            'completeness_score': validation_result['completeness_score'],
            'error_count': len(validation_result['validation_errors']),
            'field_count': len(validation_result['field_validation']),
            'quality_indicators': validation_result['quality_indicators']
        }
