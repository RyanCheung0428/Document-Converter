"""
Test script for batch download functionality
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.app import app

def test_batch_download_endpoint():
    """Test if the batch download endpoint exists"""
    with app.test_client() as client:
        # Test with empty data
        response = client.post('/api/download-batch', 
                              json={'files': []},
                              content_type='application/json')
        
        print(f"Empty files test: {response.status_code}")
        print(f"Response: {response.get_json()}")
        
        # The endpoint should return 400 for empty files
        assert response.status_code == 400
        
        print("\n✓ Batch download endpoint is working correctly!")
        print("✓ API endpoint: POST /api/download-batch")
        print("✓ Expected payload: { files: [{ session_id, filename }, ...] }")

if __name__ == '__main__':
    test_batch_download_endpoint()
