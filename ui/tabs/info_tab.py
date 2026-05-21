"""
Вкладка справки - PyQt6
"""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QFrame
from PyQt6.QtCore import Qt
from ui.modern_styles import Colors, Typography, Spacing, Styles
from ui.components import Card, Label


class InfoTab(QWidget):
    def __init__(self, current_version):
        super().__init__()
        self.current_version = current_version
        self.initUI()

    def _section(self, title: str) -> tuple:
        """Возвращает (card, layout) с заголовком секции."""
        card = Card()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {Colors.BG_CARD};
                border: 1px solid {Colors.BORDER};
                border-radius: {Spacing.RADIUS_LG}px;
            }}
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        cl.setSpacing(Spacing.SM)

        hdr = Label(title, "subheading")
        hdr.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {Colors.PRIMARY}; background: transparent; border: none;")
        cl.addWidget(hdr)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setFixedHeight(1)
        sep.setStyleSheet(f"background-color: {Colors.BORDER};")
        cl.addWidget(sep)

        return card, cl

    def _row(self, label: str, value: str, layout):
        row = QHBoxLayout()
        lbl = Label(label)
        lbl.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_SECONDARY}; min-width: 130px; background: transparent; border: none;")
        lbl.setWordWrap(False)
        row.addWidget(lbl)
        val = Label(value)
        val.setStyleSheet(f"font-size: 13px; font-weight: 600; color: {Colors.TEXT_MAIN}; background: transparent; border: none;")
        row.addWidget(val)
        row.addStretch()
        layout.addLayout(row)

    def _feature(self, icon: str, text: str, layout):
        row = QHBoxLayout()
        row.setSpacing(Spacing.SM)
        ic = Label(icon)
        ic.setFixedWidth(24)
        ic.setStyleSheet(f"font-size: 14px; background: transparent; border: none;")
        ic.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(ic)
        txt = Label(text)
        txt.setStyleSheet(f"font-size: 13px; color: {Colors.TEXT_MAIN}; background: transparent; border: none;")
        row.addWidget(txt)
        row.addStretch()
        layout.addLayout(row)

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(Spacing.LG, Spacing.LG, Spacing.LG, Spacing.LG)
        layout.setSpacing(Spacing.MD)

        # --- Заголовок ---
        hdr = Label("О приложении", "subheading")
        hdr.setStyleSheet(f"font-size: 18px; font-weight: 700; color: {Colors.TEXT_MAIN};")
        layout.addWidget(hdr)

        # --- Карточка версии ---
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
        ver_layout.setContentsMargins(Spacing.LG, Spacing.MD, Spacing.LG, Spacing.MD)

        info_col = QVBoxLayout()
        info_col.setSpacing(2)
        app_name = Label("ЕЦХД Камеры")
        app_name.setStyleSheet(f"font-size: 20px; font-weight: 800; color: {Colors.PRIMARY}; background: transparent; border: none;")
        info_col.addWidget(app_name)
        desc = Label("Автоматизация загрузки снимков из системы ЕЦХД")
        desc.setStyleSheet(f"font-size: 12px; color: {Colors.TEXT_SECONDARY}; background: transparent; border: none;")
        info_col.addWidget(desc)
        ver_layout.addLayout(info_col)
        ver_layout.addStretch()

        ver_badge = Label(f"v{self.current_version}")
        ver_badge.setStyleSheet(f"""
            font-size: 14px; font-weight: 700; color: white;
            background-color: {Colors.PRIMARY}; border: none;
            border-radius: 12px; padding: 6px 14px;
        """)
        ver_layout.addWidget(ver_badge, alignment=Qt.AlignmentFlag.AlignVCenter)

        layout.addWidget(ver_card)

        # --- Возможности + Технологии в ряд ---
        two_col = QHBoxLayout()
        two_col.setSpacing(Spacing.MD)

        # Возможности
        feat_card, feat_layout = self._section("Возможности")
        for icon, text in (
            ("📊", "Загрузка данных из Google Таблицы"),
            ("📷", "Автоматическое создание снимков"),
            ("📍", "Фильтрация по районам"),
            ("⏰", "Отложенный запуск"),
            ("📁", "Переименование файлов по адресам"),
            ("🔄", "Повторная обработка проблемных камер"),
        ):
            self._feature(icon, text, feat_layout)
        two_col.addWidget(feat_card, 1)

        # Как пользоваться
        how_card, how_layout = self._section("Как пользоваться")
        for icon, text in (
            ("1️⃣", "Загрузите листы Google Таблицы"),
            ("2️⃣", "Выберите нужный лист"),
            ("3️⃣", "Настройте параметры и районы"),
            ("4️⃣", "Нажмите «Запустить обработку»"),
            ("5️⃣", "Дождитесь завершения"),
        ):
            self._feature(icon, text, how_layout)
        two_col.addWidget(how_card, 1)

        layout.addLayout(two_col)

        # --- Системная информация ---
        sys_card, sys_layout = self._section("Системная информация")
        self._row("Версия:", f"v{self.current_version}", sys_layout)
        self._row("Платформа:", "Windows (PyQt6 + Selenium)", sys_layout)
        self._row("Авторы:", "tel9 & GNAVA4", sys_layout)
        layout.addWidget(sys_card)

        layout.addStretch()
