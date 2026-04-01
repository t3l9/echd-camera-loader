"""
Современная система стилей - бело-фиолетовая гамма
PyQt6 compatible
"""

class Colors:
    """Гармоничная бело-фиолетовая палитра"""
    # Основные фиолетовые
    PRIMARY = "#7C3AED"        # Яркий фиолетовый
    PRIMARY_LIGHT = "#8B5CF6"  # Светлый фиолетовый
    PRIMARY_DARK = "#6D28D9"   # Тёмный фиолетовый
    PRIMARY_PALE = "#EDE9FE"   # Бледный фиолетовый (фон акцентов)
    
    # Белые и нейтральные
    WHITE = "#FFFFFF"
    BG_MAIN = "#F9FAFB"        # Очень светлый серый фон
    BG_CARD = "#FFFFFF"        # Белый для карточек
    BG_HOVER = "#F3F4F6"       # Светлый серый для hover
    
    # Текст
    TEXT_MAIN = "#1F2937"      # Тёмный серый текст
    TEXT_SECONDARY = "#6B7280" # Серый текст
    TEXT_MUTED = "#9CA3AF"     # Приглушённый текст
    TEXT_ON_PRIMARY = "#FFFFFF" # Белый на фиолетовом
    
    # Границы
    BORDER = "#E5E7EB"         # Светлая граница
    BORDER_FOCUS = "#7C3AED"   # Фиолетовый фокус
    
    # Статусы
    SUCCESS = "#10B981"
    WARNING = "#F59E0B"
    ERROR = "#EF4444"
    INFO = "#3B82F6"


class Typography:
    """Современная типографика"""
    FONT_FAMILY = "Segoe UI, Roboto, Helvetica, Arial, sans-serif"
    
    SIZE_XS = 11
    SIZE_SM = 12
    SIZE_BASE = 14
    SIZE_LG = 16
    SIZE_XL = 20
    SIZE_2XL = 26
    
    WEIGHT_NORMAL = 400
    WEIGHT_MEDIUM = 500
    WEIGHT_SEMI = 600
    WEIGHT_BOLD = 700


class Spacing:
    """Единая система отступов"""
    XS = 4
    SM = 8
    MD = 12
    LG = 16
    XL = 24
    XXL = 32
    
    RADIUS_SM = 6
    RADIUS_MD = 10
    RADIUS_LG = 14


