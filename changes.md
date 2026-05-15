# Changes

## 2026-05-15

- Refactored the app into a smaller `main.py`, UI modules, and the existing PDF operations module.
- Added `ui/main_window.py`, `ui/dialogs.py`, `ui/icons.py`, and `ui/themes.py`.
- Added HTML-to-PDF conversion with searchable text output.
- Added a GUI toolbar action for opening HTML files and saving the generated PDF.
- Added test coverage for HTML conversion.
- Added expanded text annotation controls for position, size, font size, text color, and fill color.
- Added an edit text workflow for moving, resizing, changing, or removing current-page free text annotations.
- Added System, White, and Dark UI theme options.
- Made generated toolbar icons redraw with theme-aware colors for contrast.
- Added PDF compression, password protection, and password unlocking workflows.
- Added PDF page export to images, embedded image extraction, and images-to-PDF conversion.
- Added text watermarks and page number insertion.
- Expanded non-GUI tests for the new PDF operations.
- Updated the todo list with remaining screenshot-inspired feature ideas.
- Added small generated icons for every toolbar function.
- Added a remove-highlight workflow for deleting matching highlight annotations from the current page.
- Added configurable image placement and sizing before inserting an image stamp/signature.
- Added Markdown-to-PDF conversion with searchable text output.
- Added a GUI toolbar action for opening Markdown files and saving the generated PDF.
- Added test coverage for Markdown conversion.
- Added a page thumbnail sidebar.
- Added free text annotations, text search highlighting, and image stamp/signature insertion.
- Added PDF merge, per-page split, page reordering, and metadata editing workflows.
- Added a small `pdf_operations.py` module with tests for non-GUI PDF operations.
- Added macOS and Windows launchers that create a local virtual environment, install requirements, and start the app.
- Added `.gitignore` for local Python environment and cache files.
- Created the initial Python desktop app scaffold.
- Added a PySide6 GUI with a toolbar and PDF preview area.
- Added PDF loading and rendering through PyMuPDF.
- Added page navigation, zoom controls, page rotation, page deletion, and `Save As`.
- Added `requirements.txt`, `Readme.md`, and `todo.md`.
