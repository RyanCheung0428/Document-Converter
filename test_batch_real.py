"""
Test batch download with actual file creation
"""
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from backend.app import app
import json

def setup_test_files():
    """Create test output files"""
    output_folder = Path(__file__).parent / 'outputs'
    test_session = 'test-session-123'
    session_folder = output_folder / test_session
    session_folder.mkdir(parents=True, exist_ok=True)
    
    # Create test files
    test_files = ['test1.pdf', 'test2.pdf', 'test3.pdf']
    for filename in test_files:
        file_path = session_folder / filename
        file_path.write_text(f'Test content for {filename}')
    
    return test_session, test_files

def test_batch_download():
    """Test batch download with real files"""
    test_session, test_files = setup_test_files()
    
    with app.test_client() as client:
        # Prepare request data
        files_info = [
            {'session_id': test_session, 'filename': filename}
            for filename in test_files
        ]
        
        print(f"Testing batch download with {len(files_info)} files...")
        print(f"Files: {files_info}")
        
        # Make request
        response = client.post(
            '/api/download-batch',
            data=json.dumps({'files': files_info}),
            content_type='application/json'
        )
        
        print(f"\nResponse status: {response.status_code}")
        print(f"Content type: {response.content_type}")
        print(f"Content length: {len(response.data)} bytes")
        
        if response.status_code == 200:
            print("\nSUCCESS: Batch download endpoint is working!")
            print(f"ZIP file size: {len(response.data)} bytes")
            
            # Verify it's a valid ZIP
            import zipfile
            import io
            try:
                zip_data = io.BytesIO(response.data)
                with zipfile.ZipFile(zip_data, 'r') as zipf:
                    print(f"ZIP contains {len(zipf.namelist())} files:")
                    for name in zipf.namelist():
                        print(f"  - {name}")
            except Exception as e:
                print(f"ERROR: Invalid ZIP file: {e}")
        else:
            print(f"\nERROR: {response.get_json()}")
    
    # Cleanup
    import shutil
    session_folder = Path(__file__).parent / 'outputs' / test_session
    if session_folder.exists():
        shutil.rmtree(session_folder)

if __name__ == '__main__':
    test_batch_download()
