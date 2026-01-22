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

from flask import Flask, request, jsonify, send_file, render_template, after_this_request
from flask_cors import CORS
from werkzeug.utils import secure_filename
import shutil
import zipfile
from apscheduler.schedulers.background import BackgroundScheduler

# Import converters and utilities
from backend.utils.file_detector import FileDetector
from backend.converters.image_converter import ImageConverter
from backend.converters.document_converter import DocumentConverter
from backend.converters.pdf_tools import PDFTools
from backend.utils.session_cleaner import SessionCleaner

# Try to import OCR converter (optional)
try:
    from backend.converters.ocr_converter import OCRConverter
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

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
pdf_tools = PDFTools()
session_cleaner = SessionCleaner(
    app.config['UPLOAD_FOLDER'],
    app.config['OUTPUT_FOLDER'],
    max_age_hours=24
)

if OCR_AVAILABLE:
    try:
        ocr_converter = OCRConverter()
    except Exception:
        OCR_AVAILABLE = False

# Setup automatic cleanup scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=session_cleaner.cleanup_old_sessions,
    trigger="interval",
    hours=1,  # Run cleanup every hour
    id='session_cleanup'
)
scheduler.start()


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
        targets = file_detector.get_conversion_targets(format_type, file_format)
        
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
    quality = data.get('quality')  # Optional quality parameter
    max_width = data.get('max_width')  # Optional max width
    max_height = data.get('max_height')  # Optional max height
    
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
        output_filename = secure_filename(f"{base_name}.{target_format.lower()}") or f"{base_name}.{target_format.lower()}"
        output_path = output_folder / output_filename
        
        # Convert
        if format_type == 'image':
            image_converter.convert(
                str(input_path), 
                str(output_path), 
                target_format.lower(),
                quality=quality,
                max_width=max_width,
                max_height=max_height
            )
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


