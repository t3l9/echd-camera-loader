"""
Вкладка отложенного запуска - PyQt6
"""
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QDialog, QDialogButtonBox,
    QDateTimeEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QDateTime
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, Card, Label


class DelayedStartTab(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_datetime = None
        self._tick_timer = QTimer(self)
        self._tick_timer.timeout.connect(self._tick)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # --- Заголовок ---
        hdr = Label("Отложенный запуск", "subheading")
        hdr.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_MAIN};")
        layout.addWidget(hdr)

        sub = Label("Авторизуйтесь заранее — программа начнёт выгрузку точно в выбранное время", "muted")
        layout.addWidget(sub)

        # --- Инструкция ---
        how_card = Card()
        how_card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.PRIMARY_PALE};
                border: 1px solid {Colors.PRIMARY_LIGHT};
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)
        how_layout = QVBoxLayout(how_card)
        how_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        how_layout.setSpacing(Spacing.XS)

        for step in (
            "1. Нажмите «Выбрать время» и укажите нужное время запуска",
            "2. Нажмите «Запустить обработку» в настройках — программа авторизуется",
            "3. Программа будет ждать до выбранного времени, обновляя сессию",
            "4. В нужный момент выгрузка начнётся автоматически",
        ):
            lbl = Label(step)
            lbl.setStyleSheet(f"font-size: 13px; color: {Colors.PRIMARY_DARK}; background: transparent; border: none;")
            how_layout.addWidget(lbl)

        warn = Label("Отключите спящий режим: Пуск → Питание → Никогда")
        warn.setStyleSheet(f"font-size: 13px; color: {Colors.WARNING}; font-weight: 600; background: transparent; border: none;")
        how_layout.addWidget(warn)

        layout.addWidget(how_card)

        # --- Кнопка выбора времени ---
        self.select_btn = Button("Выбрать время запуска", variant="primary")
        self.select_btn.setFixedHeight(50)
        self.select_btn.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
                color: white;
                border: none;
                border-radius: {Spacing.RADIUS_MD}px;
                font-size: 15px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {Colors.PRIMARY_DARK};
            }}
        """)
        self.select_btn.clicked.connect(self.select_time)
        layout.addWidget(self.select_btn)

        # --- Карточка статуса ---
        self.status_card = Card()
        self._style_status_card("idle")
        status_layout = QVBoxLayout(self.status_card)
        status_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        status_layout.setSpacing(Spacing.XS)

        self.time_label = Label("Время не выбрано", "muted")
        self.time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.time_label.setStyleSheet(f"font-size: 15px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        status_layout.addWidget(self.time_label)

        self.countdown_label = Label("", "muted")
        self.countdown_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.countdown_label.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {Colors.PRIMARY}; background: transparent; border: none;")
        self.countdown_label.hide()
        status_layout.addWidget(self.countdown_label)

        layout.addWidget(self.status_card)

        # --- Кнопка сброса ---
        self.reset_btn = Button("Сбросить время", variant="secondary")
        self.reset_btn.setFixedHeight(40)
        self.reset_btn.setEnabled(False)
        self.reset_btn.clicked.connect(self.reset)
        layout.addWidget(self.reset_btn)

        layout.addStretch()

    def _style_status_card(self, state: str):
        if state == "set":
            self.status_card.setStyleSheet(f"""
                QFrame {{
                    background-color: #ECFDF5;
                    border: 1px solid {Colors.SUCCESS};
                    border-radius: {Spacing.RADIUS_LG}px;
                }}
            """)
        elif state == "expired":
            self.status_card.setStyleSheet(f"""
                QFrame {{
                    background-color: #FEF2F2;
                    border: 1px solid {Colors.ERROR};
                    border-radius: {Spacing.RADIUS_LG}px;
                }}
            """)
        else:
            self.status_card.setStyleSheet(f"""
                QFrame {{
                    background-color: {Colors.BG_CARD};
                    border: 1px solid {Colors.BORDER};
                    border-radius: {Spacing.RADIUS_LG}px;
                }}
            """)

    def select_time(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Время запуска")
        dialog.setFixedSize(360, 200)
        dialog.setStyleSheet(Styles.MAIN_WINDOW)

        layout = QVBoxLayout(dialog)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        layout.addWidget(Label("Выберите дату и время запуска:", "subheading"))

        dt_edit = QDateTimeEdit()
        now = datetime.now()
        dt_edit.setDateTime(QDateTime(now.year, now.month, now.day, now.hour, now.minute))
        dt_edit.setCalendarPopup(True)
        dt_edit.setDisplayFormat("dd.MM.yyyy  HH:mm")
        dt_edit.setMinimumDateTime(QDateTime.currentDateTime())
        dt_edit.setStyleSheet(Styles.INPUT + "QDateTimeEdit { font-size: 16px; padding: 12px; }")
        dt_edit.setFixedHeight(50)
        layout.addWidget(dt_edit)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Cancel |
            QDialogButtonBox.StandardButton.Ok
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("Подтвердить")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("Отмена")
        buttons.accepted.connect(dialog.accept)
        buttons.rejected.connect(dialog.reject)
        layout.addWidget(buttons)

        if dialog.exec() == QDialog.DialogCode.Accepted:
            chosen = dt_edit.dateTime().toPyDateTime()
            now = datetime.now()
            if chosen > now:
                self.selected_datetime = chosen
                self._start_countdown()
            else:
                self.time_label.setText("Выбранное время уже прошло")
                self.time_label.setStyleSheet(f"font-size: 14px; color: {Colors.ERROR}; background: transparent; border: none;")
                self._style_status_card("expired")
            self.reset_btn.setEnabled(True)

    def _start_countdown(self):
        self._tick()
        if not self._tick_timer.isActive():
            self._tick_timer.start(1000)
        self._style_status_card("set")
        self.countdown_label.show()
        self.reset_btn.setEnabled(True)

    def _tick(self):
        if not self.selected_datetime:
            self._tick_timer.stop()
            return

        remaining = int((self.selected_datetime - datetime.now()).total_seconds())

        if remaining <= 0:
            self._tick_timer.stop()
            self.selected_datetime = None
            self.time_label.setText("Время истекло — запустите обработку сейчас")
            self.time_label.setStyleSheet(f"font-size: 14px; color: {Colors.ERROR}; background: transparent; border: none;")
            self.countdown_label.setText("00:00:00")
            self.countdown_label.setStyleSheet(f"font-size: 28px; font-weight: 700; color: {Colors.ERROR}; background: transparent; border: none;")
            self._style_status_card("expired")
            return

        h, rem = divmod(remaining, 3600)
        m, s = divmod(rem, 60)
        self.time_label.setText(f"Запуск: {self.selected_datetime.strftime('%d.%m.%Y в %H:%M')}")
        self.time_label.setStyleSheet(f"font-size: 14px; color: {Colors.SUCCESS}; font-weight: 600; background: transparent; border: none;")
        self.countdown_label.setText(f"{h:02d}:{m:02d}:{s:02d}")
        self.countdown_label.setStyleSheet(f"font-size: 36px; font-weight: 700; color: {Colors.PRIMARY}; background: transparent; border: none;")

    def reset(self):
        self._tick_timer.stop()
        self.selected_datetime = None
        self.time_label.setText("Время не выбрано")
        self.time_label.setStyleSheet(f"font-size: 15px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        self.countdown_label.hide()
        self.countdown_label.setText("")
        self._style_status_card("idle")
        self.reset_btn.setEnabled(False)

    def get_wait_seconds(self):
        if self.selected_datetime:
            now = datetime.now()
            if self.selected_datetime > now:
                return min(int((self.selected_datetime - now).total_seconds()), 18000)
        return 40  # стандартное ожидание инициализации сайта
