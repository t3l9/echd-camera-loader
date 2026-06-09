"""
Диалог прогресса
"""
import time
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QApplication, QFrame
from PyQt6.QtCore import Qt, QTimer
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, ProgressBar, Label


class ProgressDialog(QDialog):
    def __init__(self, total, use_random=False, parent=None):
        super().__init__(parent)
        self.total = total
        self._start_time = time.time()
        self._current = 0

        self.setWindowTitle("Обработка (случайный порядок)" if use_random else "Обработка камер")
        self.setModal(True)
        self.resize(480, 310)
        self.setMinimumWidth(420)
        self.setStyleSheet(Styles.MAIN_WINDOW)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowType.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.XL, Spacing.XL, Spacing.XL, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # --- Заголовок + процент ---
        top_row = QHBoxLayout()
        self.title_label = Label("Обработка камер", "subheading")
        self.title_label.setWordWrap(False)
        top_row.addWidget(self.title_label)
        top_row.addStretch()

        self.pct_label = QDialog.__new__(Label)
        self.pct_label = Label("0%", "body")
        self.pct_label.setStyleSheet(
            f"font-size: 22px; font-weight: 700; color: {Colors.PRIMARY};"
        )
        self.pct_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        top_row.addWidget(self.pct_label)
        layout.addLayout(top_row)

        # --- Прогресс-бар ---
        self.progress_bar = ProgressBar()
        self.progress_bar.setMaximum(total)
        self.progress_bar.setFixedHeight(10)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: none;
                border-radius: 5px;
                background-color: {Colors.BG_HOVER};
                height: 10px;
            }}
            QProgressBar::chunk {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY_LIGHT}, stop:1 {Colors.PRIMARY_DARK});
                border-radius: 5px;
            }}
        """)
        layout.addWidget(self.progress_bar)

        # --- Счётчик ---
        self.counter_label = Label(f"0 / {total} камер", "body")
        self.counter_label.setStyleSheet(
            f"font-size: 15px; font-weight: 600; color: {Colors.TEXT_MAIN};"
        )
        self.counter_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.counter_label)

        # --- Разделитель ---
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {Colors.BORDER};")
        layout.addWidget(sep)

        # --- Статус текущей камеры ---
        self.status_label = Label("Подготовка...", "muted")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setFixedHeight(44)
        layout.addWidget(self.status_label)

        # --- Таймер и ETA ---
        time_row = QHBoxLayout()

        self.elapsed_label = Label("⏱  00:00", "muted")
        self.elapsed_label.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; font-weight: 500;"
        )
        time_row.addWidget(self.elapsed_label)
        time_row.addStretch()

        self.eta_label = Label("", "muted")
        self.eta_label.setStyleSheet(
            f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; font-weight: 500;"
        )
        self.eta_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        time_row.addWidget(self.eta_label)

        layout.addLayout(time_row)

        # --- Кнопка отмены ---
        self.cancel_button = Button("Отмена", variant="secondary")
        self.cancel_button.setFixedHeight(40)
        self.cancel_button.setMinimumWidth(120)
        layout.addWidget(self.cancel_button, alignment=Qt.AlignmentFlag.AlignCenter)

        # --- Живой таймер ---
        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick)
        self._timer.start(1000)

    def _tick(self):
        elapsed = int(time.time() - self._start_time)
        m, s = divmod(elapsed, 60)
        self.elapsed_label.setText(f"⏱  {m:02d}:{s:02d}")

        if self._current > 0 and self._current < self.total:
            rate = self._current / max(elapsed, 1)
            remaining = int((self.total - self._current) / rate)
            rm, rs = divmod(remaining, 60)
            self.eta_label.setText(f"Осталось: ~{rm:02d}:{rs:02d}")
        elif self._current >= self.total and self.total > 0:
            self.eta_label.setText("Завершено")

    def update_progress(self, current, total, status):
        self._current = current
        self.progress_bar.setValue(current)
        self.counter_label.setText(f"{current} / {total} камер")
        self.status_label.setText(status)

        if total > 0:
            pct = int((current / total) * 100)
            self.pct_label.setText(f"{pct}%")
            self.title_label.setText("Обработка камер")

        QApplication.processEvents()

    def closeEvent(self, event):
        self._timer.stop()
        super().closeEvent(event)
