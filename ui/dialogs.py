"""
Диалог прогресса
"""
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, ProgressBar, Label


class ProgressDialog(QDialog):
    def __init__(self, total, use_random=False, parent=None):
        super().__init__(parent)
        self.total = total
        self.setWindowTitle("Обработка (случайный порядок)" if use_random else "Обработка")
        self.setModal(True)
        self.resize(450, 220)
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        # Заголовок
        self.title_label = Label("Обработка камер", "subheading")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        # Счётчик
        self.counter_label = Label(f"0 / {total}")
        self.counter_label.setStyleSheet(f"font-size: {Typography.SIZE_XL}px; font-weight: 600; color: {Colors.PRIMARY};")
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.counter_label)

        # Прогресс
        self.progress_bar = ProgressBar()
        self.progress_bar.setMaximum(total)
        self.progress_bar.setFixedHeight(10)
        layout.addWidget(self.progress_bar)

        # Статус
        self.status_label = Label("Подготовка...", "muted")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        layout.addWidget(self.status_label)
        
        # Кнопка
        self.cancel_button = Button("⏹️ Отмена", variant="secondary")
        self.cancel_button.setFixedHeight(40)
        layout.addWidget(self.cancel_button)

    def update_progress(self, current, total, status):
        self.counter_label.setText(f"{current} / {total}")
        self.progress_bar.setValue(current)
        self.status_label.setText(status)
        
        if total > 0:
            pct = (current / total) * 100
            self.title_label.setText(f"Обработка — {pct:.0f}%")

        QApplication.processEvents()
