#!/usr/bin/env python
"""
Quick start script for Document Converter
"""
import os
import sys

def check_dependencies():
    """Check if all required dependencies are installed"""
    required = {
        'Flask': 'Flask',
        'flask_cors': 'Flask-CORS',
        'PIL': 'Pillow',
        'PyPDF2': 'PyPDF2',
        'fitz': 'PyMuPDF',
        'apscheduler': 'APScheduler'
    }
    
    missing = []
    for module, package in required.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (missing)")
            missing.append(package)
    
    optional = {
        'pytesseract': 'pytesseract (for OCR)',
        'pdf2image': 'pdf2image (for OCR)'
    }
    
    print("\nOptional dependencies:")
    for module, package in optional.items():
        try:
            __import__(module)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} (optional)")
    
    if missing:
        print(f"\n⚠ Missing required dependencies: {', '.join(missing)}")
        print("Install with: pip install -r requirements.txt")
        return False
    
    print("\n✓ All required dependencies installed!")
    return True

def main():
    """Start the Flask application"""
    print("=" * 60)
    print("Document Converter - Starting Server")
    print("=" * 60)
    print()
    
    # Check dependencies
    print("Checking dependencies...")
    if not check_dependencies():
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("Starting Flask server on http://localhost:5000")
    print("=" * 60)
    print()
    print("Features available:")
    print("  ✓ Batch file conversion")
    print("  ✓ Image compression")
    print("  ✓ PDF merge/split")
    print("  ✓ PDF to images")
    print("  ✓ OCR text extraction (if dependencies installed)")
    print("  ✓ Automatic session cleanup")
    print()
    print("Press Ctrl+C to stop the server")
    print()
    
    # Import and run Flask app
    try:
        from backend.app import app
        app.run(debug=True, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n\nServer stopped.")
    except Exception as e:
        print(f"\n⚠ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
