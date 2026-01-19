"""
Document format converter
Handles conversions between Word, Excel, and PDF formats
"""
import os
from docx import Document
from openpyxl import load_workbook, Workbook
from PyPDF2 import PdfReader, PdfWriter
from pdf2docx import Converter as PDFConverter
from PIL import Image
import img2pdf
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import io


class DocumentConverter:
    """Converts between document formats (Word, Excel, PDF)"""
    
    def __init__(self):
        """Initialize document converter"""
        pass
    
    def convert(self, input_path, output_path, target_format):
        """
        Convert document to target format
        
        Args:
            input_path: Source file path
            output_path: Output file path
            target_format: Target format (pdf, docx, xlsx, etc.)
            
        Returns:
            bool: True if successful
        """
        # Detect source format
        source_ext = os.path.splitext(input_path)[1].lower().lstrip('.')
        target_format = target_format.lower()
        
        # Route to appropriate converter
        if source_ext == 'pdf':
            return self._convert_from_pdf(input_path, output_path, target_format)
        elif source_ext in ['doc', 'docx']:
            return self._convert_from_word(input_path, output_path, target_format)
        elif source_ext in ['xls', 'xlsx']:
            return self._convert_from_excel(input_path, output_path, target_format)
        else:
            raise ValueError(f"Unsupported source format: {source_ext}")
    
    def _convert_from_pdf(self, input_path, output_path, target_format):
        """Convert from PDF to other formats"""
        if target_format in ['docx', 'doc']:
            return self._pdf_to_word(input_path, output_path)
        elif target_format in ['png', 'jpg', 'jpeg']:
            return self._pdf_to_image(input_path, output_path, target_format)
        elif target_format == 'xlsx':
            raise NotImplementedError("PDF to Excel conversion requires manual implementation or OCR")
        else:
            raise ValueError(f"Conversion from PDF to {target_format} not supported")
    
    def _convert_from_word(self, input_path, output_path, target_format):
        """Convert from Word to other formats"""
        if target_format == 'pdf':
            return self._word_to_pdf(input_path, output_path)
        elif target_format == 'docx':
            # Just copy if already docx
            if input_path.endswith('.docx'):
                import shutil
                shutil.copy2(input_path, output_path)
                return True
            else:
                raise NotImplementedError("DOC to DOCX requires MS Word or LibreOffice")
        else:
            raise ValueError(f"Conversion from Word to {target_format} not supported")
    
    def _convert_from_excel(self, input_path, output_path, target_format):
        """Convert from Excel to other formats"""
        if target_format == 'pdf':
            return self._excel_to_pdf(input_path, output_path)
        elif target_format == 'xlsx':
            # Just copy if already xlsx
            if input_path.endswith('.xlsx'):
                import shutil
                shutil.copy2(input_path, output_path)
                return True
            else:
                # Convert xls to xlsx
                wb = load_workbook(input_path)
                wb.save(output_path)
                return True
        else:
            raise ValueError(f"Conversion from Excel to {target_format} not supported")
    
    def _pdf_to_word(self, input_path, output_path):
        """Convert PDF to Word document"""
        try:
            cv = PDFConverter(input_path)
            cv.convert(output_path)
            cv.close()
            return True
        except Exception as e:
            raise Exception(f"PDF to Word conversion failed: {str(e)}")
    
    def _pdf_to_image(self, input_path, output_path, image_format):
        """Convert first page of PDF to image"""
        try:
            from pdf2image import pdfimages
            import fitz  # PyMuPDF
            
            # Open PDF
            pdf_document = fitz.open(input_path)
            
            # Convert first page
            page = pdf_document[0]
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))  # 2x zoom for better quality
            
            # Save as image
            if image_format in ['jpg', 'jpeg']:
                pix.save(output_path, 'jpeg')
            else:
                pix.save(output_path, 'png')
            
            pdf_document.close()
            return True
            
        except ImportError:
            # Fallback method using PIL and PyPDF2
            print("PyMuPDF not available, using alternative method")
            raise Exception("PDF to image conversion requires PyMuPDF (fitz). Install with: pip install PyMuPDF")
    
    def _word_to_pdf(self, input_path, output_path):
        """Convert Word document to PDF"""
        try:
            # Try using docx2pdf (requires MS Word on Windows)
            from docx2pdf import convert
            convert(input_path, output_path)
            return True
        except Exception as e:
            # Fallback: Create basic PDF from docx content
            print(f"docx2pdf failed: {e}")
            try:
                return self._word_to_pdf_manual(input_path, output_path)
            except Exception as e2:
                raise Exception(f"Word to PDF conversion failed: {str(e2)}")
    
    def _word_to_pdf_manual(self, input_path, output_path):
        """Manual Word to PDF conversion using reportlab"""
        try:
            # Read Word document
            doc = Document(input_path)
            
            # Create PDF
            c = canvas.Canvas(output_path, pagesize=letter)
            width, height = letter
            
            y_position = height - 50
            left_margin = 50
            
            for para in doc.paragraphs:
                text = para.text
                if text.strip():
                    # Simple text rendering (doesn't preserve formatting)
                    c.drawString(left_margin, y_position, text[:100])  # Limit length
                    y_position -= 20
                    
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50
            
            c.save()
            return True
        except Exception as e:
            raise Exception(f"Manual Word to PDF conversion failed: {str(e)}")
    
    def _excel_to_pdf(self, input_path, output_path):
        """Convert Excel to PDF"""
        try:
            # Load workbook
            wb = load_workbook(input_path)
            ws = wb.active
            
            # Create PDF
            c = canvas.Canvas(output_path, pagesize=A4)
            width, height = A4
            
            y_position = height - 50
            left_margin = 50
            
            # Get data from worksheet
            for row in ws.iter_rows(values_only=True):
                row_text = ' | '.join([str(cell) if cell is not None else '' for cell in row])
                if row_text.strip():
                    c.drawString(left_margin, y_position, row_text[:100])
                    y_position -= 20
                    
                    if y_position < 50:
                        c.showPage()
                        y_position = height - 50
            
            c.save()
            return True
        except Exception as e:
            raise Exception(f"Excel to PDF conversion failed: {str(e)}")
    
    def batch_convert(self, input_paths, output_dir, target_format):
        """
        Convert multiple documents
        
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
