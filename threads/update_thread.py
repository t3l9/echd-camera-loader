"""
Поток проверки обновлений
"""
import logging
from PyQt6.QtCore import QThread, pyqtSignal

logger = logging.getLogger(__name__)


class UpdateCheckThread(QThread):
    update_found = pyqtSignal(dict)
    no_update = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, update_manager):
        super().__init__()
        self.update_manager = update_manager

    def run(self):
        try:
            update_info = self.update_manager.check_for_updates()
            if update_info['available']:
                self.update_found.emit(update_info)
            else:
                self.no_update.emit()
        except Exception as e:
            logger.error(f"Ошибка в потоке проверки обновлений: {e}")
            self.error.emit(str(e))
