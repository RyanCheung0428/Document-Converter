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
    
    def convert(self, input_path, output_path, target_format):
        """
        Convert image to target format
        
        Args:
            input_path: Source image file path
            output_path: Output file path
            target_format: Target format (png, jpg, pdf, etc.)
            
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
                    save_kwargs['quality'] = 95
                    save_kwargs['optimize'] = True
                elif target_format == 'png':
                    save_kwargs['optimize'] = True
                
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
