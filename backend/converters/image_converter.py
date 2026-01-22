"""
Image format converter
Handles conversions between various image formats
"""
import os
from PIL import Image
import img2pdf


class ImageConverter:
    """Converts between different image formats"""
    
    def __init__(self):
        """Initialize image converter"""
        pass
    
    def convert(self, input_path, output_path, target_format, quality=None, max_width=None, max_height=None):
        """
        Convert image to target format
        
        Args:
            input_path: Source image file path
            output_path: Output file path
            target_format: Target format (png, jpg, pdf, etc.)
            quality: Image quality (1-100), None for default
            max_width: Maximum width for resizing, None to keep original
            max_height: Maximum height for resizing, None to keep original
            
        Returns:
            bool: True if successful
        """
        target_format = target_format.lower()
        
        # Special handling for PDF
        if target_format == 'pdf':
            return self._convert_to_pdf(input_path, output_path)
        
        # Standard image conversion using Pillow
        try:
            with Image.open(input_path) as img:
                # Resize if dimensions specified
                if max_width or max_height:
                    img = self._resize_image(img, max_width, max_height)
                
                # Convert RGBA to RGB for formats that don't support transparency
                if target_format in ['jpg', 'jpeg'] and img.mode in ['RGBA', 'LA', 'P']:
                    # Create white background
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                    img = background
                
                # Ensure correct mode for target format
                if target_format in ['jpg', 'jpeg']:
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                elif target_format == 'png':
                    if img.mode not in ['RGB', 'RGBA']:
                        img = img.convert('RGBA')
                
                # Save with appropriate settings
                save_kwargs = {}
                if target_format in ['jpg', 'jpeg']:
                    save_kwargs['quality'] = quality if quality else 95
                    save_kwargs['optimize'] = True
                elif target_format == 'png':
                    save_kwargs['optimize'] = True
                    if quality:
                        # PNG compression level (0-9, inverse of quality)
                        save_kwargs['compress_level'] = max(0, min(9, int((100 - quality) / 11)))
                
                img.save(output_path, format=target_format.upper(), **save_kwargs)
                return True
                
        except Exception as e:
            raise Exception(f"Image conversion failed: {str(e)}")
    
    def _convert_to_pdf(self, input_path, output_path):
        """Convert image to PDF"""
        try:
            # Open and process image
            with Image.open(input_path) as img:
                # Convert to RGB if necessary
                if img.mode in ['RGBA', 'LA', 'P']:
                    background = Image.new('RGB', img.size, (255, 255, 255))
                    if img.mode == 'P':
                        img = img.convert('RGBA')
                    if img.mode in ['RGBA', 'LA']:
                        background.paste(img, mask=img.split()[-1])
                        img = background
                    else:
                        img = background
                
                # Save as temporary RGB image if needed
                temp_path = None
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                    temp_path = input_path + '.temp.jpg'
                    img.save(temp_path, 'JPEG')
                    input_path = temp_path
            
            # Convert to PDF using img2pdf
            with open(output_path, 'wb') as f:
                f.write(img2pdf.convert(input_path))
            
            # Clean up temp file
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)
            
            return True
            
        except Exception as e:
            raise Exception(f"Image to PDF conversion failed: {str(e)}")
    
    def _resize_image(self, img, max_width=None, max_height=None):
        """
        Resize image maintaining aspect ratio
        
        Args:
            img: PIL Image object
            max_width: Maximum width
            max_height: Maximum height
            
        Returns:
            PIL Image: Resized image
        """
        width, height = img.size
        
        # Calculate new dimensions
        if max_width and max_height:
            # Fit within both dimensions
            ratio = min(max_width / width, max_height / height)
        elif max_width:
            ratio = max_width / width
        elif max_height:
            ratio = max_height / height
        else:
            return img
        
        # Only resize if image is larger
        if ratio < 1:
            new_width = int(width * ratio)
            new_height = int(height * ratio)
            return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        return img
    
    def compress_image(self, input_path, output_path, quality=85, max_width=None, max_height=None):
        """
        Compress image with quality and size options
        
        Args:
            input_path: Source image file path
            output_path: Output file path
            quality: Compression quality (1-100)
            max_width: Maximum width for resizing
            max_height: Maximum height for resizing
            
        Returns:
            dict: Information about the compression
        """
        try:
            original_size = os.path.getsize(input_path)
            
            with Image.open(input_path) as img:
                original_format = img.format.lower()
                
                # Resize if needed
                if max_width or max_height:
                    img = self._resize_image(img, max_width, max_height)
                
                # Determine output format (prefer JPG for compression)
                if original_format in ['png', 'bmp', 'tiff']:
                    # Convert to JPG for better compression
                    if img.mode in ['RGBA', 'LA', 'P']:
                        background = Image.new('RGB', img.size, (255, 255, 255))
                        if img.mode == 'P':
                            img = img.convert('RGBA')
                        if img.mode in ['RGBA', 'LA']:
                            background.paste(img, mask=img.split()[-1])
                            img = background
                    elif img.mode != 'RGB':
                        img = img.convert('RGB')
                    
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
                else:
                    # Keep original format
                    if img.mode != 'RGB':
                        img = img.convert('RGB')
                    img.save(output_path, 'JPEG', quality=quality, optimize=True)
            
            compressed_size = os.path.getsize(output_path)
            compression_ratio = (1 - compressed_size / original_size) * 100
            
            return {
                'success': True,
                'original_size': original_size,
                'compressed_size': compressed_size,
                'compression_ratio': round(compression_ratio, 2),
                'output_path': output_path
            }
            
        except Exception as e:
            raise Exception(f"Image compression failed: {str(e)}")
    
    def batch_convert(self, input_paths, output_dir, target_format):
        """
        Convert multiple images
        
        Args:
            input_paths: List of input file paths
            output_dir: Output directory
            target_format: Target format
            
        Returns:
            dict: Results with success/failure for each file
        """
        results = {}
        
        for input_path in input_paths:
            try:
                filename = os.path.splitext(os.path.basename(input_path))[0]
                output_path = os.path.join(output_dir, f"{filename}.{target_format}")
                
                self.convert(input_path, output_path, target_format)
                results[input_path] = {'status': 'success', 'output': output_path}
            except Exception as e:
                results[input_path] = {'status': 'failed', 'error': str(e)}
        
        return results
