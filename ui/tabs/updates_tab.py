"""
Вкладка обновлений - PyQt6
"""
import webbrowser
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, Card, Label


class UpdatesTab(QWidget):
    def __init__(self, update_manager):
        super().__init__()
        self.update_manager = update_manager
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        layout.addWidget(Label("🔄 Обновления", "subheading"))
        
        # Текущая версия
        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        card_layout.setSpacing(Spacing.SM)
        
        card_layout.addWidget(Label("Текущая версия:", "subheading"))
        self.version_label = Label(f"v{self.update_manager.current_version}", "primary")
        self.version_label.setStyleSheet(f"font-size: {Typography.SIZE_XL}px; font-weight: 600; color: {Colors.PRIMARY};")
        card_layout.addWidget(self.version_label)
        
        layout.addWidget(card)
        
        # Кнопка
        self.check_btn = Button("🔍 Проверить обновления", variant="primary")
        self.check_btn.setFixedHeight(48)
        self.check_btn.clicked.connect(self.check_updates)
        layout.addWidget(self.check_btn)
        
        # Статус
        self.status_label = Label("", "muted")
        layout.addWidget(self.status_label)
        
        # Обновление
        self.update_card = Card()
        update_layout = QVBoxLayout(self.update_card)
        update_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        update_layout.setSpacing(Spacing.SM)
        
        self.new_version_label = Label("", "subheading")
        update_layout.addWidget(self.new_version_label)
        
        self.notes_label = Label("", "muted")
        self.notes_label.setWordWrap(True)
        update_layout.addWidget(self.notes_label)
        
        self.github_btn = Button("📥 Перейти на GitHub", variant="primary")
        self.github_btn.clicked.connect(self.open_github)
        update_layout.addWidget(self.github_btn)
        
        self.update_card.hide()
        layout.addWidget(self.update_card)
        
        layout.addStretch()
        
        self.github_url = "https://github.com/t3l9/echd-camera-loader/releases/latest"

    def check_updates(self):
        self.check_btn.setEnabled(False)
        self.status_label.setText("Проверка...")
        
        try:
            info = self.update_manager.check_for_updates()
            
            if info['available']:
                self.status_label.setText("")
                self.new_version_label.setText(f"🎉 Версия {info['latest_version']} доступна")
                
                notes = info.get('release_notes', '')[:400]
                self.notes_label.setText(notes + "..." if len(notes) >= 400 else notes)
                
                self.update_card.show()
            else:
                self.status_label.setText("✅ Установлена актуальная версия")
        except Exception as e:
            self.status_label.setText(f"❌ Ошибка: {str(e)[:50]}")
        
        self.check_btn.setEnabled(True)

    def open_github(self):
        webbrowser.open(self.github_url)
        self.status_label.setText("✅ Открыто в браузере")
