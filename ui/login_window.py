"""
Окно авторизации - PyQt6, гармоничный дизайн
"""
import os
import re
import random
import logging
from datetime import datetime
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, QFrame, QMessageBox, QLineEdit
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QCursor

from config import areas, downloads_folder
from threads.camera_thread import CameraProcessingThread
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, Input, Card, Label, ComboBox, CheckBox, ScrollArea
from ui.dialogs import ProgressDialog

logger = logging.getLogger(__name__)


class LoginWindow(QWidget):
    def __init__(self, selected_sheet, sheets_manager, parent_window):
        super().__init__()
        self.selected_sheet = selected_sheet
        self.sheets_manager = sheets_manager
        self.parent_window = parent_window
        self.processing_thread = None
        self.progress_dialog = None
        self.all_selected = True
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Настройка - {self.selected_sheet}")
        self.resize(950, 660)
        self.setMinimumSize(900, 650)
        self.setStyleSheet(Styles.MAIN_WINDOW)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        # ===== ЗАГОЛОВОК =====
        header_layout = QHBoxLayout()
        
        back_btn = Button("← Назад", variant="secondary")
        back_btn.setFixedHeight(44)
        back_btn.setMinimumWidth(110)
        back_btn.clicked.connect(self.go_back)
        header_layout.addWidget(back_btn)
        
        title = Label(f"📋 {self.selected_sheet}", "subheading")
        title.setStyleSheet(f"font-size: 16px;")
        header_layout.addWidget(title)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # ===== ДВЕ КОЛОНКИ =====
        content_layout = QHBoxLayout()
        content_layout.setSpacing(Spacing.LG)
        
        # ===== ЛЕВАЯ КОЛОНКА - Авторизация и настройки =====
        left_column = QVBoxLayout()
        left_column.setSpacing(Spacing.MD)
        left_column.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравнивание по верху
        
        # Авторизация
        auth_card = Card()
        auth_layout = QVBoxLayout(auth_card)
        auth_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        auth_layout.setSpacing(Spacing.SM)
        
        auth_layout.addWidget(Label("🔐 Авторизация", "subheading"))
        
        self.login_input = Input("Логин")
        self.login_input.setFixedHeight(46)
        auth_layout.addWidget(self.login_input)
        
        self.password_input = Input("Пароль")
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setFixedHeight(46)
        auth_layout.addWidget(self.password_input)
        
        # Кнопка показать пароль
        self.show_password_cb = CheckBox("Показать пароль")
        self.show_password_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.PRIMARY};
                font-size: 13px;
                font-weight: 600;
                padding: 6px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {Colors.PRIMARY};
            }}
            QCheckBox::indicator:checked {{
                background: {Colors.PRIMARY};
            }}
        """)
        self.show_password_cb.stateChanged.connect(self._on_password_toggle)
        auth_layout.addWidget(self.show_password_cb)
        
        left_column.addWidget(auth_card)
        
        # Настройки
        settings_card = Card()
        settings_layout = QVBoxLayout(settings_card)
        settings_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        settings_layout.setSpacing(Spacing.SM)
        
        settings_layout.addWidget(Label("⚙️ Параметры", "subheading"))
        
        settings_layout.addWidget(Label("Доля данных:"))
        self.percent_selector = ComboBox()
        self.percent_selector.addItems(["20%", "50%", "100%"])
        self.percent_selector.setFixedHeight(44)
        settings_layout.addWidget(self.percent_selector)
        
        settings_layout.addWidget(Label("Шаг:"))
        self.queue_selector = ComboBox()
        self.queue_selector.setFixedHeight(44)
        settings_layout.addWidget(self.queue_selector)
        
        self.random_order_cb = CheckBox("🎲 Случайный порядок")
        self.random_order_cb.setStyleSheet(f"""
            QCheckBox {{
                color: {Colors.TEXT_MAIN};
                font-size: 14px;
                font-weight: 500;
                padding: 6px 0;
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border-radius: 4px;
                border: 2px solid {Colors.BORDER};
            }}
            QCheckBox::indicator:checked {{
                background: {Colors.PRIMARY};
                border-color: {Colors.PRIMARY};
            }}
        """)
        settings_layout.addWidget(self.random_order_cb)
        
        left_column.addWidget(settings_card)
        left_column.addStretch()  # Растяжка внизу чтобы карточки не растягивались
        
        content_layout.addLayout(left_column, 1)
        
        # ===== ПРАВАЯ КОЛОНКА - Районы (БОЛЬШЕ) =====
        right_column = QVBoxLayout()
        right_column.setSpacing(Spacing.SM)
        right_column.setAlignment(Qt.AlignmentFlag.AlignTop)  # Выравнивание по верху
        
        areas_card = Card()
        areas_layout = QVBoxLayout(areas_card)
        areas_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        areas_layout.setSpacing(Spacing.SM)
        
        # Заголовок с кнопкой
        areas_header = QHBoxLayout()
        areas_header.addWidget(Label("📍 Районы", "subheading"))
        areas_header.addStretch()
        
        self.toggle_btn = Button("✓ Выбрать все", variant="primary")
        self.toggle_btn.setFixedHeight(42)
        self.toggle_btn.setMinimumWidth(140)
        self.toggle_btn.clicked.connect(self.toggle_all_areas)
        areas_header.addWidget(self.toggle_btn)
        
        areas_layout.addLayout(areas_header)
        
        # Счётчик
        self.selected_count_label = Label(f"Выбрано: 0 из {len(areas)}", "muted")
        self.selected_count_label.setStyleSheet(f"font-weight: 600; color: {Colors.PRIMARY}; font-size: 13px;")
        areas_layout.addWidget(self.selected_count_label)
        
        # Список районов - 2 столбика (ПРЯМЫЕ чекбоксы без вложенности)
        self.areas_scroll = ScrollArea()
        self.areas_scroll.setFixedHeight(373)  # Уменьшил высоту для гармонии (было 480)
        self.areas_container = QWidget()
        self.areas_layout = QGridLayout(self.areas_container)
        self.areas_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.areas_layout.setSpacing(4)
        
        self.area_checkboxes = {}
        mid = len(areas) // 2
        
        for i, area in enumerate(areas):
            col = 0 if i < mid else 1
            row = i if i < mid else i - mid
            
            # Создаем чекбокс напрямую без обёртки
            cb = CheckBox(area)
            cb.setStyleSheet(f"""
                QCheckBox {{
                    color: {Colors.TEXT_MAIN};
                    font-size: 13px;
                    font-weight: 500;
                    padding: 10px 12px;
                    background-color: {Colors.WHITE};
                    border: 1px solid {Colors.BORDER};
                    border-radius: {Spacing.RADIUS_MD}px;
                }}
                QCheckBox:hover {{
                    border-color: {Colors.PRIMARY};
                    background-color: {Colors.PRIMARY_PALE};
                }}
                QCheckBox::indicator {{
                    width: 18px;
                    height: 18px;
                    border-radius: 4px;
                    border: 2px solid {Colors.BORDER};
                    background: {Colors.WHITE};
                }}
                QCheckBox::indicator:hover {{
                    border-color: {Colors.PRIMARY};
                }}
                QCheckBox::indicator:checked {{
                    background: {Colors.PRIMARY};
                    border-color: {Colors.PRIMARY};
                }}
            """)
            cb.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            cb.stateChanged.connect(self.update_count)
            self.area_checkboxes[area] = cb
            self.areas_layout.addWidget(cb, row, col)
        
        self.areas_scroll.setWidget(self.areas_container)
        areas_layout.addWidget(self.areas_scroll)
        
        right_column.addWidget(areas_card)
        right_column.addStretch()  # Растяжка внизу
        
        content_layout.addLayout(right_column, 1)
        
        layout.addLayout(content_layout)
        
        # ===== КНОПКА ЗАПУСКА =====
        self.start_btn = Button("🚀 Запустить обработку", variant="primary")
        self.start_btn.setFixedHeight(56)
        self.start_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {Colors.PRIMARY};
                color: white;
                border: none;
                border-radius: {Spacing.RADIUS_MD}px;
                font-size: 16px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background-color: {Colors.PRIMARY_DARK};
            }}
        """)
        self.start_btn.clicked.connect(self.on_ok)
        layout.addWidget(self.start_btn)
        
        self.load_saved_credentials()
        self.update_queue_options()
        self.percent_selector.currentIndexChanged.connect(self.update_queue_options)
        self.update_count()

    def update_count(self):
        selected = sum(1 for cb in self.area_checkboxes.values() if cb.isChecked())
        self.selected_count_label.setText(f"Выбрано: {selected} из {len(self.area_checkboxes)}")
        
        if selected == len(self.area_checkboxes):
            self.toggle_btn.setText("✓ Выбрано все")
            self.toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.SUCCESS};
                    color: white;
                    border: none;
                    border-radius: {Spacing.RADIUS_MD}px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #059669;
                }}
            """)
            self.all_selected = True
        elif selected == 0:
            self.toggle_btn.setText("✓ Выбрать все")
            self.toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.PRIMARY};
                    color: white;
                    border: none;
                    border-radius: {Spacing.RADIUS_MD}px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {Colors.PRIMARY_DARK};
                }}
            """)
            self.all_selected = False
        else:
            self.toggle_btn.setText("◐ Частично")
            self.toggle_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {Colors.WARNING};
                    color: white;
                    border: none;
                    border-radius: {Spacing.RADIUS_MD}px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: #D97706;
                }}
            """)
            self.all_selected = False

    def toggle_all_areas(self):
        if self.all_selected:
            for cb in self.area_checkboxes.values():
                cb.setChecked(False)
        else:
            for cb in self.area_checkboxes.values():
                cb.setChecked(True)
        self.update_count()

    def _on_password_toggle(self, state):
        """Обработчик переключения видимости пароля"""
        if state == 2:  # Qt.CheckState.Checked = 2
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)

    def load_saved_credentials(self):
        settings = QSettings("YourCompany", "YourApp")
        self.login_input.setText(settings.value("username", ""))
        self.password_input.setText(settings.value("password", ""))

    def go_back(self):
        self.parent_window.show()
        self.close()

    def update_queue_options(self):
        self.queue_selector.clear()
        percent = self.percent_selector.currentText()
        if percent == "20%":
            self.queue_selector.addItems([f"{i} шаг" for i in range(1, 6)])
        elif percent == "50%":
            self.queue_selector.addItems(["1 шаг", "2 шаг"])
        else:
            self.queue_selector.addItem("1 шаг")

    def on_ok(self):
        username = self.login_input.text().strip()
        password = self.password_input.text().strip()
        
        if not username or not password:
            QMessageBox.warning(self, "Внимание", "Введите логин и пароль")
            return
        
        selected_areas = [a for a, cb in self.area_checkboxes.items() if cb.isChecked()]
        if not selected_areas:
            QMessageBox.warning(self, "Внимание", "Выберите район")
            return
        
        try:
            data = self.sheets_manager.get_sheet_data(worksheet_name=self.selected_sheet)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return
        
        if data.empty:
            QMessageBox.warning(self, "Внимание", "Лист пустой")
            return
        
        if 'Район' not in data.columns:
            QMessageBox.critical(self, "Ошибка", "Нет колонки 'Район'")
            return
        
        data_filtered = data[data['Район'].isin(selected_areas)].copy()
        
        percent = self.percent_selector.currentText()
        queue = self.queue_selector.currentText()
        use_random = self.random_order_cb.isChecked()
        
        def get_slice(group):
            n = len(group)
            if percent == "100%":
                return group
            p = 0.2 if percent == "20%" else 0.5
            chunk = max(1, int(n * p))
            try:
                idx = int(queue.split()[0]) - 1
            except:
                idx = 0
            start = idx * chunk
            if (percent == "20%" and idx == 4) or (percent == "50%" and idx == 1):
                return group.iloc[start:]
            return group.iloc[start:start + chunk]
        
        filtered = data_filtered.groupby('Район', group_keys=False).apply(get_slice)
        
        if filtered.empty:
            QMessageBox.warning(self, "Внимание", "Нет данных для очереди")
            return
        
        if use_random:
            filtered = filtered.sample(frac=1, random_state=42).reset_index(drop=True)
            global selected_areas_randomized
            selected_areas_randomized = selected_areas.copy()
            random.shuffle(selected_areas_randomized)
        else:
            filtered = filtered.sort_values('Район').reset_index(drop=True)
        
        settings = QSettings("YourCompany", "YourApp")
        settings.setValue("username", username)
        settings.setValue("password", password)
        
        is_entrance = "Дворовые" in self.selected_sheet
        
        downloads = os.path.join(os.path.expanduser("~"), "Downloads")
        timestamp = datetime.now().strftime("%d.%m.%Y_%H-%M")
        safe_name = re.sub(r'[<>:"/\\|?*]', "", self.selected_sheet)
        folder_path = os.path.join(downloads, f"{safe_name}_{timestamp}")
        
        try:
            os.makedirs(folder_path, exist_ok=True)
            for area in (selected_areas_randomized if use_random else selected_areas):
                os.makedirs(os.path.join(folder_path, str(area)), exist_ok=True)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))
            return
        
        QMessageBox.information(self, "Инфо", f"📷 Камер: {len(filtered)}")
        self.start_processing(filtered, is_entrance, folder_path, username, password, use_random)

    def start_processing(self, data, is_entrance, folder_path, username, password, use_random):
        self.progress_dialog = ProgressDialog(len(data), use_random, self)
        self.progress_dialog.cancel_button.clicked.connect(self.cancel_processing)
        self.progress_dialog.show()
        
        self.processing_thread = CameraProcessingThread(
            processed_data=data, is_entrance=is_entrance, folder_path=folder_path,
            username=username, password=password, original_data=data,
            sheet_name=self.selected_sheet, sheets_manager=self.sheets_manager,
            use_random_order=use_random
        )
        
        self.processing_thread.progress_updated.connect(self.progress_dialog.update_progress)
        self.processing_thread.finished.connect(self.on_finished)
        self.processing_thread.error_occurred.connect(self.on_error)
        self.processing_thread.start()

    def cancel_processing(self):
        if hasattr(self, 'processing_thread'):
            self.processing_thread._is_cancelled = True
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()

    def on_finished(self, count, message):
        if self.progress_dialog:
            self.progress_dialog.close()
        
        missing = 0
        if hasattr(self, 'processing_thread') and hasattr(self.processing_thread, 'processor'):
            if hasattr(self.processing_thread.processor, 'missing_position_cameras'):
                missing = len(self.processing_thread.processor.missing_position_cameras)
        
        if missing > 0:
            QMessageBox.information(self, "Готово", f"{message}\n\nБез положения: {missing}")
        else:
            QMessageBox.information(self, "Готово", message)

    def on_error(self, error):
        if self.progress_dialog:
            self.progress_dialog.close()
        QMessageBox.critical(self, "Ошибка", error)
