"""
Поток для загрузки листов из Google Sheets
"""
import logging
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)


class LoadSheetsThread(QThread):
    """Поток для загрузки листов из Google Sheets"""
    loaded = pyqtSignal(list)
    error = pyqtSignal(str)

    def __init__(self, sheets_manager):
        super().__init__()
        self.sheets_manager = sheets_manager

    def run(self):
        try:
            sheets = self.sheets_manager.get_worksheets()
            self.loaded.emit(sheets)
        except Exception as e:
            logger.error(f"Ошибка загрузки листов: {e}")
            self.error.emit(str(e))
