"""
OCR (Optical Character Recognition) converter
Extracts text from images and PDFs
"""
import os
from PIL import Image
try:
    import pytesseract
    from pdf2image import convert_from_path
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


class OCRConverter:
    """Performs OCR on images and PDFs"""
    
    def __init__(self, tesseract_cmd=None):
        """
        Initialize OCR converter
        
        Args:
            tesseract_cmd: Path to tesseract executable (optional)
        """
        if not TESSERACT_AVAILABLE:
            raise Exception("OCR dependencies not installed. Install pytesseract and pdf2image.")
        
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
    
    def extract_text_from_image(self, image_path, lang='eng'):
        """
        Extract text from image file
        
        Args:
            image_path: Path to image file
            lang: Language code (e.g., 'eng', 'chi_tra', 'chi_sim')
            
        Returns:
            str: Extracted text
        """
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang=lang)
            return text
            
        except Exception as e:
            raise Exception(f"OCR failed: {str(e)}")
    
    def extract_text_from_pdf(self, pdf_path, lang='eng'):
        """
        Extract text from PDF file using OCR
        
        Args:
            pdf_path: Path to PDF file
            lang: Language code
            
        Returns:
            list: List of text strings (one per page)
        """
        try:
            # Convert PDF pages to images
            images = convert_from_path(pdf_path)
            
            texts = []
            for i, image in enumerate(images):
                text = pytesseract.image_to_string(image, lang=lang)
                texts.append(text)
            
            return texts
            
        except Exception as e:
            raise Exception(f"PDF OCR failed: {str(e)}")
    
    def image_to_searchable_pdf(self, image_path, output_path, lang='eng'):
        """
        Convert image to searchable PDF
        
        Args:
            image_path: Path to image file
            output_path: Output PDF path
            lang: Language code
            
        Returns:
            bool: True if successful
        """
        try:
            img = Image.open(image_path)
            pdf = pytesseract.image_to_pdf_or_hocr(img, lang=lang, extension='pdf')
            
            with open(output_path, 'wb') as f:
                f.write(pdf)
            
            return True
            
        except Exception as e:
            raise Exception(f"Searchable PDF creation failed: {str(e)}")
    
    def get_available_languages(self):
        """
        Get list of available OCR languages
        
        Returns:
            list: List of language codes
        """
        try:
            langs = pytesseract.get_languages()
            return langs
        except Exception:
            return ['eng']  # Default fallback
    
    def ocr_to_text_file(self, input_path, output_path, file_type='image', lang='eng'):
        """
        Perform OCR and save result to text file
        
        Args:
            input_path: Path to input file (image or PDF)
            output_path: Path to output text file
            file_type: 'image' or 'pdf'
            lang: Language code
            
        Returns:
            dict: Information about the OCR operation
        """
        try:
            if file_type == 'image':
                text = self.extract_text_from_image(input_path, lang=lang)
                texts = [text]
            elif file_type == 'pdf':
                texts = self.extract_text_from_pdf(input_path, lang=lang)
            else:
                raise Exception(f"Unsupported file type: {file_type}")
            
            # Write to output file
            with open(output_path, 'w', encoding='utf-8') as f:
                for i, text in enumerate(texts):
                    if len(texts) > 1:
                        f.write(f"=== Page {i + 1} ===\n\n")
                    f.write(text)
                    f.write("\n\n")
            
            total_chars = sum(len(t) for t in texts)
            
            return {
                'success': True,
                'pages': len(texts),
                'total_characters': total_chars,
                'output_path': output_path
            }
            
        except Exception as e:
            raise Exception(f"OCR to text failed: {str(e)}")
