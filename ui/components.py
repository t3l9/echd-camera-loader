"""
Современные компоненты на PyQt6
"""
from PyQt6.QtWidgets import QPushButton, QLineEdit, QFrame, QLabel, QComboBox, QCheckBox, QRadioButton, QProgressBar, QScrollArea, QFrame
from PyQt6.QtCore import Qt
from ui.modern_styles import Colors, Typography, Spacing, Styles


class Button(QPushButton):
    """Современная кнопка"""
    def __init__(self, text="", parent=None, variant="primary"):
        super().__init__(text, parent)
        if variant == "primary":
            self.setStyleSheet(Styles.BUTTON_PRIMARY)
        elif variant == "secondary":
            self.setStyleSheet(Styles.BUTTON_SECONDARY)
        elif variant == "ghost":
            self.setStyleSheet(Styles.BUTTON_GHOST)


class Input(QLineEdit):
    """Современное поле ввода"""
    def __init__(self, placeholder="", parent=None):
        super().__init__(parent)
        self.setPlaceholderText(placeholder)
        self.setStyleSheet(Styles.INPUT)


class Card(QFrame):
    """Современная карточка"""
    def __init__(self, parent=None, elevated=False):
        super().__init__(parent)
        self.setObjectName("cardWidget")
        if elevated:
            self.setStyleSheet(Styles.CARD_ELEVATED)
        else:
            self.setStyleSheet(Styles.CARD)


class Label(QLabel):
    """Современный лейбл"""
    def __init__(self, text="", variant="body", parent=None):
        super().__init__(text, parent)
        if variant == "heading":
            self.setStyleSheet(Styles.LABEL_HEADING)
        elif variant == "subheading":
            self.setStyleSheet(Styles.LABEL_SUBHEADING)
        elif variant == "muted":
            self.setStyleSheet(Styles.LABEL_MUTED)
        elif variant == "primary":
            self.setStyleSheet(Styles.LABEL_PRIMARY)
        else:
            self.setStyleSheet(Styles.LABEL_BODY)
        self.setWordWrap(True)


class ComboBox(QComboBox):
    """Современный выпадающий список"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(Styles.INPUT)


class CheckBox(QCheckBox):
    """Современный чекбокс"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.CHECKBOX)


class RadioButton(QRadioButton):
    """Современная радиокнопка"""
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self.setStyleSheet(Styles.RADIO)


class ProgressBar(QProgressBar):
    """Современный прогресс-бар"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(Styles.PROGRESS)
        self.setTextVisible(False)


class ScrollArea(QScrollArea):
    """Современная область прокрутки"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(Styles.SCROLLBAR)
        self.setWidgetResizable(True)


class Divider(QFrame):
    """Современный разделитель"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.HLine)
        self.setFixedHeight(1)
        self.setStyleSheet(f"background-color: {Colors.BORDER};")
