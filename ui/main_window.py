from __future__ import annotations

from pathlib import Path

import fitz
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import (
    QAction,
    QColor,
    QIcon,
    QImage,
    QKeySequence,
    QPalette,
    QPixmap,
)
from PySide6.QtWidgets import (
    QApplication,
    QDialog,
    QDockWidget,
    QFileDialog,
    QComboBox,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QScrollArea,
    QStatusBar,
    QToolBar,
)

from pdf_operations import (
    add_page_numbers,
    add_text_watermark,
    compress_pdf,
    convert_html_to_pdf,
    convert_markdown_to_pdf,
    export_pdf_pages_to_images,
    extract_pdf_images,
    images_to_pdf,
    merge_pdfs,
    move_page,
    protect_pdf,
    split_pages,
    unlock_pdf,
    update_metadata,
)

from ui.dialogs import (
    ImagePlacementDialog,
    MetadataDialog,
    TextAnnotationDialog,
    TextAnnotationManagerDialog,
)
from ui.icons import toolbar_icon
from ui.themes import dark_palette, dark_stylesheet, white_palette, white_stylesheet


class PdfEditorWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()

        self.setWindowTitle("pyPDF Editor")
        self.resize(1100, 800)

        self.document: fitz.Document | None = None
        self.current_page = 0
        self.zoom = 1.25
        self.current_file: Path | None = None
        self.has_unsaved_changes = False
        self.theme_mode = "System"
        self.system_palette = QApplication.palette()
        self.toolbar_icon_actions: dict[QAction, str] = {}

        self.page_label = QLabel("Open a PDF to get started")
        self.page_label.setAlignment(Qt.AlignCenter)
        self.page_label.setMinimumSize(600, 400)

        self.scroll_area = QScrollArea()
        self.scroll_area.setAlignment(Qt.AlignCenter)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setWidget(self.page_label)
        self.setCentralWidget(self.scroll_area)

        self.thumbnail_list = QListWidget()
        self.thumbnail_list.setIconSize(QSize(120, 160))
        self.thumbnail_list.setUniformItemSizes(False)
        self.thumbnail_list.currentRowChanged.connect(self.go_to_thumbnail_page)

        thumbnail_dock = QDockWidget("Pages", self)
        thumbnail_dock.setObjectName("pagesDock")
        thumbnail_dock.setWidget(self.thumbnail_list)
        self.addDockWidget(Qt.LeftDockWidgetArea, thumbnail_dock)

        self.setStatusBar(QStatusBar())
        self._build_toolbar()
        self.apply_theme(self.theme_mode)
        self._update_actions()

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("PDF Tools")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        self.addToolBar(toolbar)

        self.open_action = QAction("Open", self)
        self.open_action.setIcon(toolbar_icon("open"))
        self.open_action.setShortcut(QKeySequence.Open)
        self.open_action.triggered.connect(self.open_pdf)
        toolbar.addAction(self.open_action)

        self.save_as_action = QAction("Save As", self)
        self.save_as_action.setIcon(toolbar_icon("save"))
        self.save_as_action.setShortcut(QKeySequence.SaveAs)
        self.save_as_action.triggered.connect(self.save_pdf_as)
        toolbar.addAction(self.save_as_action)

        self.markdown_action = QAction("Markdown to PDF", self)
        self.markdown_action.setIcon(toolbar_icon("markdown"))
        self.markdown_action.triggered.connect(self.convert_markdown_file)
        toolbar.addAction(self.markdown_action)

        self.html_action = QAction("HTML to PDF", self)
        self.html_action.setIcon(toolbar_icon("html"))
        self.html_action.triggered.connect(self.convert_html_file)
        toolbar.addAction(self.html_action)

        self.images_to_pdf_action = QAction("Images to PDF", self)
        self.images_to_pdf_action.setIcon(toolbar_icon("images_to_pdf"))
        self.images_to_pdf_action.triggered.connect(self.convert_images_to_pdf)
        toolbar.addAction(self.images_to_pdf_action)

        self.unlock_action = QAction("Unlock PDF", self)
        self.unlock_action.setIcon(toolbar_icon("unlock"))
        self.unlock_action.triggered.connect(self.unlock_pdf_file)
        toolbar.addAction(self.unlock_action)

        toolbar.addSeparator()

        self.previous_action = QAction("Previous", self)
        self.previous_action.setIcon(toolbar_icon("previous"))
        self.previous_action.setShortcut(QKeySequence.MoveToPreviousPage)
        self.previous_action.triggered.connect(self.previous_page)
        toolbar.addAction(self.previous_action)

        self.next_action = QAction("Next", self)
        self.next_action.setIcon(toolbar_icon("next"))
        self.next_action.setShortcut(QKeySequence.MoveToNextPage)
        self.next_action.triggered.connect(self.next_page)
        toolbar.addAction(self.next_action)

        toolbar.addSeparator()

        self.zoom_out_action = QAction("Zoom Out", self)
        self.zoom_out_action.setIcon(toolbar_icon("zoom_out"))
        self.zoom_out_action.setShortcut(QKeySequence.ZoomOut)
        self.zoom_out_action.triggered.connect(self.zoom_out)
        toolbar.addAction(self.zoom_out_action)

        self.zoom_in_action = QAction("Zoom In", self)
        self.zoom_in_action.setIcon(toolbar_icon("zoom_in"))
        self.zoom_in_action.setShortcut(QKeySequence.ZoomIn)
        self.zoom_in_action.triggered.connect(self.zoom_in)
        toolbar.addAction(self.zoom_in_action)

        toolbar.addSeparator()

        self.rotate_action = QAction("Rotate Right", self)
        self.rotate_action.setIcon(toolbar_icon("rotate"))
        self.rotate_action.triggered.connect(self.rotate_page_right)
        toolbar.addAction(self.rotate_action)

        self.delete_action = QAction("Delete Page", self)
        self.delete_action.setIcon(toolbar_icon("delete"))
        self.delete_action.triggered.connect(self.delete_current_page)
        toolbar.addAction(self.delete_action)

        self.move_up_action = QAction("Move Up", self)
        self.move_up_action.setIcon(toolbar_icon("move_up"))
        self.move_up_action.triggered.connect(self.move_page_up)
        toolbar.addAction(self.move_up_action)

        self.move_down_action = QAction("Move Down", self)
        self.move_down_action.setIcon(toolbar_icon("move_down"))
        self.move_down_action.triggered.connect(self.move_page_down)
        toolbar.addAction(self.move_down_action)

        toolbar.addSeparator()

        self.text_action = QAction("Add Text", self)
        self.text_action.setIcon(toolbar_icon("text"))
        self.text_action.triggered.connect(self.add_text_annotation)
        toolbar.addAction(self.text_action)

        self.edit_text_action = QAction("Edit Text", self)
        self.edit_text_action.setIcon(toolbar_icon("edit_text"))
        self.edit_text_action.triggered.connect(self.edit_text_annotations)
        toolbar.addAction(self.edit_text_action)

        self.highlight_action = QAction("Highlight Text", self)
        self.highlight_action.setIcon(toolbar_icon("highlight"))
        self.highlight_action.triggered.connect(self.highlight_text)
        toolbar.addAction(self.highlight_action)

        self.remove_highlight_action = QAction("Remove Highlight", self)
        self.remove_highlight_action.setIcon(toolbar_icon("remove_highlight"))
        self.remove_highlight_action.triggered.connect(self.remove_highlight)
        toolbar.addAction(self.remove_highlight_action)

        self.image_action = QAction("Add Image", self)
        self.image_action.setIcon(toolbar_icon("image"))
        self.image_action.triggered.connect(self.add_image_stamp)
        toolbar.addAction(self.image_action)

        toolbar.addSeparator()

        self.merge_action = QAction("Merge PDFs", self)
        self.merge_action.setIcon(toolbar_icon("merge"))
        self.merge_action.triggered.connect(self.merge_pdf_files)
        toolbar.addAction(self.merge_action)

        self.split_action = QAction("Split Pages", self)
        self.split_action.setIcon(toolbar_icon("split"))
        self.split_action.triggered.connect(self.split_pdf_pages)
        toolbar.addAction(self.split_action)

        self.metadata_action = QAction("Metadata", self)
        self.metadata_action.setIcon(toolbar_icon("metadata"))
        self.metadata_action.triggered.connect(self.edit_metadata)
        toolbar.addAction(self.metadata_action)

        toolbar.addSeparator()

        self.compress_action = QAction("Compress", self)
        self.compress_action.setIcon(toolbar_icon("compress"))
        self.compress_action.triggered.connect(self.compress_current_pdf)
        toolbar.addAction(self.compress_action)

        self.protect_action = QAction("Protect", self)
        self.protect_action.setIcon(toolbar_icon("protect"))
        self.protect_action.triggered.connect(self.protect_current_pdf)
        toolbar.addAction(self.protect_action)

        self.pdf_to_images_action = QAction("PDF to Images", self)
        self.pdf_to_images_action.setIcon(toolbar_icon("pdf_to_images"))
        self.pdf_to_images_action.triggered.connect(self.export_current_pdf_to_images)
        toolbar.addAction(self.pdf_to_images_action)

        self.extract_images_action = QAction("Extract Images", self)
        self.extract_images_action.setIcon(toolbar_icon("extract_images"))
        self.extract_images_action.triggered.connect(self.extract_current_pdf_images)
        toolbar.addAction(self.extract_images_action)

        self.watermark_action = QAction("Watermark", self)
        self.watermark_action.setIcon(toolbar_icon("watermark"))
        self.watermark_action.triggered.connect(self.add_watermark_to_pdf)
        toolbar.addAction(self.watermark_action)

        self.page_numbers_action = QAction("Page Numbers", self)
        self.page_numbers_action.setIcon(toolbar_icon("page_numbers"))
        self.page_numbers_action.triggered.connect(self.add_numbers_to_pdf)
        toolbar.addAction(self.page_numbers_action)

        toolbar.addSeparator()

        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["System", "White", "Dark"])
        self.theme_combo.setCurrentText(self.theme_mode)
        self.theme_combo.setToolTip("Theme")
        self.theme_combo.currentTextChanged.connect(self.apply_theme)
        toolbar.addWidget(self.theme_combo)

        self.toolbar_icon_actions = {
            self.open_action: "open",
            self.save_as_action: "save",
            self.markdown_action: "markdown",
            self.html_action: "html",
            self.images_to_pdf_action: "images_to_pdf",
            self.unlock_action: "unlock",
            self.previous_action: "previous",
            self.next_action: "next",
            self.zoom_out_action: "zoom_out",
            self.zoom_in_action: "zoom_in",
            self.rotate_action: "rotate",
            self.delete_action: "delete",
            self.move_up_action: "move_up",
            self.move_down_action: "move_down",
            self.text_action: "text",
            self.edit_text_action: "edit_text",
            self.highlight_action: "highlight",
            self.remove_highlight_action: "remove_highlight",
            self.image_action: "image",
            self.merge_action: "merge",
            self.split_action: "split",
            self.metadata_action: "metadata",
            self.compress_action: "compress",
            self.protect_action: "protect",
            self.pdf_to_images_action: "pdf_to_images",
            self.extract_images_action: "extract_images",
            self.watermark_action: "watermark",
            self.page_numbers_action: "page_numbers",
        }

    def apply_theme(self, theme_mode: str) -> None:
        self.theme_mode = theme_mode
        app = QApplication.instance()
        if app is None:
            return

        if theme_mode == "Dark":
            app.setPalette(dark_palette())
            app.setStyleSheet(dark_stylesheet())
        elif theme_mode == "White":
            app.setPalette(white_palette())
            app.setStyleSheet(white_stylesheet())
        else:
            app.setPalette(self.system_palette)
            app.setStyleSheet("")

        self._refresh_toolbar_icons()

    def _refresh_toolbar_icons(self) -> None:
        dark_theme = self._active_theme_is_dark()
        for action, icon_name in self.toolbar_icon_actions.items():
            action.setIcon(toolbar_icon(icon_name, dark_theme))

    def _active_theme_is_dark(self) -> bool:
        app = QApplication.instance()
        palette = app.palette() if app is not None else self.palette()
        return palette.color(QPalette.Window).lightness() < 128

    def open_pdf(self) -> None:
        if not self._confirm_discard_changes():
            return

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            str(Path.home()),
            "PDF Files (*.pdf)",
        )
        if not file_name:
            return

        try:
            document = fitz.open(file_name)
            if document.needs_pass:
                password, accepted = QInputDialog.getText(
                    self,
                    "PDF password",
                    "Password:",
                    QLineEdit.Password,
                )
                if not accepted or not document.authenticate(password):
                    document.close()
                    QMessageBox.warning(self, "Could not open PDF", "Incorrect or missing password.")
                    return
        except Exception as exc:
            QMessageBox.critical(self, "Could not open PDF", str(exc))
            return

        if self.document is not None:
            self.document.close()

        self.document = document
        self.current_file = Path(file_name)
        self.current_page = 0
        self.has_unsaved_changes = False
        self.refresh_thumbnails()
        self.render_page()
        self._update_actions()

    def save_pdf_as(self) -> None:
        if self.document is None:
            return

        suggested_name = "edited.pdf"
        if self.current_file is not None:
            suggested_name = f"{self.current_file.stem}_edited.pdf"

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF As",
            str((self.current_file or Path.home()).with_name(suggested_name)),
            "PDF Files (*.pdf)",
        )
        if not file_name:
            return

        output_path = Path(file_name)
        if output_path.suffix.lower() != ".pdf":
            output_path = output_path.with_suffix(".pdf")

        try:
            self.document.save(output_path, garbage=4, deflate=True)
        except Exception as exc:
            QMessageBox.critical(self, "Could not save PDF", str(exc))
            return

        self.current_file = output_path
        self.has_unsaved_changes = False
        self.statusBar().showMessage(f"Saved {output_path.name}", 5000)
        self._update_actions()

    def convert_markdown_file(self) -> None:
        if not self._confirm_discard_changes():
            return

        markdown_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open Markdown",
            str(Path.home()),
            "Markdown Files (*.md *.markdown *.txt)",
        )
        if not markdown_file:
            return

        markdown_path = Path(markdown_file)
        suggested_path = markdown_path.with_suffix(".pdf")
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            str(suggested_path),
            "PDF Files (*.pdf)",
        )
        if not output_file:
            return

        try:
            output_path = convert_markdown_to_pdf(markdown_path, Path(output_file))
            document = fitz.open(output_path)
        except Exception as exc:
            QMessageBox.critical(self, "Could not convert Markdown", str(exc))
            return

        if self.document is not None:
            self.document.close()

        self.document = document
        self.current_file = output_path
        self.current_page = 0
        self.has_unsaved_changes = False
        self.refresh_thumbnails()
        self.render_page()
        self._update_actions()
        self.statusBar().showMessage(f"Converted {markdown_path.name} to {output_path.name}", 5000)

    def convert_html_file(self) -> None:
        if not self._confirm_discard_changes():
            return

        html_file, _ = QFileDialog.getOpenFileName(
            self,
            "Open HTML",
            str(Path.home()),
            "HTML Files (*.html *.htm)",
        )
        if not html_file:
            return

        html_path = Path(html_file)
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            str(html_path.with_suffix(".pdf")),
            "PDF Files (*.pdf)",
        )
        if not output_file:
            return

        try:
            output_path = convert_html_to_pdf(html_path, Path(output_file))
            document = fitz.open(output_path)
        except Exception as exc:
            QMessageBox.critical(self, "Could not convert HTML", str(exc))
            return

        if self.document is not None:
            self.document.close()

        self.document = document
        self.current_file = output_path
        self.current_page = 0
        self.has_unsaved_changes = False
        self.refresh_thumbnails()
        self.render_page()
        self._update_actions()
        self.statusBar().showMessage(f"Converted {html_path.name} to {output_path.name}", 5000)

    def convert_images_to_pdf(self) -> None:
        if not self._confirm_discard_changes():
            return

        image_files, _ = QFileDialog.getOpenFileNames(
            self,
            "Choose images",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp *.tiff)",
        )
        if not image_files:
            return

        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save PDF",
            str(Path(image_files[0]).with_suffix(".pdf")),
            "PDF Files (*.pdf)",
        )
        if not output_file:
            return

        try:
            output_path = images_to_pdf([Path(file_name) for file_name in image_files], Path(output_file))
            document = fitz.open(output_path)
        except Exception as exc:
            QMessageBox.critical(self, "Could not convert images", str(exc))
            return

        if self.document is not None:
            self.document.close()

        self.document = document
        self.current_file = output_path
        self.current_page = 0
        self.has_unsaved_changes = False
        self.refresh_thumbnails()
        self.render_page()
        self._update_actions()
        self.statusBar().showMessage(f"Created {output_path.name} from {len(image_files)} image(s)", 5000)

    def unlock_pdf_file(self) -> None:
        input_file, _ = QFileDialog.getOpenFileName(
            self,
            "Choose protected PDF",
            str(Path.home()),
            "PDF Files (*.pdf)",
        )
        if not input_file:
            return

        password, accepted = QInputDialog.getText(
            self,
            "Unlock PDF",
            "Password:",
            QLineEdit.Password,
        )
        if not accepted:
            return

        input_path = Path(input_file)
        output_file, _ = QFileDialog.getSaveFileName(
            self,
            "Save unlocked PDF",
            str(input_path.with_name(f"{input_path.stem}_unlocked.pdf")),
            "PDF Files (*.pdf)",
        )
        if not output_file:
            return

        try:
            output_path = unlock_pdf(input_path, Path(output_file), password)
        except Exception as exc:
            QMessageBox.critical(self, "Could not unlock PDF", str(exc))
            return

        QMessageBox.information(self, "Unlock complete", f"Saved {output_path.name}.")

    def previous_page(self) -> None:
        if self.document is None or self.current_page <= 0:
            return

        self.current_page -= 1
        self.render_page()
        self._update_actions()

    def next_page(self) -> None:
        if self.document is None or self.current_page >= self.document.page_count - 1:
            return

        self.current_page += 1
        self.render_page()
        self._update_actions()

    def zoom_in(self) -> None:
        self.zoom = min(self.zoom + 0.25, 5.0)
        self.render_page()

    def zoom_out(self) -> None:
        self.zoom = max(self.zoom - 0.25, 0.25)
        self.render_page()

    def rotate_page_right(self) -> None:
        if self.document is None:
            return

        page = self.document[self.current_page]
        page.set_rotation((page.rotation + 90) % 360)
        self._mark_document_changed()

    def delete_current_page(self) -> None:
        if self.document is None:
            return

        if self.document.page_count == 1:
            QMessageBox.warning(self, "Cannot delete page", "A PDF must contain at least one page.")
            return

        reply = QMessageBox.question(
            self,
            "Delete page",
            f"Delete page {self.current_page + 1}?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        if reply != QMessageBox.Yes:
            return

        self.document.delete_page(self.current_page)
        self.current_page = min(self.current_page, self.document.page_count - 1)
        self.has_unsaved_changes = True
        self.refresh_thumbnails()
        self.render_page()
        self._update_actions()

    def move_page_up(self) -> None:
        self._move_current_page(-1)

    def move_page_down(self) -> None:
        self._move_current_page(1)

    def _move_current_page(self, offset: int) -> None:
        if self.document is None:
            return

        new_index = move_page(self.document, self.current_page, offset)
        if new_index == self.current_page:
            return

        self.current_page = new_index
        self.has_unsaved_changes = True
        self.refresh_thumbnails()
        self.render_page()
        self._update_actions()

    def add_text_annotation(self) -> None:
        if self.document is None:
            return

        page = self.document[self.current_page]
        dialog = TextAnnotationDialog(page.rect, self)
        if dialog.exec() != QDialog.Accepted:
            return

        values = dialog.values()
        if not values["text"]:
            return

        self._add_free_text_annotation(page, values)
        self._mark_document_changed()

    def edit_text_annotations(self) -> None:
        if self.document is None:
            return

        page = self.document[self.current_page]
        annotations = [
            annotation
            for annotation in list(page.annots() or [])
            if annotation.type[0] == fitz.PDF_ANNOT_FREE_TEXT
        ]
        if not annotations:
            QMessageBox.information(self, "No text annotations", "No editable text annotations were found on the current page.")
            return

        dialog = TextAnnotationManagerDialog(page, self)
        if dialog.exec() != QDialog.Accepted or dialog.selected_index is None:
            return

        annotations = [
            annotation
            for annotation in list(page.annots() or [])
            if annotation.type[0] == fitz.PDF_ANNOT_FREE_TEXT
        ]
        if dialog.selected_index >= len(annotations):
            QMessageBox.warning(self, "Annotation changed", "The selected annotation could not be found.")
            return

        annotation = annotations[dialog.selected_index]
        if dialog.result_action == "delete":
            page.delete_annot(annotation)
            self._mark_document_changed()
            return

        if dialog.result_action == "edit" and dialog.annotation_values is not None:
            page.delete_annot(annotation)
            self._add_free_text_annotation(page, dialog.annotation_values)
            self._mark_document_changed()

    def _add_free_text_annotation(self, page: fitz.Page, values: dict) -> None:
        annotation = page.add_freetext_annot(
            values["rect"],
            values["text"],
            fontsize=values["font_size"],
            fontname="helv",
            text_color=self._qcolor_to_pdf_rgb(values["text_color"]),
            fill_color=self._qcolor_to_pdf_rgb(values["fill_color"]),
        )
        annotation.update()

    def _qcolor_to_pdf_rgb(self, color: QColor) -> tuple[float, float, float]:
        return (color.redF(), color.greenF(), color.blueF())

    def highlight_text(self) -> None:
        if self.document is None:
            return

        search_text, accepted = QInputDialog.getText(
            self,
            "Highlight text",
            "Text to find on current page:",
        )
        if not accepted or not search_text.strip():
            return

        page = self.document[self.current_page]
        matches = page.search_for(search_text.strip())
        if not matches:
            QMessageBox.information(self, "No matches", "No matching text was found on the current page.")
            return

        for match in matches:
            annotation = page.add_highlight_annot(match)
            annotation.update()

        self._mark_document_changed()
        self.statusBar().showMessage(f"Highlighted {len(matches)} match(es)", 5000)

    def remove_highlight(self) -> None:
        if self.document is None:
            return

        search_text, accepted = QInputDialog.getText(
            self,
            "Remove highlight",
            "Highlighted text to remove on current page:",
        )
        if not accepted or not search_text.strip():
            return

        page = self.document[self.current_page]
        matches = page.search_for(search_text.strip())
        if not matches:
            QMessageBox.information(self, "No matches", "No matching text was found on the current page.")
            return

        removed_count = 0
        for annotation in list(page.annots() or []):
            if annotation.type[0] != fitz.PDF_ANNOT_HIGHLIGHT:
                continue

            if any(annotation.rect.intersects(match) for match in matches):
                page.delete_annot(annotation)
                removed_count += 1

        if removed_count == 0:
            QMessageBox.information(self, "No highlights", "No matching highlight annotations were found.")
            return

        self._mark_document_changed()
        self.statusBar().showMessage(f"Removed {removed_count} highlight(s)", 5000)

    def add_image_stamp(self) -> None:
        if self.document is None:
            return

        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "Choose image",
            str(Path.home()),
            "Images (*.png *.jpg *.jpeg *.bmp)",
        )
        if not file_name:
            return

        page = self.document[self.current_page]
        page_rect = page.rect

        try:
            source_pixmap = fitz.Pixmap(file_name)
        except Exception as exc:
            QMessageBox.critical(self, "Could not read image", str(exc))
            return

        placement_dialog = ImagePlacementDialog(self)
        if placement_dialog.exec() != QDialog.Accepted:
            return

        position, width_percent, margin = placement_dialog.placement()
        stamp_width = page_rect.width * (width_percent / 100)
        image_ratio = source_pixmap.height / source_pixmap.width
        source_pixmap = None
        stamp_height = stamp_width * image_ratio
        stamp_rect = self._image_rect_for_position(page_rect, stamp_width, stamp_height, margin, position)

        try:
            page.insert_image(stamp_rect, filename=file_name, keep_proportion=True)
        except Exception as exc:
            QMessageBox.critical(self, "Could not add image", str(exc))
            return

        self._mark_document_changed()

    def _image_rect_for_position(
        self,
        page_rect: fitz.Rect,
        stamp_width: float,
        stamp_height: float,
        margin: int,
        position: str,
    ) -> fitz.Rect:
        max_width = max(page_rect.width - (margin * 2), 1)
        max_height = max(page_rect.height - (margin * 2), 1)
        scale = min(max_width / stamp_width, max_height / stamp_height, 1)
        stamp_width *= scale
        stamp_height *= scale

        left = {
            "Top left": margin,
            "Top center": (page_rect.width - stamp_width) / 2,
            "Top right": page_rect.width - stamp_width - margin,
            "Center": (page_rect.width - stamp_width) / 2,
            "Bottom left": margin,
            "Bottom center": (page_rect.width - stamp_width) / 2,
            "Bottom right": page_rect.width - stamp_width - margin,
        }[position]
        top = {
            "Top left": margin,
            "Top center": margin,
            "Top right": margin,
            "Center": (page_rect.height - stamp_height) / 2,
            "Bottom left": page_rect.height - stamp_height - margin,
            "Bottom center": page_rect.height - stamp_height - margin,
            "Bottom right": page_rect.height - stamp_height - margin,
        }[position]

        return fitz.Rect(left, top, left + stamp_width, top + stamp_height)

    def merge_pdf_files(self) -> None:
        if self.document is None:
            return

        file_names, _ = QFileDialog.getOpenFileNames(
            self,
            "Choose PDFs to append",
            str(Path.home()),
            "PDF Files (*.pdf)",
        )
        if not file_names:
            return

        try:
            merge_pdfs(self.document, [Path(file_name) for file_name in file_names])
        except Exception as exc:
            QMessageBox.critical(self, "Could not merge PDFs", str(exc))
            return

        self.has_unsaved_changes = True
        self.refresh_thumbnails()
        self.render_page()
        self._update_actions()
        self.statusBar().showMessage(f"Appended {len(file_names)} PDF file(s)", 5000)

    def split_pdf_pages(self) -> None:
        if self.document is None:
            return

        output_dir = QFileDialog.getExistingDirectory(
            self,
            "Choose output folder",
            str(Path.home()),
        )
        if not output_dir:
            return

        base_name = self.current_file.stem if self.current_file else "document"
        try:
            written_paths = split_pages(self.document, Path(output_dir), base_name)
        except Exception as exc:
            QMessageBox.critical(self, "Could not split PDF", str(exc))
            return

        QMessageBox.information(
            self,
            "Split complete",
            f"Saved {len(written_paths)} page file(s) to {output_dir}.",
        )

    def edit_metadata(self) -> None:
        if self.document is None:
            return

        dialog = MetadataDialog(self.document.metadata or {}, self)
        if dialog.exec() != QDialog.Accepted:
            return

        update_metadata(self.document, dialog.metadata())
        self.has_unsaved_changes = True
        self.render_page()
        self._update_actions()

    def compress_current_pdf(self) -> None:
        if self.document is None:
            return

        output_path = self._ask_pdf_output_path("Save compressed PDF", "compressed")
        if output_path is None:
            return

        try:
            written_path = compress_pdf(self.document, output_path)
        except Exception as exc:
            QMessageBox.critical(self, "Could not compress PDF", str(exc))
            return

        QMessageBox.information(self, "Compression complete", f"Saved {written_path.name}.")

    def protect_current_pdf(self) -> None:
        if self.document is None:
            return

        password, accepted = QInputDialog.getText(
            self,
            "Protect PDF",
            "Password:",
            QLineEdit.Password,
        )
        if not accepted or not password:
            return

        confirm_password, accepted = QInputDialog.getText(
            self,
            "Protect PDF",
            "Confirm password:",
            QLineEdit.Password,
        )
        if not accepted:
            return

        if password != confirm_password:
            QMessageBox.warning(self, "Password mismatch", "The passwords did not match.")
            return

        output_path = self._ask_pdf_output_path("Save protected PDF", "protected")
        if output_path is None:
            return

        try:
            written_path = protect_pdf(self.document, output_path, password)
        except Exception as exc:
            QMessageBox.critical(self, "Could not protect PDF", str(exc))
            return

        QMessageBox.information(self, "Protection complete", f"Saved {written_path.name}.")

    def export_current_pdf_to_images(self) -> None:
        if self.document is None:
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Choose output folder", str(Path.home()))
        if not output_dir:
            return

        base_name = self.current_file.stem if self.current_file else "document"
        try:
            written_paths = export_pdf_pages_to_images(self.document, Path(output_dir), base_name)
        except Exception as exc:
            QMessageBox.critical(self, "Could not export pages", str(exc))
            return

        QMessageBox.information(self, "Export complete", f"Saved {len(written_paths)} image file(s).")

    def extract_current_pdf_images(self) -> None:
        if self.document is None:
            return

        output_dir = QFileDialog.getExistingDirectory(self, "Choose output folder", str(Path.home()))
        if not output_dir:
            return

        base_name = self.current_file.stem if self.current_file else "document"
        try:
            written_paths = extract_pdf_images(self.document, Path(output_dir), base_name)
        except Exception as exc:
            QMessageBox.critical(self, "Could not extract images", str(exc))
            return

        QMessageBox.information(self, "Extraction complete", f"Saved {len(written_paths)} image file(s).")

    def add_watermark_to_pdf(self) -> None:
        if self.document is None:
            return

        text, accepted = QInputDialog.getText(self, "Add watermark", "Watermark text:")
        if not accepted or not text.strip():
            return

        add_text_watermark(self.document, text.strip())
        self._mark_document_changed()

    def add_numbers_to_pdf(self) -> None:
        if self.document is None:
            return

        start_number, accepted = QInputDialog.getInt(
            self,
            "Add page numbers",
            "Start number:",
            1,
            1,
            99999,
        )
        if not accepted:
            return

        add_page_numbers(self.document, start_number)
        self._mark_document_changed()

    def _ask_pdf_output_path(self, title: str, suffix: str) -> Path | None:
        if self.current_file is not None:
            suggested_path = self.current_file.with_name(f"{self.current_file.stem}_{suffix}.pdf")
        else:
            suggested_path = Path.home() / f"document_{suffix}.pdf"

        file_name, _ = QFileDialog.getSaveFileName(self, title, str(suggested_path), "PDF Files (*.pdf)")
        if not file_name:
            return None

        return Path(file_name).with_suffix(".pdf")

    def go_to_thumbnail_page(self, row: int) -> None:
        if self.document is None or row < 0 or row >= self.document.page_count:
            return

        if row == self.current_page:
            return

        self.current_page = row
        self.render_page()
        self._update_actions()

    def refresh_thumbnails(self) -> None:
        self.thumbnail_list.blockSignals(True)
        self.thumbnail_list.clear()

        if self.document is None:
            self.thumbnail_list.blockSignals(False)
            return

        for page_index in range(self.document.page_count):
            page = self.document[page_index]
            pixmap = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2), alpha=False)
            image = QImage(
                pixmap.samples,
                pixmap.width,
                pixmap.height,
                pixmap.stride,
                QImage.Format_RGB888,
            ).copy()
            item = QListWidgetItem(QIcon(QPixmap.fromImage(image)), f"Page {page_index + 1}")
            item.setSizeHint(QSize(150, 190))
            self.thumbnail_list.addItem(item)

        self.thumbnail_list.setCurrentRow(self.current_page)
        self.thumbnail_list.blockSignals(False)

    def _mark_document_changed(self) -> None:
        self.has_unsaved_changes = True
        self.refresh_thumbnails()
        self.render_page()
        self._update_actions()

    def render_page(self) -> None:
        if self.document is None:
            self.page_label.setText("Open a PDF to get started")
            self.statusBar().clearMessage()
            return

        page = self.document[self.current_page]
        matrix = fitz.Matrix(self.zoom, self.zoom)
        pixmap = page.get_pixmap(matrix=matrix, alpha=False)
        image = QImage(
            pixmap.samples,
            pixmap.width,
            pixmap.height,
            pixmap.stride,
            QImage.Format_RGB888,
        ).copy()

        self.page_label.setPixmap(QPixmap.fromImage(image))
        self.page_label.adjustSize()
        self.thumbnail_list.blockSignals(True)
        self.thumbnail_list.setCurrentRow(self.current_page)
        self.thumbnail_list.blockSignals(False)

        file_name = self.current_file.name if self.current_file else "Untitled"
        change_marker = " *" if self.has_unsaved_changes else ""
        self.statusBar().showMessage(
            f"{file_name}{change_marker} | Page {self.current_page + 1} of "
            f"{self.document.page_count} | Zoom {int(self.zoom * 100)}%"
        )

    def _update_actions(self) -> None:
        has_document = self.document is not None
        has_previous = has_document and self.current_page > 0
        has_next = has_document and self.current_page < self.document.page_count - 1

        self.save_as_action.setEnabled(has_document)
        self.markdown_action.setEnabled(True)
        self.html_action.setEnabled(True)
        self.images_to_pdf_action.setEnabled(True)
        self.unlock_action.setEnabled(True)
        self.previous_action.setEnabled(has_previous)
        self.next_action.setEnabled(has_next)
        self.zoom_out_action.setEnabled(has_document)
        self.zoom_in_action.setEnabled(has_document)
        self.rotate_action.setEnabled(has_document)
        self.delete_action.setEnabled(has_document)
        self.move_up_action.setEnabled(has_previous)
        self.move_down_action.setEnabled(has_next)
        self.text_action.setEnabled(has_document)
        self.edit_text_action.setEnabled(has_document)
        self.highlight_action.setEnabled(has_document)
        self.remove_highlight_action.setEnabled(has_document)
        self.image_action.setEnabled(has_document)
        self.merge_action.setEnabled(has_document)
        self.split_action.setEnabled(has_document)
        self.metadata_action.setEnabled(has_document)
        self.compress_action.setEnabled(has_document)
        self.protect_action.setEnabled(has_document)
        self.pdf_to_images_action.setEnabled(has_document)
        self.extract_images_action.setEnabled(has_document)
        self.watermark_action.setEnabled(has_document)
        self.page_numbers_action.setEnabled(has_document)

    def _confirm_discard_changes(self) -> bool:
        if not self.has_unsaved_changes:
            return True

        reply = QMessageBox.question(
            self,
            "Discard unsaved changes?",
            "The current PDF has unsaved changes. Continue without saving?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )
        return reply == QMessageBox.Yes

    def closeEvent(self, event) -> None:  # noqa: N802 - Qt method name
        if self._confirm_discard_changes():
            if self.document is not None:
                self.document.close()
            event.accept()
        else:
            event.ignore()
