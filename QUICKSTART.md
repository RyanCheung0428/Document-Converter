# Quick Start Guide - Universal File Converter

## Getting Started in 3 Easy Steps

### Step 1: Install Dependencies

Open PowerShell in this directory and run:

```powershell
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Install all required packages
pip install -r requirements.txt
```

### Step 2: Run the Application

```powershell
python main.py
```

### Step 3: Build EXE (Optional)

To create a standalone executable:

```powershell
.\build.bat
```

The EXE will be in the `dist` folder: `dist\FileConverter.exe`

## First Time Usage

1. **Launch** the application
2. **Click** "Browse Files" to select files
3. **Select** target format from dropdown
4. **Choose** output folder (optional)
5. **Click** "Convert Files"

## Conversion Examples

### Convert Images to PDF
- Select multiple PNG/JPG files
- Choose "PDF" as target format
- Click Convert

### Convert Word to PDF
- Select DOCX file
- Choose "PDF" as target format
- Click Convert

### Convert PDF to Images
- Select PDF file
- Choose "PNG" or "JPG" as target format
- Click Convert (converts first page)

### Convert Between Image Formats
- Select image files (any format)
- Choose target format (PNG, JPG, BMP, etc.)
- Click Convert

## Tips

- You can select multiple files at once for batch conversion
- Format detection is automatic - no need to specify input format
- Output files are saved with the same name + new extension
- Failed conversions will show error messages

## Common Issues

**"Module not found" errors:**
```powershell
pip install -r requirements.txt
```

**Word to PDF not working:**
- Install Microsoft Word, or
- Use the basic PDF generation (automatic fallback)

**PDF to Image requires PyMuPDF:**
```powershell
pip install PyMuPDF
```

## Need Help?

Check the full README.md for detailed documentation and troubleshooting.
