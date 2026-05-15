from __future__ import annotations

from PySide6.QtGui import QColor, QPalette


def dark_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1f252c"))
    palette.setColor(QPalette.WindowText, QColor("#edf2f7"))
    palette.setColor(QPalette.Base, QColor("#14191f"))
    palette.setColor(QPalette.AlternateBase, QColor("#242b33"))
    palette.setColor(QPalette.ToolTipBase, QColor("#242b33"))
    palette.setColor(QPalette.ToolTipText, QColor("#edf2f7"))
    palette.setColor(QPalette.Text, QColor("#edf2f7"))
    palette.setColor(QPalette.Button, QColor("#2b333d"))
    palette.setColor(QPalette.ButtonText, QColor("#edf2f7"))
    palette.setColor(QPalette.BrightText, QColor("#ff6b6b"))
    palette.setColor(QPalette.Link, QColor("#69a7ff"))
    palette.setColor(QPalette.Highlight, QColor("#3b82f6"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#7b8794"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#7b8794"))
    return palette


def white_palette() -> QPalette:
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#f6f7f9"))
    palette.setColor(QPalette.WindowText, QColor("#1f2933"))
    palette.setColor(QPalette.Base, QColor("#ffffff"))
    palette.setColor(QPalette.AlternateBase, QColor("#eef1f5"))
    palette.setColor(QPalette.ToolTipBase, QColor("#ffffff"))
    palette.setColor(QPalette.ToolTipText, QColor("#1f2933"))
    palette.setColor(QPalette.Text, QColor("#1f2933"))
    palette.setColor(QPalette.Button, QColor("#eef1f5"))
    palette.setColor(QPalette.ButtonText, QColor("#1f2933"))
    palette.setColor(QPalette.BrightText, QColor("#d64545"))
    palette.setColor(QPalette.Link, QColor("#2f80ed"))
    palette.setColor(QPalette.Highlight, QColor("#2f80ed"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    palette.setColor(QPalette.Disabled, QPalette.Text, QColor("#8a94a3"))
    palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor("#8a94a3"))
    return palette


def dark_stylesheet() -> str:
    return """
        QMainWindow, QDialog, QDockWidget {
            background: #1f252c;
            color: #edf2f7;
        }
        QToolBar, QStatusBar {
            background: #242b33;
            border: 0;
            color: #edf2f7;
        }
        QToolButton {
            color: #edf2f7;
            padding: 4px;
            border-radius: 4px;
        }
        QToolButton:hover {
            background: #34404c;
        }
        QLabel, QListWidget, QComboBox, QLineEdit, QSpinBox, QTextEdit {
            color: #edf2f7;
        }
        QListWidget, QLineEdit, QSpinBox, QComboBox, QTextEdit, QScrollArea {
            background: #14191f;
            border: 1px solid #3a4653;
        }
        QListWidget::item:selected {
            background: #2f80ed;
        }
        QPushButton {
            background: #2b333d;
            color: #edf2f7;
            border: 1px solid #3a4653;
            padding: 5px 10px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background: #34404c;
        }
        QToolTip {
            background-color: #242b33;
            color: #edf2f7;
            border: 1px solid #4a5563;
            padding: 4px;
        }
    """


def white_stylesheet() -> str:
    return """
        QMainWindow, QDialog, QDockWidget {
            background: #f6f7f9;
            color: #1f2933;
        }
        QToolBar, QStatusBar {
            background: #eef1f5;
            border: 0;
            color: #1f2933;
        }
        QToolButton {
            color: #1f2933;
            padding: 4px;
            border-radius: 4px;
        }
        QToolButton:hover {
            background: #dde3ea;
        }
        QListWidget, QLineEdit, QSpinBox, QComboBox, QTextEdit, QScrollArea {
            background: #ffffff;
            border: 1px solid #cfd6df;
        }
        QListWidget::item:selected {
            background: #2f80ed;
            color: #ffffff;
        }
        QPushButton {
            background: #eef1f5;
            color: #1f2933;
            border: 1px solid #cfd6df;
            padding: 5px 10px;
            border-radius: 4px;
        }
        QPushButton:hover {
            background: #dde3ea;
        }
        QToolTip {
            background-color: #ffffff;
            color: #1f2933;
            border: 1px solid #cfd6df;
            padding: 4px;
        }
    """
