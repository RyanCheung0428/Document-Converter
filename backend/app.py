"""
Universal File Format Converter - Backend API
Flask-based REST API for file conversion
"""
import os
import sys
import uuid
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
from werkzeug.utils import secure_filename
import shutil

# Import converters and utilities
from backend.utils.file_detector import FileDetector
from backend.converters.image_converter import ImageConverter
from backend.converters.document_converter import DocumentConverter

# Get project root directory
ROOT_DIR = Path(__file__).parent.parent

app = Flask(__name__, 
            static_folder=str(ROOT_DIR / 'frontend' / 'static'), 
            template_folder=str(ROOT_DIR / 'frontend' / 'templates'))
CORS(app)

# Configuration
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size
app.config['UPLOAD_FOLDER'] = ROOT_DIR / 'uploads'
app.config['OUTPUT_FOLDER'] = ROOT_DIR / 'outputs'

# Create necessary folders
app.config['UPLOAD_FOLDER'].mkdir(exist_ok=True)
app.config['OUTPUT_FOLDER'].mkdir(exist_ok=True)

# Initialize converters
file_detector = FileDetector()
image_converter = ImageConverter()
document_converter = DocumentConverter()


@app.route('/')
def index():
    """Serve the main page"""
    return render_template('index.html')


@app.route('/api/formats', methods=['GET'])
def get_formats():
    """Get all supported formats"""
    formats = file_detector.get_supported_formats()
    return jsonify({
        'success': True,
        'formats': formats
    })


@app.route('/api/detect', methods=['POST'])
def detect_format():
    """Detect file format"""
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'success': False, 'error': 'Empty filename'}), 400
    
    try:
        # Save temporarily
        session_id = str(uuid.uuid4())
        session_folder = app.config['UPLOAD_FOLDER'] / session_id
        session_folder.mkdir(exist_ok=True)
        
        filename = secure_filename(file.filename)
        filepath = session_folder / filename
        file.save(filepath)
        
        # Detect format
        format_type, file_format = file_detector.detect_format(str(filepath))
        
        # Get available conversion targets
        targets = file_detector.get_conversion_targets(format_type)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'filename': filename,
            'detected_type': format_type,
            'detected_format': file_format,
            'available_targets': targets
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/convert', methods=['POST'])
def convert_file():
    """Convert file to target format"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    session_id = data.get('session_id')
    filename = data.get('filename')
    target_format = data.get('target_format')
    
    if not all([session_id, filename, target_format]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        # Locate input file
        input_path = app.config['UPLOAD_FOLDER'] / session_id / secure_filename(filename)
        
        if not input_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Detect format type
        format_type, _ = file_detector.detect_format(str(input_path))
        
        # Prepare output path
        output_folder = app.config['OUTPUT_FOLDER'] / session_id
        output_folder.mkdir(exist_ok=True)
        
        base_name = Path(filename).stem
        output_filename = f"{base_name}.{target_format.lower()}"
        output_path = output_folder / output_filename
        
        # Convert
        if format_type == 'image':
            image_converter.convert(str(input_path), str(output_path), target_format.lower())
        elif format_type == 'document':
            document_converter.convert(str(input_path), str(output_path), target_format.lower())
        else:
            return jsonify({'success': False, 'error': 'Unsupported format type'}), 400
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'download_url': f'/api/download/{session_id}/{output_filename}'
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/download/<session_id>/<filename>', methods=['GET'])
def download_file(session_id, filename):
    """Download converted file"""
    try:
        file_path = app.config['OUTPUT_FOLDER'] / session_id / secure_filename(filename)
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=filename
        )
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cleanup/<session_id>', methods=['DELETE'])
def cleanup_session(session_id):
    """Clean up session files"""
    try:
        upload_folder = app.config['UPLOAD_FOLDER'] / session_id
        output_folder = app.config['OUTPUT_FOLDER'] / session_id
        
        if upload_folder.exists():
            shutil.rmtree(upload_folder)
        
        if output_folder.exists():
            shutil.rmtree(output_folder)
        
        return jsonify({'success': True, 'message': 'Session cleaned up'})
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.errorhandler(413)
def file_too_large(e):
    """Handle file too large error"""
    return jsonify({'success': False, 'error': 'File too large (max 50MB)'}), 413


@app.errorhandler(404)
def not_found(e):
    """Handle not found error"""
    return jsonify({'success': False, 'error': 'Resource not found'}), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle internal server error"""
    return jsonify({'success': False, 'error': 'Internal server error'}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
