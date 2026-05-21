"""
ECHD Camera Loader - Приложение для автоматизации загрузки камер ЕЦХД
Точка входа (PyQt6)
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication, QMessageBox
from config import APP_VERSION, LOGGING_FORMAT, LOGGING_LEVEL
from ui.main_window import MainWindow

# Настройка логирования
logging.basicConfig(level=LOGGING_LEVEL, format=LOGGING_FORMAT)


def main():
    """Точка входа в приложение"""
    app = QApplication(sys.argv)

    # Устанавливаем обработчик исключений
    sys.excepthook = lambda exctype, value, traceback: (
        QMessageBox.critical(None, "Критическая ошибка",
                             f"Произошла ошибка:\n{exctype.__name__}: {value}"),
        sys.__excepthook__(exctype, value, traceback)
    )

    try:
        mainWin = MainWindow()
        mainWin.show()
        sys.exit(app.exec())
    except Exception as e:
        QMessageBox.critical(None, "Ошибка запуска", str(e))
        sys.exit(1)


if __name__ == '__main__':
    main()