class Styles:
    """Готовые стили компонентов"""
    
    MAIN_WINDOW = f"""
        QWidget {{
            background-color: {Colors.BG_MAIN};
            color: {Colors.TEXT_MAIN};
            font-family: {Typography.FONT_FAMILY};
            font-size: {Typography.SIZE_BASE}px;
        }}
    """
    
    BUTTON_PRIMARY = f"""
        QPushButton {{
            background-color: {Colors.PRIMARY};
            color: {Colors.TEXT_ON_PRIMARY};
            border: none;
            border-radius: {Spacing.RADIUS_MD}px;
            padding: 12px 24px;
            font-size: {Typography.SIZE_BASE}px;
            font-weight: {Typography.WEIGHT_SEMI};
        }}
        QPushButton:hover {{
            background-color: {Colors.PRIMARY_DARK};
        }}
        QPushButton:pressed {{
            background-color: {Colors.PRIMARY_DARK};
        }}
        QPushButton:disabled {{
            background-color: {Colors.BORDER};
            color: {Colors.TEXT_MUTED};
        }}
    """
    
    BUTTON_SECONDARY = f"""
        QPushButton {{
            background-color: {Colors.WHITE};
            color: {Colors.TEXT_MAIN};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.RADIUS_MD}px;
            padding: 12px 24px;
            font-size: {Typography.SIZE_BASE}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
        }}
        QPushButton:hover {{
            border-color: {Colors.PRIMARY};
            color: {Colors.PRIMARY};
            background-color: {Colors.PRIMARY_PALE};
        }}
    """
    
    BUTTON_GHOST = f"""
        QPushButton {{
            background-color: transparent;
            color: {Colors.TEXT_SECONDARY};
            border: none;
            border-radius: {Spacing.RADIUS_MD}px;
            padding: 8px 16px;
            font-size: {Typography.SIZE_SM}px;
        }}
        QPushButton:hover {{
            background-color: {Colors.BG_HOVER};
            color: {Colors.PRIMARY};
        }}
    """
    
    INPUT = f"""
        QLineEdit, QComboBox {{
            background-color: {Colors.WHITE};
            color: {Colors.TEXT_MAIN};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.RADIUS_MD}px;
            padding: 11px 14px;
            font-size: {Typography.SIZE_BASE}px;
        }}
        QLineEdit:focus, QComboBox:focus {{
            border: 2px solid {Colors.PRIMARY};
            padding: 10px 13px;
        }}
        QLineEdit:hover, QComboBox:hover {{
            border-color: {Colors.PRIMARY_LIGHT};
        }}
        QLineEdit::placeholder {{
            color: {Colors.TEXT_MUTED};
        }}
        QComboBox::drop-down {{
            border: none;
            padding-right: 12px;
        }}
        QComboBox::down-arrow {{
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 6px solid {Colors.TEXT_SECONDARY};
            margin-right: 12px;
        }}
        QComboBox QAbstractItemView {{
            background-color: {Colors.WHITE};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.RADIUS_MD}px;
            selection-background-color: {Colors.PRIMARY_PALE};
            color: {Colors.TEXT_MAIN};
            outline: none;
            padding: 4px;
        }}
        QComboBox QAbstractItemView::item {{
            min-height: 40px;
            padding: 8px 12px;
            border-radius: {Spacing.RADIUS_SM}px;
        }}
        QComboBox QAbstractItemView::item:hover {{
            background-color: {Colors.BG_HOVER};
        }}
        QComboBox QAbstractItemView::item:selected {{
            background-color: {Colors.PRIMARY_PALE};
            color: {Colors.PRIMARY_DARK};
        }}
    """
    
    CARD = f"""
        QFrame, QWidget#cardWidget {{
            background-color: {Colors.BG_CARD};
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.RADIUS_LG}px;
        }}
    """
    
    CARD_ELEVATED = f"""
        QFrame, QWidget#cardWidget {{
            background-color: {Colors.BG_CARD};
            border: none;
            border-radius: {Spacing.RADIUS_LG}px;
        }}
    """
    
    SCROLLBAR = f"""
        QScrollArea {{
            border: none;
            background: transparent;
        }}
        QScrollBar:vertical {{
            background: transparent;
            width: 8px;
        }}
        QScrollBar::handle:vertical {{
            background: {Colors.BORDER};
            border-radius: 4px;
            min-height: 30px;
        }}
        QScrollBar::handle:vertical:hover {{
            background: {Colors.TEXT_MUTED};
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
    """
    
    TAB = f"""
        QTabWidget::pane {{
            border: 1px solid {Colors.BORDER};
            border-radius: {Spacing.RADIUS_LG}px;
            background-color: {Colors.BG_CARD};
        }}
        QTabBar::tab {{
            background-color: transparent;
            color: {Colors.TEXT_SECONDARY};
            padding: 14px 28px;
            font-size: {Typography.SIZE_BASE}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
            border: none;
            border-bottom: 2px solid transparent;
            margin-right: 4px;
        }}
        QTabBar::tab:selected {{
            color: {Colors.PRIMARY};
            border-bottom-color: {Colors.PRIMARY};
            font-weight: {Typography.WEIGHT_SEMI};
        }}
        QTabBar::tab:hover {{
            color: {Colors.TEXT_MAIN};
        }}
    """
    
    PROGRESS = f"""
        QProgressBar {{
            border: none;
            border-radius: {Spacing.RADIUS_SM}px;
            text-align: center;
            background-color: {Colors.BG_HOVER};
            color: {Colors.TEXT_SECONDARY};
            font-size: {Typography.SIZE_XS}px;
            height: 8px;
        }}
        QProgressBar::chunk {{
            background-color: {Colors.PRIMARY};
            border-radius: {Spacing.RADIUS_SM}px;
        }}
    """
    
    CHECKBOX = f"""
        QCheckBox {{
            color: {Colors.TEXT_MAIN};
            spacing: 10px;
            font-size: {Typography.SIZE_BASE}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
        }}
        QCheckBox::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 5px;
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
    """
    
    RADIO = f"""
        QRadioButton {{
            color: {Colors.TEXT_MAIN};
            spacing: 10px;
            font-size: {Typography.SIZE_BASE}px;
            font-weight: {Typography.WEIGHT_MEDIUM};
        }}
        QRadioButton::indicator {{
            width: 20px;
            height: 20px;
            border-radius: 10px;
            border: 2px solid {Colors.BORDER};
            background: {Colors.WHITE};
        }}
        QRadioButton::indicator:hover {{
            border-color: {Colors.PRIMARY};
        }}
        QRadioButton::indicator:checked {{
            background: {Colors.PRIMARY};
            border: 5px solid {Colors.PRIMARY};
        }}
    """
    
    LABEL_HEADING = f"""
        color: {Colors.TEXT_MAIN};
        font-size: {Typography.SIZE_2XL}px;
        font-weight: {Typography.WEIGHT_BOLD};
    """
    
    LABEL_SUBHEADING = f"""
        color: {Colors.TEXT_MAIN};
        font-size: {Typography.SIZE_XL}px;
        font-weight: {Typography.WEIGHT_SEMI};
    """
    
    LABEL_BODY = f"""
        color: {Colors.TEXT_MAIN};
        font-size: {Typography.SIZE_BASE}px;
        line-height: 1.6;
    """
    
    LABEL_MUTED = f"""
        color: {Colors.TEXT_SECONDARY};
        font-size: {Typography.SIZE_SM}px;
    """
    
    LABEL_PRIMARY = f"""
        color: {Colors.PRIMARY};
        font-size: {Typography.SIZE_BASE}px;
        font-weight: {Typography.WEIGHT_SEMI};
    """
