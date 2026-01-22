# Agent Guide for Document-Converter

This repository contains a Flask backend and a vanilla HTML/CSS/JS frontend.
Follow the notes below when building, testing, or changing code.

## Quick orientation
- Entry points: `app.py` (root), `backend/app.py` (Flask app)
- Frontend assets: `frontend/templates/index.html`, `frontend/static/css/style.css`, `frontend/static/js/app.js`
- Config: `backend/config.py`
- Conversion logic: `backend/converters/`, `backend/utils/`

## Build, lint, test
This repo does not define a formal build or lint pipeline.
Use the commands below as the standard execution paths.

### Install dependencies
- `pip install -r requirements.txt`

### Run the web app (development)
- `python app.py`
- `python run_web.py`
- `python start_server.py`
- Windows: `run_web.bat` or `START.bat`

### Tests
- No test runner or test directory is present.
- If you add tests later, use `pytest` and keep them under `tests/`.
- Example single test run (if tests exist): `pytest tests/test_example.py -k "test_name"`

### Lint/format
- No linting or formatting tooling configured.
- Keep formatting consistent with existing files (PEP 8 for Python, 4-space indents).
- When adding new linting, document it here.

## Code style guidelines
Follow existing conventions in each layer. Avoid introducing new patterns
or dependencies unless required for a feature.

### Python (backend)
- Use 4 spaces for indentation; keep line length readable (~88-100 chars).
- Use triple-double-quote docstrings for modules/classes/functions.
- Prefer explicit imports over wildcard imports.
- Import order: standard library, third-party, then local `backend.*`.
- Use `Path` from `pathlib` for filesystem paths when practical.
- Favor explicit error messages and return JSON errors via Flask.
- Keep request handlers thin; delegate heavy logic to `backend/converters/*`.
- Validate inputs early and return `400` for missing/invalid fields.
- Use `secure_filename` for any user-provided file names.
- Keep optional dependencies guarded with try/except (see OCR patterns).
- Prefer returning data from helpers rather than printing inside helpers.

### Flask API patterns
- Use `jsonify({"success": True, ...})` for successful responses.
- Use `jsonify({"success": False, "error": "..."})` for errors.
- Choose appropriate HTTP status codes (400/404/500/503).
- Keep route functions small; prefer helper methods in converters/utils.
- Avoid side effects inside error handlers beyond returning JSON.
- Use `request.get_json()` for JSON payloads; validate data before use.

### Error handling
- Catch exceptions at the API boundary and return JSON errors.
- Raise explicit `ValueError` or `NotImplementedError` for unsupported formats.
- Keep error strings user-friendly; do not leak file system paths.
- For background tasks (cleanup), collect and return error arrays.

### Naming conventions
- Python: `snake_case` for variables/functions, `PascalCase` for classes.
- JavaScript: `camelCase` for variables/functions, `PascalCase` for classes.
- CSS: `kebab-case` for class names; use CSS variables for theme colors.
- Files: use descriptive names matching existing modules.

### Frontend (HTML/CSS/JS)
- HTML uses semantic sections and IDs referenced in JS.
- JS uses `const` and `let` (no `var`).
- Keep state in the top-level `state` object and update through helpers.
- Use Fetch API with JSON bodies for POST endpoints.
- Keep UI state toggles via `style.display` to match current patterns.
- Use template literals for DOM fragments; keep strings readable.
- CSS uses variables under `:root` and `[data-theme="dark"]`.
- Prefer small, reusable classes over inline styles in JS.

### Imports and dependencies
- Do not add new dependencies without updating `requirements.txt`.
- Optional tools (OCR, PyMuPDF) should be imported lazily in try/except.
- Keep module-level imports stable; avoid circular imports.
- Keep standard-library imports grouped at the top of each module.

### Filesystem and sessions
- Uploads live in `uploads/<session_id>/`.
- Outputs live in `outputs/<session_id>/`.
- Always create directories with `exist_ok=True` before writing.
- Use UUIDs for new session IDs.
- Clean up per-session folders after downloads when appropriate.

### Conversion patterns
- Image conversions use Pillow and `img2pdf` for PDF output.
- Document conversions use `pdf2docx`, `docx2pdf`, and `reportlab` fallbacks.
- PDF tools (merge/split) live in `backend/converters/pdf_tools.py`.
- Keep conversion functions pure and return booleans/results, not Flask responses.
- Preserve source files; write outputs to a session folder.

### Configuration
- Config defaults are in `backend/config.py`.
- The Flask app also sets `UPLOAD_FOLDER` and `OUTPUT_FOLDER` directly.
- Use `SECRET_KEY` from environment for production.
- Keep max upload size at 50MB unless product requirements change.

### Logging/printing
- The project uses `print()` in scripts; backend does not use logging.
- If adding logging, keep it minimal and avoid noisy logs in request paths.

## Cursor/Copilot rules
- No Cursor rules found in `.cursor/rules/` or `.cursorrules`.
- No Copilot instructions found in `.github/copilot-instructions.md`.

## Suggested workflow for agents
1. Read `README.md` for app usage and supported formats.
2. Inspect `backend/app.py` for route behavior and response shapes.
3. Update converters/utilities first, then wire routes or UI changes.
4. Run the app locally to verify behavior.

## Common endpoints
- `GET /` main UI
- `GET /api/formats` supported formats
- `POST /api/detect` upload + detect
- `POST /api/convert` convert a single file
- `POST /api/compress` image compression
- `POST /api/pdf/merge` merge PDFs
- `POST /api/pdf/split` split PDF
- `GET /api/pdf/info/<session_id>/<filename>` get PDF metadata
- `POST /api/pdf/to-images` PDF pages to images
- `POST /api/ocr` OCR extraction (optional deps)
- `GET /api/ocr/languages` list OCR languages

## Notes for adding tests
- Prefer `pytest` with fixtures for sample files.
- Keep sample inputs in `tests/fixtures/` and clean outputs after runs.
- Avoid large binaries in git; small sample files only.
- Tests that touch filesystem should use temporary directories.

## Repository conventions
- Keep user-facing strings in Chinese unless updating translations globally.
- Avoid introducing framework tooling; stick to vanilla JS/CSS.
- Keep CSS themes aligned with existing variable palette.
