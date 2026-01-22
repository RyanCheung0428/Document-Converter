"""
PDF manipulation tools
Handles PDF merging, splitting, and other operations
"""
import os
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class PDFTools:
    """Tools for PDF manipulation"""
    
    def __init__(self):
        """Initialize PDF tools"""
        pass
    
    def merge_pdfs(self, input_paths, output_path):
        """
        Merge multiple PDF files into one
        
        Args:
            input_paths: List of PDF file paths to merge
            output_path: Output PDF file path
            
        Returns:
            dict: Information about the merge operation
        """
        try:
            if not input_paths or len(input_paths) < 2:
                raise Exception("At least 2 PDF files are required for merging")
            
            merger = PdfMerger()
            total_pages = 0
            
            for pdf_path in input_paths:
                if not os.path.exists(pdf_path):
                    raise Exception(f"File not found: {pdf_path}")
                
                reader = PdfReader(pdf_path)
                page_count = len(reader.pages)
                total_pages += page_count
                
                merger.append(pdf_path)
            
            merger.write(output_path)
            merger.close()
            
            return {
                'success': True,
                'total_files': len(input_paths),
                'total_pages': total_pages,
                'output_path': output_path
            }
            
        except Exception as e:
            raise Exception(f"PDF merge failed: {str(e)}")
    
    def split_pdf(self, input_path, output_dir, mode='pages', pages=None):
        """
        Split PDF file
        
        Args:
            input_path: Source PDF file path
            output_dir: Output directory for split files
            mode: Split mode ('pages', 'range', 'single')
                - 'pages': Split specific pages (requires pages parameter)
                - 'range': Split into page ranges
                - 'single': Split into individual pages
            pages: Page numbers or ranges (for 'pages' mode)
                Examples: [1, 3, 5] or [(1, 3), (5, 7)]
            
        Returns:
            dict: Information about the split operation
        """
        try:
            if not os.path.exists(input_path):
                raise Exception(f"File not found: {input_path}")
            
            reader = PdfReader(input_path)
            total_pages = len(reader.pages)
            output_files = []
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            if mode == 'single':
                # Split into individual pages
                for i in range(total_pages):
                    writer = PdfWriter()
                    writer.add_page(reader.pages[i])
                    
                    output_path = os.path.join(output_dir, f"{base_name}_page_{i+1}.pdf")
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(output_path)
            
            elif mode == 'pages' and pages:
                # Split specific pages
                for idx, page_spec in enumerate(pages):
                    writer = PdfWriter()
                    
                    if isinstance(page_spec, tuple):
                        # Page range
                        start, end = page_spec
                        for i in range(start - 1, min(end, total_pages)):
                            writer.add_page(reader.pages[i])
                        output_name = f"{base_name}_pages_{start}-{end}.pdf"
                    else:
                        # Single page
                        if page_spec <= total_pages:
                            writer.add_page(reader.pages[page_spec - 1])
                        output_name = f"{base_name}_page_{page_spec}.pdf"
                    
                    output_path = os.path.join(output_dir, output_name)
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(output_path)
            
            elif mode == 'range':
                # Split into ranges (every N pages)
                pages_per_file = pages if pages else 10
                
                for start_page in range(0, total_pages, pages_per_file):
                    writer = PdfWriter()
                    end_page = min(start_page + pages_per_file, total_pages)
                    
                    for i in range(start_page, end_page):
                        writer.add_page(reader.pages[i])
                    
                    output_path = os.path.join(
                        output_dir, 
                        f"{base_name}_part_{start_page//pages_per_file + 1}.pdf"
                    )
                    with open(output_path, 'wb') as output_file:
                        writer.write(output_file)
                    
                    output_files.append(output_path)
            
            return {
                'success': True,
                'total_pages': total_pages,
                'output_files': output_files,
                'file_count': len(output_files)
            }
            
        except Exception as e:
            raise Exception(f"PDF split failed: {str(e)}")
    
    def extract_pages(self, input_path, output_path, page_numbers):
        """
        Extract specific pages from PDF
        
        Args:
            input_path: Source PDF file path
            output_path: Output PDF file path
            page_numbers: List of page numbers to extract (1-indexed)
            
        Returns:
            bool: True if successful
        """
        try:
            reader = PdfReader(input_path)
            writer = PdfWriter()
            
            for page_num in page_numbers:
                if 1 <= page_num <= len(reader.pages):
                    writer.add_page(reader.pages[page_num - 1])
            
            with open(output_path, 'wb') as output_file:
                writer.write(output_file)
            
            return True
            
        except Exception as e:
            raise Exception(f"Page extraction failed: {str(e)}")
    
    def get_pdf_info(self, input_path):
        """
        Get PDF file information
        
        Args:
            input_path: PDF file path
            
        Returns:
            dict: PDF information
        """
        try:
            reader = PdfReader(input_path)
            
            info = {
                'page_count': len(reader.pages),
                'metadata': {}
            }
            
            # Get metadata if available
            if reader.metadata:
                info['metadata'] = {
                    'title': reader.metadata.get('/Title', ''),
                    'author': reader.metadata.get('/Author', ''),
                    'subject': reader.metadata.get('/Subject', ''),
                    'creator': reader.metadata.get('/Creator', '')
                }
            
            return info
            
        except Exception as e:
            raise Exception(f"Failed to get PDF info: {str(e)}")
    
    def pdf_to_images(self, input_path, output_dir, format='png', dpi=150):
        """
        Convert PDF pages to images
        
        Args:
            input_path: Source PDF file path
            output_dir: Output directory for images
            format: Output image format (png, jpg, jpeg)
            dpi: Resolution in DPI (default 150)
            
        Returns:
            dict: Information about the conversion
        """
        if not PYMUPDF_AVAILABLE:
            raise Exception("PyMuPDF not installed. Install with: pip install PyMuPDF")
        
        try:
            # Open PDF
            pdf_document = fitz.open(input_path)
            total_pages = len(pdf_document)
            output_files = []
            
            base_name = os.path.splitext(os.path.basename(input_path))[0]
            
            # Convert each page
            for page_num in range(total_pages):
                page = pdf_document[page_num]
                
                # Set resolution (zoom factor)
                zoom = dpi / 72  # 72 is the default DPI
                mat = fitz.Matrix(zoom, zoom)
                
                # Render page to image
                pix = page.get_pixmap(matrix=mat)
                
                # Save image
                output_filename = f"{base_name}_page_{page_num + 1}.{format.lower()}"
                output_path = os.path.join(output_dir, output_filename)
                
                if format.lower() in ['jpg', 'jpeg']:
                    pix.save(output_path, 'JPEG')
                else:
                    pix.save(output_path)
                
                output_files.append(output_path)
            
            pdf_document.close()
            
            return {
                'success': True,
                'total_pages': total_pages,
                'output_files': output_files,
                'dpi': dpi,
                'format': format
            }
            
        except Exception as e:
            raise Exception(f"PDF to images conversion failed: {str(e)}")
