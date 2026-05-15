from __future__ import annotations

import fitz
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QColorDialog,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QSpinBox,
    QTextEdit,
    QVBoxLayout,
)


class MetadataDialog(QDialog):
    def __init__(self, metadata: dict[str, str], parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit metadata")

        self.title_input = QLineEdit(metadata.get("title", ""))
        self.author_input = QLineEdit(metadata.get("author", ""))
        self.subject_input = QLineEdit(metadata.get("subject", ""))
        self.keywords_input = QLineEdit(metadata.get("keywords", ""))

        form_layout = QFormLayout()
        form_layout.addRow("Title", self.title_input)
        form_layout.addRow("Author", self.author_input)
        form_layout.addRow("Subject", self.subject_input)
        form_layout.addRow("Keywords", self.keywords_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def metadata(self) -> dict[str, str]:
        return {
            "title": self.title_input.text().strip(),
            "author": self.author_input.text().strip(),
            "subject": self.subject_input.text().strip(),
            "keywords": self.keywords_input.text().strip(),
        }


class ImagePlacementDialog(QDialog):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Place image")

        self.position_input = QComboBox()
        self.position_input.addItems(
            [
                "Top left",
                "Top center",
                "Top right",
                "Center",
                "Bottom left",
                "Bottom center",
                "Bottom right",
            ]
        )
        self.position_input.setCurrentText("Bottom right")

        self.width_input = QSpinBox()
        self.width_input.setRange(25, 100)
        self.width_input.setSuffix("%")
        self.width_input.setValue(35)

        self.margin_input = QSpinBox()
        self.margin_input.setRange(0, 200)
        self.margin_input.setSuffix(" pt")
        self.margin_input.setValue(72)

        form_layout = QFormLayout()
        form_layout.addRow("Position", self.position_input)
        form_layout.addRow("Width", self.width_input)
        form_layout.addRow("Margin", self.margin_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def placement(self) -> tuple[str, int, int]:
        return (
            self.position_input.currentText(),
            self.width_input.value(),
            self.margin_input.value(),
        )


class TextAnnotationDialog(QDialog):
    def __init__(self, page_rect: fitz.Rect, parent=None, values: dict | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Text annotation")
        values = values or {}
        default_rect = fitz.Rect(72, 72, min(page_rect.width - 72, 360), min(page_rect.height - 72, 180))
        annotation_rect = values.get("rect", default_rect)
        self.text_color = values.get("text_color", QColor("#111111"))
        self.fill_color = values.get("fill_color", QColor("#fff4b8"))

        self.text_input = QTextEdit()
        self.text_input.setPlainText(values.get("text", ""))
        self.text_input.setMinimumHeight(90)

        self.x_input = QSpinBox()
        self.x_input.setRange(0, int(page_rect.width))
        self.x_input.setValue(int(annotation_rect.x0))

        self.y_input = QSpinBox()
        self.y_input.setRange(0, int(page_rect.height))
        self.y_input.setValue(int(annotation_rect.y0))

        self.width_input = QSpinBox()
        self.width_input.setRange(20, int(page_rect.width))
        self.width_input.setValue(max(20, int(annotation_rect.width)))

        self.height_input = QSpinBox()
        self.height_input.setRange(20, int(page_rect.height))
        self.height_input.setValue(max(20, int(annotation_rect.height)))

        self.font_size_input = QSpinBox()
        self.font_size_input.setRange(6, 96)
        self.font_size_input.setValue(int(values.get("font_size", 12)))

        self.text_color_button = QPushButton()
        self.text_color_button.clicked.connect(self.choose_text_color)
        self.fill_color_button = QPushButton()
        self.fill_color_button.clicked.connect(self.choose_fill_color)
        self._update_color_buttons()

        position_layout = QHBoxLayout()
        position_layout.addWidget(QLabel("X"))
        position_layout.addWidget(self.x_input)
        position_layout.addWidget(QLabel("Y"))
        position_layout.addWidget(self.y_input)

        size_layout = QHBoxLayout()
        size_layout.addWidget(QLabel("Width"))
        size_layout.addWidget(self.width_input)
        size_layout.addWidget(QLabel("Height"))
        size_layout.addWidget(self.height_input)

        color_layout = QHBoxLayout()
        color_layout.addWidget(QLabel("Text"))
        color_layout.addWidget(self.text_color_button)
        color_layout.addWidget(QLabel("Fill"))
        color_layout.addWidget(self.fill_color_button)

        form_layout = QFormLayout()
        form_layout.addRow("Text", self.text_input)
        form_layout.addRow("Position", position_layout)
        form_layout.addRow("Box size", size_layout)
        form_layout.addRow("Font size", self.font_size_input)
        form_layout.addRow("Colors", color_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout = QVBoxLayout()
        layout.addLayout(form_layout)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def choose_text_color(self) -> None:
        color = QColorDialog.getColor(self.text_color, self, "Text color")
        if color.isValid():
            self.text_color = color
            self._update_color_buttons()

    def choose_fill_color(self) -> None:
        color = QColorDialog.getColor(self.fill_color, self, "Fill color")
        if color.isValid():
            self.fill_color = color
            self._update_color_buttons()

    def values(self) -> dict:
        x = self.x_input.value()
        y = self.y_input.value()
        return {
            "text": self.text_input.toPlainText().strip(),
            "rect": fitz.Rect(x, y, x + self.width_input.value(), y + self.height_input.value()),
            "font_size": self.font_size_input.value(),
            "text_color": self.text_color,
            "fill_color": self.fill_color,
        }

    def _update_color_buttons(self) -> None:
        self.text_color_button.setText(self.text_color.name())
        self.text_color_button.setStyleSheet(f"background: {self.text_color.name()}; color: {self._button_text_color(self.text_color)};")
        self.fill_color_button.setText(self.fill_color.name())
        self.fill_color_button.setStyleSheet(f"background: {self.fill_color.name()}; color: {self._button_text_color(self.fill_color)};")

    def _button_text_color(self, color: QColor) -> str:
        return "#ffffff" if color.lightness() < 128 else "#111111"


class TextAnnotationManagerDialog(QDialog):
    def __init__(self, page: fitz.Page, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Edit text annotations")
        self.page = page
        self.result_action = "none"
        self.selected_index: int | None = None
        self.annotation_values: dict | None = None

        self.annotation_list = QListWidget()
        self._load_annotations()

        self.edit_button = QPushButton("Edit")
        self.edit_button.clicked.connect(self.edit_selected)
        self.delete_button = QPushButton("Remove")
        self.delete_button.clicked.connect(self.delete_selected)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.edit_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.close_button)

        layout = QVBoxLayout()
        layout.addWidget(self.annotation_list)
        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.resize(420, 320)

    def _load_annotations(self) -> None:
        self.annotation_list.clear()
        for index, annotation in enumerate(self._text_annotations()):
            text = annotation.info.get("content", "").strip() or "(empty text)"
            item = QListWidgetItem(f"{index + 1}. {text[:80]}")
            item.setData(Qt.UserRole, index)
            self.annotation_list.addItem(item)

    def _text_annotations(self) -> list[fitz.Annot]:
        return [
            annotation
            for annotation in list(self.page.annots() or [])
            if annotation.type[0] == fitz.PDF_ANNOT_FREE_TEXT
        ]

    def edit_selected(self) -> None:
        item = self.annotation_list.currentItem()
        if item is None:
            return

        annotation_index = item.data(Qt.UserRole)
        annotations = self._text_annotations()
        if annotation_index >= len(annotations):
            return

        annotation = annotations[annotation_index]
        dialog = TextAnnotationDialog(
            self.page.rect,
            self,
            {
                "text": annotation.info.get("content", ""),
                "rect": annotation.rect,
                "font_size": 12,
                "text_color": QColor("#111111"),
                "fill_color": QColor("#fff4b8"),
            },
        )
        if dialog.exec() != QDialog.Accepted:
            return

        self.selected_index = annotation_index
        self.annotation_values = dialog.values()
        self.result_action = "edit"
        self.accept()

    def delete_selected(self) -> None:
        item = self.annotation_list.currentItem()
        if item is None:
            return

        self.selected_index = item.data(Qt.UserRole)
        self.result_action = "delete"
        self.accept()
