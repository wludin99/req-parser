"""
Debug tests for API endpoints to identify issues.
"""
import pytest
import traceback
from fastapi.testclient import TestClient
from src.main import app


class TestAPIDebug:
    """Debug tests to identify API issues."""

    @pytest.fixture
    def client(self):
        """Create test client for the FastAPI app."""
        return TestClient(app)

    def test_extract_endpoint_basic(self, client):
        """Test basic extract endpoint functionality."""
        try:
            text_content = 'European Union Tender Notice\nPublication Date: 14 June 2024\nTender Reference: EU-EN-2024-056'
            response = client.post('/extract', files={'file': ('test.txt', text_content.encode('utf-8'), 'text/plain')})
            
            print(f"Response Status: {response.status_code}")
            print(f"Response Headers: {dict(response.headers)}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                print(f"Document ID: {data.get('document_id')}")
                print(f"Status: {data.get('processing_status')}")
                print(f"Confidence Score: {data.get('confidence_score')}")
                print(f"Processing Time: {data.get('processing_time')}s")
                print(f"Extracted Data Keys: {list(data.get('extracted_data', {}).keys())}")
                print(f"Tender Reference: {data.get('extracted_data', {}).get('tender_reference')}")
                print(f"Publication Date: {data.get('extracted_data', {}).get('publication_date')}")
                print(f"Tender Deadline: {data.get('extracted_data', {}).get('tender_deadline')}")
                
                # Assertions
                assert response.status_code == 200
                assert "document_id" in data
                assert "processing_status" in data
                assert "extracted_data" in data
                assert data["processing_status"] == "completed"
                
            else:
                print(f"❌ ERROR: {response.text[:500]}...")
                # Print full error for debugging
                print(f"Full Error Response: {response.text}")
                pytest.fail(f"API call failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            traceback.print_exc()
            pytest.fail(f"Test failed with exception: {e}")

    def test_extract_endpoint_detailed(self, client):
        """Test extract endpoint with more detailed tender content."""
        try:
            text_content = '''European Union Tender Notice
Publication Date: 14 June 2024
Tender Reference: EU-EN-2024-056
Contracting Authority: Ministry of Energy Transition
Subject: Supply and installation of solar photovoltaic systems
Description: The Ministry seeks suppliers for solar PV systems.
Estimated Budget: 2,500,000 EUR
Eligibility Requirements: 3 prior contracts, ISO 14001
Tender Deadline: 30 July 2024, 17:00 CET
Contact: Marie Dubois, marie.dubois@transition.gouv.fr'''
            
            response = client.post('/extract', files={'file': ('test.txt', text_content.encode('utf-8'), 'text/plain')})
            
            print(f"Response Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print("✅ SUCCESS!")
                print(f"Document ID: {data.get('document_id')}")
                print(f"Status: {data.get('processing_status')}")
                print(f"Confidence Score: {data.get('confidence_score')}")
                print(f"Processing Time: {data.get('processing_time')}s")
                
                extracted_data = data.get('extracted_data', {})
                print(f"Extracted Data Keys: {list(extracted_data.keys())}")
                print(f"Tender Reference: {extracted_data.get('tender_reference')}")
                print(f"Publication Date: {extracted_data.get('publication_date')}")
                print(f"Subject: {extracted_data.get('subject')}")
                print(f"Estimated Budget: {extracted_data.get('estimated_budget_eur')}")
                print(f"Tender Deadline: {extracted_data.get('tender_deadline')}")
                
                # Assertions
                assert response.status_code == 200
                assert "document_id" in data
                assert "processing_status" in data
                assert "extracted_data" in data
                assert data["processing_status"] == "completed"
                assert extracted_data.get('tender_reference') == "EU-EN-2024-056"
                
            else:
                print(f"❌ ERROR: {response.text[:500]}...")
                print(f"Full Error Response: {response.text}")
                pytest.fail(f"API call failed with status {response.status_code}: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
            traceback.print_exc()
            pytest.fail(f"Test failed with exception: {e}")

    def test_mock_data_creation(self):
        """Test mock data creation directly."""
        try:
            from src.services.llm_extractor import LLMExtractor
            from datetime import date, datetime
            
            # Create LLM extractor
            extractor = LLMExtractor()
            
            # Test mock data creation
            mock_data = extractor._extract_with_mock("test text", None)
            
            print("✅ Mock data created successfully!")
            print(f"Tender Reference: {mock_data.tender_reference}")
            print(f"Publication Date: {mock_data.publication_date}")
            print(f"Subject: {mock_data.subject}")
            print(f"Estimated Budget: {mock_data.estimated_budget_eur}")
            print(f"Tender Deadline: {mock_data.tender_deadline}")
            
            # Assertions
            assert mock_data.tender_reference == "EU-EN-2024-056"
            assert mock_data.publication_date == date(2024, 6, 14)
            assert mock_data.subject == "Supply and installation of solar photovoltaic systems"
            assert mock_data.estimated_budget_eur == 2500000.0
            assert mock_data.tender_deadline == "2024-07-30 17:00 CET"
            
        except Exception as e:
            print(f"❌ Mock data creation failed: {e}")
            traceback.print_exc()
            pytest.fail(f"Mock data creation failed: {e}")

    def test_tender_data_model_direct(self):
        """Test TenderData model creation directly."""
        try:
            from src.models.tender_data import TenderData
            from datetime import date
            
            # Test direct model creation
            tender_data = TenderData(
                tender_reference="EU-EN-2024-056",
                publication_date=date(2024, 6, 14),
                contracting_authority={
                    "name": "Ministry of Energy Transition",
                    "address": "12 Rue de Rivoli, 75001 Paris, France"
                },
                subject="Supply and installation of solar photovoltaic systems",
                description="The Ministry seeks suppliers for solar PV systems.",
                estimated_budget_eur=2500000.0,
                eligibility_requirements=["3 prior contracts", "ISO 14001"],
                tender_deadline="2024-07-30 17:00 CET",
                contact={
                    "name": "Marie Dubois",
                    "email": "marie.dubois@transition.gouv.fr"
                }
            )
            
            print("✅ TenderData model created successfully!")
            print(f"Tender Reference: {tender_data.tender_reference}")
            print(f"Publication Date: {tender_data.publication_date}")
            print(f"Subject: {tender_data.subject}")
            print(f"Estimated Budget: {tender_data.estimated_budget_eur}")
            print(f"Tender Deadline: {tender_data.tender_deadline}")
            
            # Test to_dict method
            data_dict = tender_data.to_dict()
            print(f"✅ to_dict() method works: {len(data_dict)} fields")
            
            # Test from_dict method
            tender_data_2 = TenderData.from_dict(data_dict)
            print(f"✅ from_dict() method works: {tender_data_2.tender_reference}")
            
        except Exception as e:
            print(f"❌ TenderData model test failed: {e}")
            traceback.print_exc()
            pytest.fail(f"TenderData model test failed: {e}")
