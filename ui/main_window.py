"""
Главное окно - PyQt6, современный бело-фиолетовый дизайн
"""
import logging
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QMessageBox, QTabWidget
from PyQt6.QtCore import QTimer, Qt

from config import APP_VERSION
from core.google_sheets import GoogleSheetsManager
from services.update_manager import UpdateManager
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
        
        # ===== ЗАГОЛОВОК =====
        header_card = Card()
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        
        title_layout = QVBoxLayout()
        title_layout.setSpacing(2)
        title = Label("ЕЦХД Камеры", "heading")
        title.setStyleSheet(f"font-size: 22px;")
        title_layout.addWidget(title)
        
        version = Label(f"v{self.current_version}", "muted")
        version.setStyleSheet(f"font-size: 12px;")
        title_layout.addWidget(version)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Кнопка обновлений
        self.updates_btn = Button("🔄 Обновления", variant="secondary")
        self.updates_btn.setFixedHeight(44)
        self.updates_btn.setMinimumWidth(140)
        self.updates_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_MAIN};
                border: 2px solid {Colors.BORDER};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                border-color: {Colors.PRIMARY};
                color: {Colors.PRIMARY};
                background-color: {Colors.PRIMARY_PALE};
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
        self.updates_content = UpdatesTab(self.update_manager)
        self.info_content = InfoTab(self.current_version)
        
        self.tab_widget.addTab(self.main_content, "📋 Главная")
        self.tab_widget.addTab(self.delayed_content, "⏰ Отложенный")
        self.tab_widget.addTab(self.updates_content, "🔄 Обновления")
        self.tab_widget.addTab(self.info_content, "ℹ️ Справка")
        
        main_layout.addWidget(self.tab_widget)
        
        # ===== СТАТУС БАР =====
        status_card = Card()
        status_layout = QHBoxLayout(status_card)
        status_layout.setContentsMargins(Spacing.MD, Spacing.SM, Spacing.MD, Spacing.SM)
        
        self.status_label = Label("Готов", "muted")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        exit_btn = Button("Выход", variant="secondary")
        exit_btn.setFixedHeight(40)
        exit_btn.setMinimumWidth(100)
        exit_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.WHITE};
                color: {Colors.TEXT_MAIN};
                border: 2px solid {Colors.BORDER};
                border-radius: {Spacing.RADIUS_MD}px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
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
        layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        layout.setSpacing(Spacing.SM)
        
        self.load_btn = Button("📋 Загрузить листы", variant="primary")
        self.load_btn.setFixedHeight(50)
        self.load_btn.clicked.connect(self.load_worksheets)
        layout.addWidget(self.load_btn)
        
        self.loading_label = Label("", "muted")
        layout.addWidget(self.loading_label)
        
        self.sheets_card = Card()
        sheets_layout = QVBoxLayout(self.sheets_card)
        sheets_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        sheets_layout.setSpacing(Spacing.SM)
        
        sheets_layout.addWidget(Label("Выберите лист:", "subheading"))
        
        self.sheets_scroll = ScrollArea()
        self.sheets_scroll.setFixedHeight(350)
        self.sheets_container = QWidget()
        self.sheets_layout = QVBoxLayout(self.sheets_container)
        self.sheets_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.sheets_layout.setSpacing(Spacing.SM)
        self.sheets_scroll.setWidget(self.sheets_container)
        sheets_layout.addWidget(self.sheets_scroll)
        
        layout.addWidget(self.sheets_card)
        self.sheets_card.hide()
        
        self.continue_btn = Button("Далее →", variant="primary")
        self.continue_btn.setFixedHeight(50)
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
            radio = RadioButton(f"{i+1}. {sheet}")
            radio.setStyleSheet(f"""
                QRadioButton {{
                    color: {Colors.TEXT_MAIN};
                    font-size: 14px;
                    padding: 16px 18px;
                    background-color: {Colors.WHITE};
                    border: 1px solid {Colors.BORDER};
                    border-radius: {Spacing.RADIUS_MD}px;
                    margin: 3px 0;
                    font-weight: 500;
                }}
                QRadioButton:hover {{
                    background-color: {Colors.PRIMARY_PALE};
                    border-color: {Colors.PRIMARY};
                }}
                QRadioButton::indicator {{
                    width: 20px;
                    height: 20px;
                }}
            """)
            self.sheets_radio_group.append(radio)
            self.sheets_layout.addWidget(radio)
        
        if self.sheets_radio_group:
            self.sheets_radio_group[0].setChecked(True)
        
        self.loading_label.setText(f"✅ Найдено листов: {len(sheets)}")
        self.load_btn.setEnabled(True)
        self.continue_btn.setEnabled(True)
        self.sheets_card.show()
        self.status_label.setText("Листы загружены")

    def on_sheets_error(self, error):
        self.loading_label.setText(f"❌ Ошибка: {error[:50]}")
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
        
        sheet_name = selected.split(". ", 1)[-1]
        self.login_window = LoginWindow(sheet_name, self.sheets_manager, self)
        self.login_window.show()
        self.hide()

    def check_updates_on_start(self):
        try:
            update_info = self.update_manager.check_for_updates()
            if update_info['available']:
                self.updates_btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {Colors.BG_HOVER};
                        color: {Colors.TEXT_MAIN};
                        border: 2px solid {Colors.WARNING};
                        border-radius: {Spacing.RADIUS_MD}px;
                        padding: 10px 18px;
                        font-size: 13px;
                        font-weight: 600;
                    }}
                    QPushButton:hover {{
                        border-color: {Colors.PRIMARY};
                        color: {Colors.PRIMARY};
                    }}
                """)
        except:
            pass

    def close_application(self):
        reply = QMessageBox.question(self, 'Выход', 'Закрыть?', 
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                                     QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            if self.login_window:
                self.login_window.close()
            self.close()
