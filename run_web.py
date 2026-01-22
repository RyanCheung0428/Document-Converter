#!/usr/bin/env python3
"""
Quick start script for the web version
"""
import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import flask
        import flask_cors
        print("✓ Dependencies found")
        return True
    except ImportError:
        print("✗ Missing dependencies")
        print("\nInstalling required packages...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True

def create_directories():
    """Create necessary directories"""
    os.makedirs('uploads', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    print("✓ Directories created")

def main():
    print("=" * 50)
    print("Universal File Converter - Web Version")
    print("=" * 50)
    print()
    
    # Check dependencies
    check_dependencies()
    
    # Create directories
    create_directories()
    
    print()
    print("Starting server...")
    print("Access the application at: http://localhost:5000")
    print("Press Ctrl+C to stop")
    print()
    
    # Start the app
    subprocess.call([sys.executable, "app.py"])

if __name__ == '__main__':
    main()
