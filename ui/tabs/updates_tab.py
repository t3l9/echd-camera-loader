"""
Вкладка обновлений - PyQt6
"""
import webbrowser
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, Card, Label
from threads.update_thread import UpdateCheckThread


class UpdatesTab(QWidget):
    def __init__(self, update_manager):
        super().__init__()
        self.update_manager = update_manager
        self.github_url = "https://github.com/t3l9/echd-camera-loader/releases/latest"
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # --- Заголовок ---
        hdr = Label("Управление обновлениями", "subheading")
        hdr.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_MAIN};")
        layout.addWidget(hdr)

        # --- Карточка текущей версии ---
        ver_card = Card()
        ver_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.PRIMARY_PALE}, stop:1 #F5F3FF);
                border: 1px solid {Colors.PRIMARY_LIGHT};
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)
        ver_layout = QHBoxLayout(ver_card)
        ver_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)

        ver_info = QVBoxLayout()
        ver_info.setSpacing(4)
        lbl_cur = Label("Установленная версия", "muted")
        lbl_cur.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        ver_info.addWidget(lbl_cur)

        self.version_label = Label(f"v{self.update_manager.current_version}")
        self.version_label.setStyleSheet(f"font-size: 32px; font-weight: 800; color: {Colors.PRIMARY}; background: transparent; border: none;")
        ver_info.addWidget(self.version_label)

        ver_layout.addLayout(ver_info)
        ver_layout.addStretch()

        self.badge_label = Label("актуальная", "muted")
        self.badge_label.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; color: {Colors.SUCCESS};
            background-color: #D1FAE5; border: 1px solid {Colors.SUCCESS};
            border-radius: 12px; padding: 4px 12px;
        """)
        self.badge_label.setFixedHeight(28)
        ver_layout.addWidget(self.badge_label, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(ver_card)

        # --- Кнопка проверки ---
        self.check_btn = Button("Проверить наличие обновлений", variant="primary")
        self.check_btn.setFixedHeight(50)
        self.check_btn.setStyleSheet(f"""
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
            QPushButton:disabled {{
                background: {Colors.BORDER};
                color: {Colors.TEXT_MUTED};
            }}
        """)
        self.check_btn.clicked.connect(self.check_updates)
        layout.addWidget(self.check_btn)

        # --- Статус ---
        self.status_label = Label("", "muted")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY};")
        layout.addWidget(self.status_label)

        # --- Карточка с новой версией ---
        self.update_card = Card()
        self.update_card.setStyleSheet(f"""
            QFrame {{
                background-color: #ECFDF5;
                border: 1px solid {Colors.SUCCESS};
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)
        upd_layout = QVBoxLayout(self.update_card)
        upd_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        upd_layout.setSpacing(Spacing.SM)

        upd_hdr = Label("Доступна новая версия!", "subheading")
        upd_hdr.setStyleSheet(f"font-size: 16px; font-weight: 700; color: #065F46; background: transparent; border: none;")
        upd_layout.addWidget(upd_hdr)

        self.new_version_label = Label("", "body")
        self.new_version_label.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {Colors.SUCCESS}; background: transparent; border: none;")
        upd_layout.addWidget(self.new_version_label)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: #A7F3D0;")
        upd_layout.addWidget(sep)

        self.notes_label = Label("", "muted")
        self.notes_label.setWordWrap(True)
        self.notes_label.setStyleSheet(f"font-size: 13px; color: #065F46; background: transparent; border: none;")
        upd_layout.addWidget(self.notes_label)

        self.github_btn = Button("Скачать на GitHub", variant="primary")
        self.github_btn.setFixedHeight(44)
        self.github_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.SUCCESS};
                color: white;
                border: none;
                border-radius: {Spacing.RADIUS_MD}px;
                font-size: 14px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: #059669;
            }}
        """)
        self.github_btn.clicked.connect(self.open_github)
        upd_layout.addWidget(self.github_btn)

        self.update_card.hide()
        layout.addWidget(self.update_card)

        layout.addStretch()

    def check_updates(self):
        self.check_btn.setEnabled(False)
        self.status_label.setText("Подключение к GitHub...")
        self.update_card.hide()
        self.badge_label.setText("проверка...")
        self.badge_label.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; color: {Colors.TEXT_SECONDARY};
            background-color: {Colors.BG_HOVER}; border: 1px solid {Colors.BORDER};
            border-radius: 12px; padding: 4px 12px;
        """)

        self._thread = UpdateCheckThread(self.update_manager)
        self._thread.update_found.connect(self._on_update_found)
        self._thread.no_update.connect(self._on_no_update)
        self._thread.error.connect(self._on_error)
        self._thread.start()

    def _on_update_found(self, info):
        self.status_label.setText("")
        self.new_version_label.setText(f"v{info['latest_version']}")
        notes = info.get('release_notes', '')[:400]
        self.notes_label.setText(notes + "..." if len(notes) >= 400 else notes)
        self.update_card.show()
        self.badge_label.setText("обновление!")
        self.badge_label.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; color: white;
            background-color: {Colors.SUCCESS}; border: none;
            border-radius: 12px; padding: 4px 12px;
        """)
        self.check_btn.setEnabled(True)

    def _on_no_update(self):
        self.status_label.setText("Установлена актуальная версия")
        self.badge_label.setText("актуальная")
        self.badge_label.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; color: {Colors.SUCCESS};
            background-color: #D1FAE5; border: 1px solid {Colors.SUCCESS};
            border-radius: 12px; padding: 4px 12px;
        """)
        self.check_btn.setEnabled(True)

    def _on_error(self, err):
        self.status_label.setText("GitHub недоступен — проверьте интернет-соединение")
        self.badge_label.setText("нет связи")
        self.badge_label.setStyleSheet(f"""
            font-size: 12px; font-weight: 600; color: {Colors.TEXT_SECONDARY};
            background-color: {Colors.BG_HOVER}; border: 1px solid {Colors.BORDER};
            border-radius: 12px; padding: 4px 12px;
        """)
        self.check_btn.setEnabled(True)

    def open_github(self):
        webbrowser.open(self.github_url)
        self.status_label.setText("Открыто в браузере")
