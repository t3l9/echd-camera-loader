"""
Вкладка справки - PyQt6
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Button, Card, Label


class InfoTab(QWidget):
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)
        
        layout.addWidget(Label("ℹ️ Справка", "subheading"))
        
        # О приложении
        card = Card()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        card_layout.setSpacing(Spacing.SM)
        
        card_layout.addWidget(Label(f"Версия: {self.current_version}"))
        card_layout.addWidget(Label("Приложение для автоматизации загрузки камер ЕЦХД"))
        
        layout.addWidget(card)
        
        # Возможности
        features_card = Card()
        features_layout = QVBoxLayout(features_card)
        features_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        features_layout.setSpacing(Spacing.XS)
        
        features_layout.addWidget(Label("Возможности:", "subheading"))
        features = [
            "• Работа с Google Sheets",
            "• Автоматизация загрузки",
            "• Обработка по районам",
            "• Отложенный запуск",
            "• Переименование по адресам"
        ]
        for f in features:
            features_layout.addWidget(Label(f, "muted"))
        
        layout.addWidget(features_card)
        
        # Авторы
        authors_card = Card()
        authors_layout = QVBoxLayout(authors_card)
        authors_layout.setContentsMargins(Spacing.MD, Spacing.MD, Spacing.MD, Spacing.MD)
        authors_layout.addWidget(Label("Created by tel9 & GNAVA4", "muted"))
        
        layout.addWidget(authors_card)
        
        layout.addStretch()
