"""
Вкладка отложенного запуска - PyQt6
"""
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QDialog, QDialogButtonBox
from PyQt6.QtCore import Qt
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, Card, Label


class DelayedStartTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_datetime = None
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        layout.addWidget(Label("⏰ Отложенный запуск", "subheading"))
        layout.addWidget(Label("Запустите программу в удобное время", "muted"))
        
        # Инструкция
        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        card_layout.setSpacing(Spacing.SM)
        
        card_layout.addWidget(Label("Как это работает:", "subheading"))
        card_layout.addWidget(Label("1. Выберите время запуска"))
        card_layout.addWidget(Label("2. Отсканируйте биометрию на сайте"))
        card_layout.addWidget(Label("3. Занимайтесь делами — программа запустится сама"))
        
        warning = Label("⚠️ Отключите спящий режим: Win+I → Система → Питание → Никогда", "muted")
        warning.setStyleSheet(f"color: {Colors.WARNING}; font-weight: 500;")
        card_layout.addWidget(warning)
        
        layout.addWidget(card)
        
        # Кнопка
        self.select_btn = Button("📅 Выбрать время", variant="primary")
        self.select_btn.setFixedHeight(48)
        self.select_btn.clicked.connect(self.select_time)
        layout.addWidget(self.select_btn)
        
        # Инфо
        self.time_info = Card()
        time_layout = QVBoxLayout(self.time_info)
        time_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        self.time_label = Label("Время не выбрано", "muted")
        time_layout.addWidget(self.time_label)
        
        layout.addWidget(self.time_info)
        
        # Сброс
        self.reset_btn = Button("🗑️ Сбросить", variant="secondary")
        self.reset_btn.clicked.connect(self.reset)
        self.reset_btn.setEnabled(False)
        layout.addWidget(self.reset_btn)
        
        layout.addStretch()

    def select_time(self):
        """Диалог выбора времени"""
        from PyQt6.QtWidgets import QDateTimeEdit
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите время")
        dialog.setFixedSize(350, 200)
        
        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        
        layout.addWidget(Label("Выберите дату и время:", "subheading"))
        
        datetime_edit = QDateTimeEdit()
        datetime_edit.setDateTime(datetime.now())
        datetime_edit.setCalendarPopup(True)
        datetime_edit.setDisplayFormat("dd.MM.yyyy HH:mm")
        datetime_edit.setMinimumDateTime(datetime.now())
        datetime_edit.setStyleSheet(Styles.INPUT)
        layout.addWidget(datetime_edit)
        
        # Кнопки
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel | 
            QDialogButtonBox.StandardButton.Ok
        )
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.selected_datetime = datetime_edit.dateTime().toPyDateTime()
            now = datetime.now()
            if self.selected_datetime > now:
                delta = self.selected_datetime - now
                h = delta.seconds // 3600
                m = (delta.seconds % 3600) // 60
                self.time_label.setText(f"✅ Запуск: {self.selected_datetime.strftime('%d.%m в %H:%M')} (через {h}ч {m}м)")
                self.time_label.setStyleSheet(f"color: {Colors.SUCCESS}; font-weight: 600;")
            else:
                self.time_label.setText("⚠️ Время в прошлом")
            self.reset_btn.setEnabled(True)

    def reset(self):
        self.selected_datetime = None
        self.time_label.setText("Время не выбрано")
        self.time_label.setStyleSheet("")
        self.reset_btn.setEnabled(False)

    def get_wait_seconds(self):
        if self.selected_datetime:
            now = datetime.now()
            if self.selected_datetime > now:
                return min(int((self.selected_datetime - now).total_seconds()), 18000)
        return 40
