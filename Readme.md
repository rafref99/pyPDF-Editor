# pyPDF Editor

A small Python desktop app for reading and making basic modifications to PDF files.

## Current features

- Open a PDF file
- Preview pages in a scrollable desktop window
- Switch between System, White, and Dark UI themes
- Use toolbar buttons with small function-specific icons
- Browse pages with a thumbnail sidebar
- Navigate to the previous or next page
- Zoom in and out
- Rotate the current page clockwise
- Delete the current page
- Move pages up or down
- Add a free text annotation with configurable text, position, box size, font size, text color, and fill color
- Edit, move, resize, or remove free text annotations on the current page
- Highlight matching text on the current page
- Remove matching highlight annotations from the current page
- Insert an image stamp or signature with configurable position, width, and margin
- Append other PDF files to the current document
- Split a document into one PDF file per page
- Compress PDFs into optimized copies
- Protect PDFs with password encryption
- Unlock password-protected PDFs when the password is known
- Export PDF pages to image files
- Extract embedded images from PDFs
- Convert image files into a PDF
- Add text watermarks to all pages
- Add page numbers to all pages
- Edit basic PDF metadata
- Convert Markdown files to searchable PDFs
- Convert HTML files to searchable PDFs
- Save the modified PDF as a new file

## Quick start

### macOS

Double-click `launch_mac.command`, or run:

```bash
./launch_mac.command
```

If macOS blocks the file because it is not executable yet, run this once:

```bash
chmod +x launch_mac.command
```

### Windows

Double-click `launch_windows.bat`.

The launchers create a local `.venv`, install anything listed in `requirements.txt`, and then start the app.

## Manual setup

Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the app:

```bash
python main.py
```

Run tests:

```bash
pytest
```

## Project structure

- `main.py`: application entry point.
- `ui/main_window.py`: main PySide6 window, toolbar wiring, PDF rendering, and GUI workflows.
- `ui/dialogs.py`: reusable dialogs for metadata, image placement, and text annotations.
- `ui/icons.py`: generated toolbar icons.
- `ui/themes.py`: System, White, and Dark theme palettes/stylesheets.
- `pdf_operations.py`: non-GUI PDF operations and conversions.
- `tests/`: non-GUI operation tests.

## Notes

This first version focuses on practical PDF operations that work reliably with existing PDF files. Direct text editing inside an existing PDF is more complex because PDFs are layout documents, not word-processing documents.

The app currently saves document changes through `Save As` so the original PDF is not overwritten accidentally. Splitting pages writes new files into the folder you choose.

Compress, protect, unlock, export, extract, and image conversion workflows write new files or folders. The loaded PDF is not overwritten unless you explicitly save a copy over an existing path.

Markdown conversion currently supports common document structure: headings, paragraphs, bullet and numbered lists, blockquotes, fenced code blocks, horizontal rules, and simple inline cleanup for links, bold, italic, and code text.

HTML conversion uses PyMuPDF's HTML layout engine and can resolve local relative assets from the HTML file's folder when supported by that engine.

Images are currently embedded into the PDF page content when inserted. Choose their placement and size before adding them; drag-moving already embedded images is planned as a later interactive editing feature.

The theme selector is in the toolbar. System follows the operating system palette, while White and Dark force a specific app theme. Toolbar icons are redrawn for the active theme so they remain visible.
