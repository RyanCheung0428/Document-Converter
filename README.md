# Universal File Format Converter

A powerful, user-friendly desktop application for converting between various file formats including documents (Word, Excel, PDF) and images (PNG, JPG, BMP, TIFF, etc.).

## Features

- **Automatic Format Detection**: No need to manually select the input format - the application automatically detects it!
- **Document Conversions**: 
  - PDF ↔ Word (DOCX)
  - Excel ↔ PDF
  - Word → PDF
- **Image Conversions**: 
  - Between formats: PNG, JPG, JPEG, BMP, TIFF, GIF, WEBP, ICO
  - Images → PDF
  - PDF → Image (first page)
- **Batch Processing**: Convert multiple files at once
- **User-Friendly GUI**: Simple and intuitive interface
- **Standalone EXE**: No Python installation required

## Installation

### From Source

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv .venv
   ```
3. Activate the virtual environment:
   ```bash
   # Windows
   .venv\Scripts\activate
   
   # Linux/Mac
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Run the application:
   ```bash
   python main.py
   ```

### Build EXE

To create a standalone EXE file:

**Windows:**
```bash
build.bat
```

The EXE will be created in the `dist` folder and can be distributed without Python.

**Manual Build:**
```bash
pyinstaller FileConverter.spec --clean
```

## Usage

1. **Launch the Application**
   - Run `main.py` or double-click `FileConverter.exe`

2. **Select Files**
   - Click "Browse Files" to select one or more files
   - The application will automatically detect the file format

3. **Choose Target Format**
   - Select the desired output format from the dropdown
   - Available formats depend on the input file type

4. **Select Output Folder**
   - Choose where to save the converted files
   - Default is the Downloads folder

5. **Convert**
   - Click "Convert Files" to start the conversion
   - Progress will be shown in real-time

## Supported Conversions

### Document Formats
- **PDF to Word**: Converts PDF to editable DOCX
- **Word to PDF**: Converts DOCX/DOC to PDF
- **Excel to PDF**: Converts XLSX/XLS to PDF
- **PDF to Image**: Extracts first page as PNG/JPG

### Image Formats
- Convert between: PNG, JPG, JPEG, BMP, TIFF, GIF, WEBP, ICO
- Batch convert images to PDF
- Automatic transparency handling for JPG conversion

## Requirements

- Python 3.8 or higher (for running from source)
- Windows 10/11 (for EXE file)

## Dependencies

- Pillow: Image processing
- python-docx: Word document handling
- openpyxl: Excel file handling
- PyPDF2: PDF manipulation
- pdf2docx: PDF to Word conversion
- img2pdf: Image to PDF conversion
- reportlab: PDF generation
- python-magic: File type detection
- customtkinter: Modern GUI (optional)

## Notes

### Word to PDF Conversion
- On Windows, Word to PDF conversion works best with Microsoft Word installed
- Without Word, a basic PDF is generated using reportlab

### PDF to Word Conversion
- Conversion quality depends on the PDF structure
- Works best with text-based PDFs
- Scanned PDFs may require OCR (not included)

## Troubleshooting

### Import Errors
If you encounter import errors, ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### PyMuPDF for PDF to Image
For better PDF to image conversion, install PyMuPDF:
```bash
pip install PyMuPDF
```

### Windows Defender / Antivirus
The built EXE might be flagged by antivirus software. This is a false positive common with PyInstaller applications. You can:
- Add an exception in your antivirus
- Build with code signing (requires certificate)

## License

This project is provided as-is for personal and commercial use.

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests.

## Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] More document formats (RTF, ODT, etc.)
- [ ] Video/Audio format support
- [ ] Cloud storage integration
- [ ] Drag and drop interface
- [ ] Custom conversion settings
- [ ] Multi-language support

## Author

Created with ❤️ for universal file format conversion needs.
