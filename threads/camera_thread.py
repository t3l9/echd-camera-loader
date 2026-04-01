"""
Поток обработки камер
"""
import os
import time
import logging
import pandas as pd
from PyQt6.QtCore import QThread, pyqtSignal

from config import downloads_folder
from core.camera_processor import CameraProcessor
from utils.helpers import clean_filename

logger = logging.getLogger(__name__)


class CameraProcessingThread(QThread):
    progress_updated = pyqtSignal(int, int, str)
    finished = pyqtSignal(int, str)
    error_occurred = pyqtSignal(str)

    def __init__(self, processed_data, is_entrance, folder_path, username, password,
                 original_data, sheet_name, sheets_manager, use_random_order=False):
        super().__init__()

        self.processed_data = processed_data
        self.is_entrance = is_entrance
        self.folder_path = folder_path
        self.username = username
        self.password = password
        self.original_data = original_data
        self.sheet_name = sheet_name
        self.sheets_manager = sheets_manager
        self.use_random_order = use_random_order
        self.driver = None
        self._is_cancelled = False
        self.processor = None

    def run(self):
        total = len(self.processed_data)
        processed_count = 0
        failed_rows = []

        try:
            # Информируем о начале обработки
            logger.info(f"Начинаем обработку {total} камер")

            # Создаем процессор
            processor = CameraProcessor(
                username=self.username,
                password=self.password
            )
            self.processor = processor

            # Инициализируем драйвер ПЕРЕД использованием
            if not processor._initialize_driver():
                self.error_occurred.emit("Не удалось инициализировать драйвер Chrome")
                return

            # Авторизуемся ОДИН РАЗ
            self.progress_updated.emit(0, total, f"Авторизация... (всего камер: {total})")
            if not processor._login_to_site():
                self.error_occurred.emit("Ошибка авторизации на сайте")
                return

            # === ДОПОЛНИТЕЛЬНО: НАСТРАИВАЕМ РАЗРЕШЕНИЯ ЕЩЕ РАЗ ===
            self.progress_updated.emit(0, total, "Настройка медиа-разрешений...")
            if hasattr(processor, '_setup_media_permissions'):
                processor._setup_media_permissions()

            # Закрываем уведомления
            self.progress_updated.emit(0, total, "Настройка интерфейса...")
            processor._handle_notifications()

            # Настраиваем интерфейс
            processor._setup_interface()

            # ===== ОСНОВНАЯ ОБРАБОТКА =====
            for index, row in self.processed_data.iterrows():
                if self._is_cancelled:
                    break

                camera_id = row.get('Номер камеры', 'Unknown')
                address = row.get('Адрес', None)

                # Логируем информацию об адресе
                if address and not pd.isna(address):
                    clean_addr = clean_filename(str(address))
                    status_msg = f"Камера: {camera_id}\nАдрес: {clean_addr}"
                else:
                    status_msg = f"Камера: {camera_id}\n(адрес не указан)"

                self.progress_updated.emit(processed_count, total, status_msg)

                # Дополнительная проверка
                if address and not pd.isna(address):
                    logger.info(
                        f"Обработка камеры {camera_id} -> будет сохранена как: {clean_filename(str(address))}.jpg")

                success = processor.fast_process_single_camera(
                    row=row,
                    is_entrance=self.is_entrance,
                    folder_path=self.folder_path
                )

                if not success:
                    failed_rows.append(row)
                    logger.warning(f"Проблема с камерой {camera_id} по адресу: {address}")

                processed_count += 1
                self.progress_updated.emit(processed_count, total, f"Обработано: {processed_count}/{total}")

            # ===== RETRY ПРОХОД =====
            if failed_rows and not self._is_cancelled:
                self.progress_updated.emit(processed_count, total, "Повторная обработка проблемных камер...")
                time.sleep(2)

                for row in failed_rows.copy():
                    if self._is_cancelled:
                        break

                    success = processor.fast_process_single_camera(
                        row=row,
                        is_entrance=self.is_entrance,
                        folder_path=self.folder_path
                    )

                    if success:
                        failed_rows.remove(row)

            # ===== СОХРАНЕНИЕ РЕЗУЛЬТАТОВ =====
            if not self._is_cancelled:
                self._save_results(failed_rows, self.folder_path)

            # Закрываем драйвер
            if processor.driver:
                try:
                    processor.driver.quit()
                except:
                    pass

            if self._is_cancelled:
                self.finished.emit(0, "Обработка отменена пользователем")
            else:
                problematic_count = len(failed_rows)
                if problematic_count > 0:
                    self.finished.emit(problematic_count,
                                       f"Обработка завершена. Проблемных камер: {problematic_count}")
                else:
                    self.finished.emit(0, "Обработка успешно завершена!")

        except Exception as e:
            logger.error(f"Ошибка в потоке обработки: {e}")
            self.error_occurred.emit(str(e))
            self.finished.emit(0, f"Ошибка обработки: {str(e)}")
        finally:
            # Гарантируем закрытие драйвера
            if processor and processor.driver:
                try:
                    processor.driver.quit()
                except:
                    pass

    def _save_results(self, failed_rows, folder_path):
        """Сохранение результатов обработки - все проблемные камеры в один файл"""
        try:
            all_problematic = []
            
            # Собираем камеры без положения
            if hasattr(self.processor, 'missing_position_cameras') and self.processor.missing_position_cameras:
                for camera in self.processor.missing_position_cameras:
                    camera_record = {
                        'Тип проблемы': 'Без положения',
                        'Район': camera.get('Район', ''),
                        'Адрес': camera.get('Адрес', ''),
                        'Номер камеры': camera.get('Номер камеры', ''),
                        'Положение': camera.get('Положение', ''),
                        'Ошибка': camera.get('Ошибка', '')
                    }
                    all_problematic.append(camera_record)
                logger.info(f"Добавлено камер без положения: {len(self.processor.missing_position_cameras)}")

            # Собираем проблемные камеры (не выгруженные)
            if failed_rows:
                for row in failed_rows:
                    if hasattr(row, 'to_dict'):
                        row_dict = row.to_dict()
                    else:
                        row_dict = row
                    
                    camera_record = {
                        'Тип проблемы': 'Не выгружена',
                        'Район': row_dict.get('Район', ''),
                        'Адрес': row_dict.get('Адрес', ''),
                        'Номер камеры': row_dict.get('Номер камеры', ''),
                        'Положение': row_dict.get('Положение', ''),
                        'Ошибка': 'Не удалось выгрузить'
                    }
                    all_problematic.append(camera_record)
                logger.info(f"Добавлено не выгруженных камер: {len(failed_rows)}")

            # Сохраняем всё в один файл
            if all_problematic:
                problematic_df = pd.DataFrame(all_problematic)
                problematic_file_path = os.path.join(folder_path, "ПРОБЛЕМНЫЕ_КАМЕРЫ.xlsx")
                problematic_df.to_excel(problematic_file_path, index=False)
                logger.info(f"✅ Сохранено проблемных камер: {len(all_problematic)} в файл {problematic_file_path}")
            else:
                logger.info("✅ Проблемных камер нет")

        except Exception as e:
            logger.error(f"Ошибка сохранения результатов: {e}")

    def cancel(self):
        """Отмена обработки"""
        self._is_cancelled = True
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