@app.route('/api/download-batch', methods=['POST'])
def download_batch():
    """Download multiple files as a ZIP archive"""
    zip_path = None
    try:
        data = request.get_json()
        print(f"[BATCH DOWNLOAD] Received request with data: {data}")
        
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        files_info = data.get('files', [])
        print(f"[BATCH DOWNLOAD] Files to process: {len(files_info)}")
        
        if not files_info:
            return jsonify({'success': False, 'error': 'No files specified'}), 400
        
        # Create a temporary ZIP file
        import time
        
        timestamp = int(time.time())
        zip_filename = f'converted_files_{timestamp}.zip'
        zip_path = app.config['OUTPUT_FOLDER'] / zip_filename
        print(f"[BATCH DOWNLOAD] Creating ZIP at: {zip_path}")
        
        # Create ZIP archive
        files_added = 0
        missing_files = []
        with zipfile.ZipFile(str(zip_path), 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_info in files_info:
                session_id = file_info.get('session_id')
                filename = file_info.get('filename')
                
                if not session_id or not filename:
                    print(f"[BATCH DOWNLOAD] Skipping invalid file info: {file_info}")
                    continue
                
                file_path = app.config['OUTPUT_FOLDER'] / session_id / secure_filename(filename)
                print(f"[BATCH DOWNLOAD] Looking for: {file_path}")
                
                if file_path.exists():
                    # Add file to ZIP with just the filename (no session path)
                    zipf.write(str(file_path), arcname=filename)
                    files_added += 1
                    print(f"[BATCH DOWNLOAD] Added: {filename}")
                else:
                    missing_files.append(str(file_path))
                    print(f"[BATCH DOWNLOAD] Missing: {file_path}")
        
        print(f"[BATCH DOWNLOAD] Files added: {files_added}, Missing: {len(missing_files)}")
        
        # Check if any files were added
        if files_added == 0:
            if zip_path.exists():
                zip_path.unlink()
            error_msg = f'No files found to download. Missing files: {missing_files}'
            print(f"[BATCH DOWNLOAD] ERROR: {error_msg}")
            return jsonify({'success': False, 'error': error_msg}), 404
        
        # Get ZIP file size
        zip_size = zip_path.stat().st_size
        print(f"[BATCH DOWNLOAD] ZIP created successfully: {zip_size} bytes")
        
        # Send the ZIP file using send_file with as_attachment
        # Flask will handle file closing properly
        print(f"[BATCH DOWNLOAD] Sending file...")
        
        @after_this_request
        def cleanup_zip(response):
            """Cleanup ZIP file after response is sent"""
            def remove_file(path):
                try:
                    import time
                    time.sleep(1)  # Give time for download to start
                    if path.exists():
                        path.unlink()
                        print(f"[BATCH DOWNLOAD] Cleaned up ZIP file: {path}")
                except Exception as e:
                    print(f"[BATCH DOWNLOAD] Cleanup error: {e}")
            
            import threading
            threading.Thread(target=remove_file, args=(zip_path,)).start()
            return response
        
        return send_file(
            str(zip_path),
            as_attachment=True,
            download_name=zip_filename,
            mimetype='application/zip'
        )
    
    except Exception as e:
        import traceback
        error_trace = traceback.format_exc()
        print(f"[BATCH DOWNLOAD] EXCEPTION: {e}")
        print(f"[BATCH DOWNLOAD] Traceback:\n{error_trace}")
        
        # Clean up ZIP file on error
        if zip_path and zip_path.exists():
            try:
                zip_path.unlink()
            except Exception:
                pass
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


@app.route('/api/compress', methods=['POST'])
def compress_image():
    """Compress image file"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    session_id = data.get('session_id')
    filename = data.get('filename')
    quality = data.get('quality', 85)
    max_width = data.get('max_width')
    max_height = data.get('max_height')
    
    if not all([session_id, filename]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        # Locate input file
        input_path = app.config['UPLOAD_FOLDER'] / session_id / secure_filename(filename)
        
        if not input_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Prepare output path
        output_folder = app.config['OUTPUT_FOLDER'] / session_id
        output_folder.mkdir(exist_ok=True)
        
        base_name = Path(filename).stem
        output_filename = secure_filename(f"{base_name}_compressed.jpg") or f"{base_name}_compressed.jpg"
        output_path = output_folder / output_filename
        
        # Compress
        result = image_converter.compress_image(
            str(input_path),
            str(output_path),
            quality=quality,
            max_width=max_width,
            max_height=max_height
        )
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'download_url': f'/api/download/{session_id}/{output_filename}',
            'original_size': result['original_size'],
            'compressed_size': result['compressed_size'],
            'compression_ratio': result['compression_ratio']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pdf/merge', methods=['POST'])
def merge_pdfs():
    """Merge multiple PDF files"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    files = data.get('files')  # List of {session_id, filename}
    output_session_id = data.get('output_session_id', str(uuid.uuid4()))
    
    if not files or len(files) < 2:
        return jsonify({'success': False, 'error': 'At least 2 files required'}), 400
    
    try:
        # Collect input paths
        input_paths = []
        for file_info in files:
            input_path = app.config['UPLOAD_FOLDER'] / file_info['session_id'] / secure_filename(file_info['filename'])
            if not input_path.exists():
                return jsonify({'success': False, 'error': f"File not found: {file_info['filename']}"}), 404
            input_paths.append(str(input_path))
        
        # Prepare output path
        output_folder = app.config['OUTPUT_FOLDER'] / output_session_id
        output_folder.mkdir(exist_ok=True)
        
        output_filename = 'merged.pdf'
        output_path = output_folder / output_filename
        
        # Merge
        result = pdf_tools.merge_pdfs(input_paths, str(output_path))
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'download_url': f'/api/download/{output_session_id}/{output_filename}',
            'total_files': result['total_files'],
            'total_pages': result['total_pages']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pdf/split', methods=['POST'])
def split_pdf():
    """Split PDF file"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    session_id = data.get('session_id')
    filename = data.get('filename')
    mode = data.get('mode', 'single')  # 'single', 'pages', 'range'
    pages = data.get('pages')  # For 'pages' or 'range' mode
    
    if not all([session_id, filename]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        # Locate input file
        input_path = app.config['UPLOAD_FOLDER'] / session_id / secure_filename(filename)
        
        if not input_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Prepare output directory
        output_folder = app.config['OUTPUT_FOLDER'] / session_id
        output_folder.mkdir(exist_ok=True)
        
        # Split
        result = pdf_tools.split_pdf(str(input_path), str(output_folder), mode=mode, pages=pages)
        
        # Generate download URLs
        download_urls = []
        for output_file in result['output_files']:
            file_name = Path(output_file).name
            download_urls.append({
                'filename': file_name,
                'url': f'/api/download/{session_id}/{file_name}'
            })
        
        return jsonify({
            'success': True,
            'total_pages': result['total_pages'],
            'file_count': result['file_count'],
            'files': download_urls
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pdf/info/<session_id>/<filename>', methods=['GET'])
def get_pdf_info(session_id, filename):
    """Get PDF file information"""
    try:
        file_path = app.config['UPLOAD_FOLDER'] / session_id / secure_filename(filename)
        
        if not file_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        info = pdf_tools.get_pdf_info(str(file_path))
        
        return jsonify({
            'success': True,
            'info': info
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/pdf/to-images', methods=['POST'])
def pdf_to_images():
    """Convert PDF to images"""
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    session_id = data.get('session_id')
    filename = data.get('filename')
    format = data.get('format', 'png')  # 'png', 'jpg', 'jpeg'
    dpi = data.get('dpi', 150)  # Resolution
    
    if not all([session_id, filename]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        # Locate input file
        input_path = app.config['UPLOAD_FOLDER'] / session_id / secure_filename(filename)
        
        if not input_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Prepare output directory
        output_folder = app.config['OUTPUT_FOLDER'] / session_id
        output_folder.mkdir(exist_ok=True)
        
        # Convert
        result = pdf_tools.pdf_to_images(
            str(input_path),
            str(output_folder),
            format=format,
            dpi=dpi
        )
        
        # Generate download URLs
        download_urls = []
        for output_file in result['output_files']:
            file_name = Path(output_file).name
            download_urls.append({
                'filename': file_name,
                'url': f'/api/download/{session_id}/{file_name}'
            })
        
        return jsonify({
            'success': True,
            'total_pages': result['total_pages'],
            'files': download_urls,
            'dpi': result['dpi'],
            'format': result['format']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ocr', methods=['POST'])
def ocr_extract():
    """Perform OCR on image or PDF"""
    if not OCR_AVAILABLE:
        return jsonify({
            'success': False, 
            'error': 'OCR not available. Install pytesseract and pdf2image.'
        }), 503
    
    data = request.get_json()
    
    if not data:
        return jsonify({'success': False, 'error': 'No data provided'}), 400
    
    session_id = data.get('session_id')
    filename = data.get('filename')
    file_type = data.get('file_type', 'image')  # 'image' or 'pdf'
    lang = data.get('lang', 'eng')  # Language code
    
    if not all([session_id, filename]):
        return jsonify({'success': False, 'error': 'Missing required fields'}), 400
    
    try:
        # Locate input file
        input_path = app.config['UPLOAD_FOLDER'] / session_id / secure_filename(filename)
        
        if not input_path.exists():
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        # Prepare output path
        output_folder = app.config['OUTPUT_FOLDER'] / session_id
        output_folder.mkdir(exist_ok=True)
        
        base_name = Path(filename).stem
        output_filename = secure_filename(f"{base_name}_ocr.txt") or f"{base_name}_ocr.txt"
        output_path = output_folder / output_filename
        
        # Perform OCR
        result = ocr_converter.ocr_to_text_file(
            str(input_path),
            str(output_path),
            file_type=file_type,
            lang=lang
        )
        
        return jsonify({
            'success': True,
            'output_filename': output_filename,
            'download_url': f'/api/download/{session_id}/{output_filename}',
            'pages': result['pages'],
            'total_characters': result['total_characters']
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/ocr/languages', methods=['GET'])
def get_ocr_languages():
    """Get available OCR languages"""
    if not OCR_AVAILABLE:
        return jsonify({'success': False, 'error': 'OCR not available'}), 503
    
    try:
        langs = ocr_converter.get_available_languages()
        return jsonify({
            'success': True,
            'languages': langs
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cleanup/stats', methods=['GET'])
def get_cleanup_stats():
    """Get session storage statistics"""
    try:
        stats = session_cleaner.get_folder_stats()
        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/cleanup/run', methods=['POST'])
def run_cleanup():
    """Manually trigger session cleanup"""
    try:
        stats = session_cleaner.cleanup_old_sessions()
        return jsonify({
            'success': True,
            'stats': stats
        })
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
