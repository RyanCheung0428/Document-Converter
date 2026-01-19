# How to Add a Custom Icon to Your EXE

## Option 1: Use a Pre-made Icon

1. Download or create a `.ico` file (256x256 recommended)
2. Save it in the project root as `icon.ico`
3. The `FileConverter.spec` file is already configured to use it

## Option 2: Create Icon from Image

If you have a PNG/JPG image:

```powershell
# Install pillow if not already installed
pip install pillow

# Convert to ICO
python -c "from PIL import Image; img = Image.open('your_image.png'); img.save('icon.ico', sizes=[(256,256)])"
```

## Free Icon Resources

- https://icons8.com (free icons)
- https://www.flaticon.com (free icons)
- https://fontawesome.com (icon fonts)

Recommended search terms:
- "file converter"
- "document"
- "arrows"
- "exchange"

## After Adding Icon

1. Place `icon.ico` in the project root
2. The build script will automatically use it
3. Run `build.bat` to rebuild the EXE

The spec file already has this line ready:
```python
icon='icon.ico'  # Will be used when icon.ico exists
```

No code changes needed!
