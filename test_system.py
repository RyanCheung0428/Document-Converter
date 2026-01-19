"""
Test the file converter application
Run this to verify basic functionality
"""
import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    modules = {
        'PIL': 'Pillow',
        'docx': 'python-docx',
        'openpyxl': 'openpyxl',
        'PyPDF2': 'PyPDF2',
        'pdf2docx': 'pdf2docx',
        'img2pdf': 'img2pdf',
        'magic': 'python-magic-bin',
        'reportlab': 'reportlab',
    }
    
    failed = []
    
    for module, package in modules.items():
        try:
            __import__(module)
            print(f"  ✓ {package}")
        except ImportError as e:
            print(f"  ✗ {package}: {e}")
            failed.append(package)
    
    if failed:
        print(f"\n❌ Failed to import: {', '.join(failed)}")
        print("Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All modules imported successfully!")
        return True


def test_converters():
    """Test if converters can be instantiated"""
    print("\nTesting converters...")
    
    try:
        from utils.file_detector import FileDetector
        detector = FileDetector()
        print("  ✓ FileDetector")
        
        from converters.image_converter import ImageConverter
        img_conv = ImageConverter()
        print("  ✓ ImageConverter")
        
        from converters.document_converter import DocumentConverter
        doc_conv = DocumentConverter()
        print("  ✓ DocumentConverter")
        
        print("\n✅ All converters initialized successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Failed to initialize converters: {e}")
        return False


def main():
    """Run all tests"""
    print("=" * 50)
    print("Universal File Converter - System Check")
    print("=" * 50)
    print()
    
    imports_ok = test_imports()
    converters_ok = test_converters()
    
    print()
    print("=" * 50)
    
    if imports_ok and converters_ok:
        print("✅ System Ready!")
        print("\nYou can now run: python main.py")
    else:
        print("❌ System Not Ready")
        print("\nPlease fix the errors above before running the application.")
    
    print("=" * 50)


if __name__ == "__main__":
    main()
