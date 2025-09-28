"""
Simple API test to isolate the date issue.
"""
from fastapi.testclient import TestClient
from src.main import app


def test_simple_extract():
    """Test the simplest possible extract call."""
    client = TestClient(app)
    
    # Use more realistic tender document content
    text_content = """
    GOVERNMENT TENDER NOTICE
    
    Tender Reference: EU-EN-2024-056
    Publication Date: 2024-06-14
    
    Contracting Authority: Ministry of Energy Transition
    Address: 12 Rue de Rivoli, 75001 Paris, France
    
    Subject: Supply and installation of solar photovoltaic systems for government buildings
    
    Description: The Ministry seeks qualified suppliers for the supply and installation of solar photovoltaic systems across multiple government buildings. The project includes design, supply, installation, and maintenance of solar panels with a total capacity of 2MW.
    
    Estimated Budget: €2,500,000
    
    Eligibility Requirements:
    - Minimum 3 prior contracts in renewable energy sector
    - ISO 14001 environmental certification
    - Financial capacity of at least €1M
    
    Tender Deadline: 2024-07-30 17:00 CET
    
    Contact Person: Marie Dubois
    Email: marie.dubois@transition.gouv.fr
    """
    
    try:
        response = client.post('/extract', files={'file': ('test.txt', text_content.encode('utf-8'), 'text/plain')})
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
        else:
            print(f"❌ ERROR: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    test_simple_extract()
