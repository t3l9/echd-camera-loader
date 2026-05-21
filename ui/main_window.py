"""
Главное окно - PyQt6, современный бело-фиолетовый дизайн
"""
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QTabWidget
from PyQt6.QtCore import QTimer, Qt

from config import APP_VERSION
from core.google_sheets import GoogleSheetsManager
from services.update_manager import UpdateManager
from threads.update_thread import UpdateCheckThread
from ui.tabs.delayed_start_tab import DelayedStartTab
from ui.tabs.updates_tab import UpdatesTab
from ui.tabs.info_tab import InfoTab
from ui.login_window import LoginWindow
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, Card, Label, ScrollArea, RadioButton

logger = logging.getLogger(__name__)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.sheets_manager = GoogleSheetsManager()
        self.available_sheets = []
        self.sheets_radio_group = []
        self.current_version = APP_VERSION
        self.update_manager = UpdateManager(current_version=self.current_version)
        self.login_window = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"ЕЦХД Камеры v{self.current_version}")
        self.resize(1000, 720)
        self.setStyleSheet(Styles.MAIN_WINDOW)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        main_layout.setSpacing(Spacing.MD)

        # ===== ЗАГОЛОВОК (градиентный) =====
        header_card = Card()
        header_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {Colors.PRIMARY}, stop:1 {Colors.PRIMARY_DARK});
                border: none;
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.MD, Spacing.MD)

        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title = Label("ЕЦХД Камеры", "heading")
        title.setStyleSheet("font-size: 22px; font-weight: 700; color: white; border: none; background: transparent;")
        title.setWordWrap(False)
        title_layout.addWidget(title)

        version = Label(f"v{self.current_version}", "muted")
        version.setStyleSheet("font-size: 12px; color: rgba(255,255,255,0.7); border: none; background: transparent;")
        title_layout.addWidget(version)

        header_layout.addLayout(title_layout)
        header_layout.addStretch()

        # Кнопка обновлений
        self.updates_btn = Button("🔄 Обновления", variant="secondary")
        self.updates_btn.setFixedHeight(40)
        self.updates_btn.setMinimumWidth(140)
        self.updates_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255,255,255,0.15);
                color: white;
                border: 1px solid rgba(255,255,255,0.4);
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.25);
                border-color: rgba(255,255,255,0.7);
            }}
        """)
        self.updates_btn.clicked.connect(lambda: self.tab_widget.setCurrentIndex(2))
        header_layout.addWidget(self.updates_btn)

        main_layout.addWidget(header_card)
        
        # ===== ВКЛАДКИ =====
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet(Styles.TAB)
        
        self.main_content = self.create_main_tab()
        self.delayed_content = DelayedStartTab()
        self.delayed_tab = self.delayed_content  # alias for camera_processor
        self.updates_content = UpdatesTab(self.update_manager)
        self.info_content = InfoTab(self.current_version)
        
        self.tab_widget.addTab(self.main_content, "📋 Главная")
        self.tab_widget.addTab(self.delayed_content, "⏰ Отложенный")
        self.tab_widget.addTab(self.updates_content, "🔄 Обновления")
        self.tab_widget.addTab(self.info_content, "ℹ️ Справка")
        
        main_layout.addWidget(self.tab_widget)
        
        # ===== СТАТУС БАР =====
        status_card = Card()
        status_card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: {Spacing.RADIUS_MD}px;
            }}
        """)
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(Spacing.LG, Spacing.SM, Spacing.MD, Spacing.SM)

        dot = Label("●", "muted")
        dot.setStyleSheet(f"color: {Colors.SUCCESS}; font-size: 10px; font-weight: 700; border: none; background: transparent;")
        dot.setWordWrap(False)
        dot.setFixedWidth(16)
        status_layout.addWidget(dot)

        self.status_label = Label("Готов к работе", "muted")
        self.status_label.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; border: none; background: transparent;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()

        exit_btn = Button("Выход", variant="secondary")
        exit_btn.setFixedHeight(36)
        exit_btn.setMinimumWidth(90)
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_SECONDARY};
                border: 1px solid {Colors.BORDER};
                border-radius: {Spacing.RADIUS_SM}px;
                padding: 8px 18px;
                font-size: 13px;
                font-weight: 500;
            }}
            QPushButton:hover {{
                border-color: {Colors.ERROR};
                color: {Colors.ERROR};
                background-color: #FEF2F2;
            }}
        """)
        exit_btn.clicked.connect(self.close_application)
        status_layout.addWidget(exit_btn)

        main_layout.addWidget(status_card)

        QTimer.singleShot(300, self.load_worksheets)
        QTimer.singleShot(1000, self.check_updates_on_start)

    def create_main_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # --- Баннер с шагами ---
        steps_card = Card()
        steps_card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {Colors.PRIMARY_PALE}, stop:1 #F5F3FF);
                border: 1px solid {Colors.PRIMARY_LIGHT};
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)
        steps_layout = QHBoxLayout(steps_card)
        steps_layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)
        steps_layout.setSpacing(0)

        for i, (num, text) in enumerate((
            ("1", "Загрузить листы"),
            ("2", "Выбрать лист"),
            ("3", "Настроить"),
            ("4", "Запустить"),
        )):
            col = QVBoxLayout()
            col.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            col.setSpacing(4)

            circle = Label(num)
            circle.setFixedSize(32, 32)
            circle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            circle.setStyleSheet(f"""
                font-size: 14px; font-weight: 800; color: white;
                background-color: {Colors.PRIMARY}; border: none;
                border-radius: 16px;
            """)
            col.addWidget(circle, alignment=Qt.AlignmentFlag.AlignHCenter)

            step_lbl = Label(text)
            step_lbl.setAlignment(Qt.AlignmentFlag.AlignHCenter)
            step_lbl.setStyleSheet(f"font-size: 11px; font-weight: 600; color: {Colors.PRIMARY_DARK}; background: transparent; border: none;")
            col.addWidget(step_lbl)
            steps_layout.addLayout(col)

            if i < 3:
                arr = Label("→")
                arr.setStyleSheet(f"font-size: 16px; color: {Colors.PRIMARY_LIGHT}; background: transparent; border: none;")
                arr.setAlignment(Qt.AlignmentFlag.AlignVCenter)
                steps_layout.addWidget(arr)

        layout.addWidget(steps_card)

        # --- Кнопка загрузки листов ---
        self.load_btn = Button("Загрузить листы из Google Таблицы", variant="primary")
        self.load_btn.setFixedHeight(52)
        self.load_btn.setStyleSheet(f"""
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
        self.load_btn.clicked.connect(self.load_worksheets)
        layout.addWidget(self.load_btn)

        # --- Статус загрузки ---
        self.loading_label = Label("", "muted")
        self.loading_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.loading_label)

        # --- Карточка со списком листов ---
        self.sheets_card = Card()
        self.sheets_card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)
        sheets_layout = QVBoxLayout(self.sheets_card)
        sheets_layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        sheets_layout.setSpacing(Spacing.SM)

        hdr_row = QHBoxLayout()
        lbl_sheets = Label("Выберите лист:", "subheading")
        lbl_sheets.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {Colors.TEXT_MAIN}; background: transparent; border: none;")
        hdr_row.addWidget(lbl_sheets)
        hdr_row.addStretch()
        self.sheets_count_lbl = Label("", "muted")
        self.sheets_count_lbl.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_MUTED}; background: transparent; border: none;")
        hdr_row.addWidget(self.sheets_count_lbl)
        sheets_layout.addLayout(hdr_row)

        self.sheets_scroll = ScrollArea()
        self.sheets_scroll.setFixedHeight(290)
        self.sheets_container = QWidget()
        self.sheets_layout = QVBoxLayout(self.sheets_container)
        self.sheets_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sheets_layout.setSpacing(6)
        self.sheets_scroll.setWidget(self.sheets_container)
        sheets_layout.addWidget(self.sheets_scroll)

        layout.addWidget(self.sheets_card)
        self.sheets_card.hide()

        # --- Кнопка продолжить ---
        self.continue_btn = Button("Далее — настройка запуска →", variant="primary")
        self.continue_btn.setFixedHeight(52)
        self.continue_btn.setStyleSheet(f"""
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
        self.continue_btn.clicked.connect(self.on_continue)
        self.continue_btn.setEnabled(False)
        layout.addWidget(self.continue_btn)

        layout.addStretch()
        return widget

    def load_worksheets(self):
        try:
            self.load_btn.setEnabled(False)
            self.loading_label.setText("Загрузка...")
            
            self.available_sheets = self.sheets_manager.get_worksheets()
            self.on_sheets_loaded(self.available_sheets)
        except Exception as e:
            self.on_sheets_error(str(e))

    def on_sheets_loaded(self, sheets):
        for btn in self.sheets_radio_group:
            btn.deleteLater()
        self.sheets_radio_group = []

        for i, sheet in enumerate(sheets):
            radio = RadioButton(f"  {sheet}")
            radio.setStyleSheet(f"""
                QRadioButton {{
                    color: {Colors.TEXT_MAIN};
                    font-size: 14px;
                    padding: 14px 16px;
                    background-color: {Colors.WHITE};
                    border: 1px solid {Colors.BORDER};
                    border-radius: {Spacing.RADIUS_MD}px;
                    font-weight: 500;
                }}
                QRadioButton:hover {{
                    background-color: {Colors.PRIMARY_PALE};
                    border-color: {Colors.PRIMARY};
                    color: {Colors.PRIMARY_DARK};
                }}
                QRadioButton:checked {{
                    background-color: {Colors.PRIMARY_PALE};
                    border: 2px solid {Colors.PRIMARY};
                    color: {Colors.PRIMARY_DARK};
                    font-weight: 600;
                }}
                QRadioButton::indicator {{
                    width: 18px;
                    height: 18px;
                    border-radius: 9px;
                    border: 2px solid {Colors.BORDER};
                    background: {Colors.WHITE};
                    margin-right: 4px;
                }}
                QRadioButton::indicator:checked {{
                    background: {Colors.PRIMARY};
                    border: 5px solid {Colors.PRIMARY};
                }}
                QRadioButton::indicator:hover {{
                    border-color: {Colors.PRIMARY};
                }}
            """)
            self.sheets_radio_group.append(radio)
            self.sheets_layout.addWidget(radio)

        if self.sheets_radio_group:
            self.sheets_radio_group[0].setChecked(True)

        self.sheets_count_lbl.setText(f"{len(sheets)} листов")
        self.loading_label.setText(f"✅ Загружено листов: {len(sheets)}")
        self.loading_label.setStyleSheet(f"font-size: 13px; color: {Colors.SUCCESS}; font-weight: 600;")
        self.load_btn.setEnabled(True)
        self.continue_btn.setEnabled(True)
        self.sheets_card.show()
        self.status_label.setText("Листы Google Таблицы загружены")

    def on_sheets_error(self, error):
        self.loading_label.setText(f"❌ Ошибка соединения")
        self.loading_label.setStyleSheet(f"font-size: 13px; color: {Colors.ERROR}; font-weight: 600;")
        self.load_btn.setEnabled(True)
        QMessageBox.critical(self, "Ошибка", error)

    def on_continue(self):
        selected = None
        for radio in self.sheets_radio_group:
            if radio.isChecked():
                selected = radio.text()
                break
        
        if not selected:
            QMessageBox.warning(self, "Внимание", "Выберите лист")
            return
        
        sheet_name = selected.strip()
        self.login_window = LoginWindow(sheet_name, self.sheets_manager, self)
        self.login_window.show()
        self.hide()

    def check_updates_on_start(self):
        self._update_thread = UpdateCheckThread(self.update_manager)
        self._update_thread.update_found.connect(self._on_update_found)
        self._update_thread.start()

    def _on_update_found(self, info):
        self.updates_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255,255,255,0.25);
                color: white;
                border: 1px solid {Colors.WARNING};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 10px 20px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: rgba(255,255,255,0.35);
            }}
        """)

    def close_application(self):
        reply = QMessageBox.question(self, 'Выход', 'Закрыть?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.login_window:
                self.login_window.close()
            self.close()
