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
            
        except ImportError as e:
            # PyMuPDF not installed
            raise Exception(f"PDF to image conversion requires PyMuPDF (fitz). Install with: pip install PyMuPDF. Error: {str(e)}")
        except Exception as e:
            raise Exception(f"PDF to image conversion failed: {str(e)}")
    
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
        """Manual Word to PDF conversion using reportlab with formatting preservation"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.platypus import (
                SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, 
                PageBreak, ListFlowable, ListItem
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib.units import inch
            from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY
            from reportlab.pdfbase import pdfmetrics
            from reportlab.pdfbase.ttfonts import TTFont
            
            # Read Word document
            doc = Document(input_path)
            
            # Create PDF document
            pdf_doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=72,
                leftMargin=72,
                topMargin=72,
                bottomMargin=72
            )
            
            # Get styles
            styles = getSampleStyleSheet()
            story = []  # List of flowables
            
            # Create custom styles for different heading levels
            heading_styles = {
                'Heading 1': ParagraphStyle(
                    'CustomHeading1',
                    parent=styles['Heading1'],
                    fontSize=24,
                    textColor=colors.HexColor('#2F5496'),
                    spaceAfter=12,
                    spaceBefore=12,
                    leading=28
                ),
                'Heading 2': ParagraphStyle(
                    'CustomHeading2',
                    parent=styles['Heading2'],
                    fontSize=18,
                    textColor=colors.HexColor('#2F5496'),
                    spaceAfter=10,
                    spaceBefore=10,
                    leading=22
                ),
                'Heading 3': ParagraphStyle(
                    'CustomHeading3',
                    parent=styles['Heading3'],
                    fontSize=14,
                    textColor=colors.HexColor('#2F5496'),
                    spaceAfter=8,
                    spaceBefore=8,
                    leading=18
                ),
            }
            
            # Process paragraphs
            for para in doc.paragraphs:
                # Skip empty paragraphs
                if not para.text.strip():
                    story.append(Spacer(1, 0.1*inch))
                    continue
                
                # Determine paragraph style
                style_name = para.style.name
                
                # Handle headings
                if style_name.startswith('Heading'):
                    if style_name in heading_styles:
                        style = heading_styles[style_name]
                    elif 'Heading 1' in style_name:
                        style = heading_styles['Heading 1']
                    elif 'Heading 2' in style_name:
                        style = heading_styles['Heading 2']
                    elif 'Heading 3' in style_name:
                        style = heading_styles['Heading 3']
                    else:
                        style = styles['Heading1']
                else:
                    style = styles['Normal']
                
                # Handle text alignment
                if para.alignment == 1:  # Center
                    style = ParagraphStyle('TempCenter', parent=style, alignment=TA_CENTER)
                elif para.alignment == 2:  # Right
                    style = ParagraphStyle('TempRight', parent=style, alignment=TA_RIGHT)
                elif para.alignment == 3:  # Justify
                    style = ParagraphStyle('TempJustify', parent=style, alignment=TA_JUSTIFY)
                
                # Build formatted text from runs
                formatted_text = ""
                for run in para.runs:
                    text = run.text
                    if not text:
                        continue
                    
                    # Escape special XML characters
                    text = text.replace('&', '&amp;')
                    text = text.replace('<', '&lt;')
                    text = text.replace('>', '&gt;')
                    
                    # Apply formatting
                    if run.bold and run.italic:
                        text = f"<b><i>{text}</i></b>"
                    elif run.bold:
                        text = f"<b>{text}</b>"
                    elif run.italic:
                        text = f"<i>{text}</i>"
                    
                    if run.underline:
                        text = f"<u>{text}</u>"
                    
                    formatted_text += text
                
                # Add paragraph to story
                if formatted_text.strip():
                    try:
                        story.append(Paragraph(formatted_text, style))
                        story.append(Spacer(1, 0.1*inch))
                    except Exception as e:
                        # Fallback: use plain text if formatting fails
                        story.append(Paragraph(para.text, style))
                        story.append(Spacer(1, 0.1*inch))
            
            # Process tables
            for table in doc.tables:
                table_data = []
                
                # Extract table data
                for row in table.rows:
                    row_data = []
                    for cell in row.cells:
                        # Get cell text, handle merged cells
                        cell_text = cell.text.strip()
                        row_data.append(cell_text if cell_text else '')
                    table_data.append(row_data)
                
                if table_data:
                    # Create PDF table
                    pdf_table = Table(table_data)
                    
                    # Style the table
                    table_style = TableStyle([
                        # Header row (first row)
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0, 0), (-1, 0), 10),
                        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
                        
                        # Data rows
                        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                        ('FONTSIZE', (0, 1), (-1, -1), 9),
                        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                        
                        # Borders and grid
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        
                        # Alternating row colors
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                        
                        # Cell padding
                        ('TOPPADDING', (0, 0), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                        ('LEFTPADDING', (0, 0), (-1, -1), 8),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                        
                        # Vertical alignment
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ])
                    
                    pdf_table.setStyle(table_style)
                    story.append(pdf_table)
                    story.append(Spacer(1, 0.2*inch))
            
            # Build PDF
            pdf_doc.build(story)
            return True
            
        except Exception as e:
            raise Exception(f"Manual Word to PDF conversion failed: {str(e)}")
    
    def _excel_to_pdf(self, input_path, output_path):
        """Convert Excel to PDF with table formatting"""
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4, landscape
            from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, PageBreak
            from reportlab.lib.styles import getSampleStyleSheet
            from reportlab.lib.units import mm
            
            # Load workbook
            wb = load_workbook(input_path)
            ws = wb.active
            
            # Get all data from worksheet
            data = []
            for row in ws.iter_rows(values_only=True):
                # Convert None to empty string, limit cell length
                row_data = [str(cell)[:100] if cell is not None else '' for cell in row]
                data.append(row_data)
            
            if not data:
                raise Exception("No data found in Excel file")
            
            # Determine page orientation based on number of columns
            num_cols = len(data[0]) if data else 0
            pagesize = landscape(A4) if num_cols > 6 else A4
            
            # Create PDF with proper margins
            doc = SimpleDocTemplate(
                output_path,
                pagesize=pagesize,
                rightMargin=20,
                leftMargin=20,
                topMargin=20,
                bottomMargin=20
            )
            
            # Calculate column widths
            page_width = pagesize[0] - 40  # Account for margins
            if num_cols > 0:
                col_width = page_width / num_cols
                # Limit minimum column width
                col_width = max(col_width, 30)
                col_widths = [min(col_width, page_width / num_cols)] * num_cols
            else:
                col_widths = None
            
            # Create table with data
            table = Table(data, colWidths=col_widths, repeatRows=1)
            
            # Style the table
            table_style = TableStyle([
                # Header row styling
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                
                # Data rows styling
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                
                # Alternating row colors
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                
                # Cell padding
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('LEFTPADDING', (0, 0), (-1, -1), 6),
                ('RIGHTPADDING', (0, 0), (-1, -1), 6),
                
                # Vertical alignment
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ])
            
            table.setStyle(table_style)
            
            # Build PDF
            elements = [table]
            doc.build(elements)
            
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
