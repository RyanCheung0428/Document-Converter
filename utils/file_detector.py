"""
File format detection utility
Automatically detects file formats using magic bytes and extensions
"""
import os
import magic


class FileDetector:
    """Detects file format automatically"""
    
    # Supported formats mapping
    SUPPORTED_FORMATS = {
        'document': ['docx', 'doc', 'xlsx', 'xls', 'pdf'],
        'image': ['png', 'jpg', 'jpeg', 'bmp', 'tiff', 'gif', 'webp', 'ico']
    }
    
    MIME_TO_FORMAT = {
        # Documents
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
        'application/msword': 'doc',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
        'application/vnd.ms-excel': 'xls',
        'application/pdf': 'pdf',
        
        # Images
        'image/png': 'png',
        'image/jpeg': 'jpg',
        'image/bmp': 'bmp',
        'image/tiff': 'tiff',
        'image/gif': 'gif',
        'image/webp': 'webp',
        'image/x-icon': 'ico',
        'image/vnd.microsoft.icon': 'ico'
    }
    
    def __init__(self):
        """Initialize the file detector"""
        self.magic = magic.Magic(mime=True)
    
    def detect_format(self, file_path):
        """
        Detect file format automatically
        
        Args:
            file_path: Path to the file
            
        Returns:
            tuple: (format_type, file_extension)
                   format_type: 'document' or 'image'
                   file_extension: detected extension (e.g., 'pdf', 'png')
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        # Try to detect using magic bytes
        try:
            mime_type = self.magic.from_file(file_path)
            detected_ext = self.MIME_TO_FORMAT.get(mime_type)
            
            if detected_ext:
                format_type = self._get_format_type(detected_ext)
                return format_type, detected_ext
        except Exception as e:
            print(f"Magic detection failed: {e}")
        
        # Fallback to extension
        ext = os.path.splitext(file_path)[1].lower().lstrip('.')
        if ext:
            format_type = self._get_format_type(ext)
            if format_type:
                return format_type, ext
        
        raise ValueError("Unable to detect file format")
    
    def _get_format_type(self, extension):
        """Get format type from extension"""
        for format_type, extensions in self.SUPPORTED_FORMATS.items():
            if extension in extensions:
                return format_type
        return None
    
    def get_supported_formats(self):
        """Get all supported formats"""
        return self.SUPPORTED_FORMATS
    
    def get_conversion_targets(self, source_format_type):
        """
        Get available conversion targets based on source format type
        
        Args:
            source_format_type: 'document' or 'image'
            
        Returns:
            list: Available target formats
        """
        if source_format_type == 'document':
            return ['pdf', 'docx', 'xlsx', 'png', 'jpg']
        elif source_format_type == 'image':
            return ['png', 'jpg', 'jpeg', 'pdf', 'bmp', 'tiff', 'gif', 'webp', 'ico']
        return []
    
    def is_supported(self, file_path):
        """Check if file format is supported"""
        try:
            self.detect_format(file_path)
            return True
        except:
            return False
