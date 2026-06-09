"""
Утилиты для работы с файлами: проверка загрузки, перемещение, переименование
"""
import os
import time
import shutil
import logging
import pandas as pd

from config import downloads_folder
from utils.helpers import clean_filename

logger = logging.getLogger(__name__)


def is_file_downloaded(camera_id):
    """Проверяет, загружен ли файл с указанным префиксом camera_id (без учета регистра)"""
    try:
        files = os.listdir(downloads_folder)

        # Создаем базовый ID без учета регистра
        camera_id_lower = camera_id.lower()

        for file in files:
            file_lower = file.lower()

            # Проверяем, начинается ли имя файла с ID камеры (без учета регистра)
            if file_lower.startswith(camera_id_lower):
                file_path = os.path.join(downloads_folder, file)

                if os.path.exists(file_path):
                    # Проверка стабильности размера
                    size1 = os.path.getsize(file_path)
                    time.sleep(0.3)
                    size2 = os.path.getsize(file_path)

                    if size2 > 0 and size1 == size2:
                        logger.info(f"✅ Найден готовый файл: {file} ({size2} bytes)")
                        return True
                    elif size2 > 0:
                        logger.info(f"⏳ Файл еще пишется: {file} ({size1} -> {size2})")

        return False
    except Exception as e:
        logger.error(f"Ошибка при проверке загруженных файлов: {e}")
        return False


def move_and_rename_last_downloaded_file(destination, camera_id=None, address=None):
    """Перемещает и переименовывает файл по ID камеры (без учета регистра)"""
    try:
        files = [f for f in os.listdir(downloads_folder)
                 if os.path.isfile(os.path.join(downloads_folder, f))]

        if not files:
            logger.warning("Нет загруженных файлов")
            return None

        # Ищем файл по ID камеры (без учета регистра)
        target_file = None
        if camera_id:
            camera_id_lower = camera_id.lower()
            for file in files:
                if file.lower().startswith(camera_id_lower):
                    target_file = file
                    logger.info(f"Найден файл по ID камеры: {file}")
                    break

        # Если не нашли - берем последний
        if not target_file:
            files.sort(key=lambda x: os.path.getctime(os.path.join(downloads_folder, x)), reverse=True)
            target_file = files[0]
            logger.info(f"Взяли последний файл: {target_file}")

        old_file_path = os.path.join(downloads_folder, target_file)

        # Ждем стабильности файла
        time.sleep(0.5)  # Даем время на завершение записи

        # Определяем расширение
        file_extension = os.path.splitext(target_file)[1]

        # Новое имя
        if address and not pd.isna(address):
            clean_address = clean_filename(str(address))
            new_filename = f"{clean_address}{file_extension}"
        else:
            new_filename = target_file

        new_file_path = os.path.join(destination, new_filename)

        # Обработка дубликатов
        counter = 1
        while os.path.exists(new_file_path):
            name_without_ext = os.path.splitext(new_filename)[0]
            new_filename = f"{name_without_ext} ({counter}){file_extension}"
            new_file_path = os.path.join(destination, new_filename)
            counter += 1

        # Перемещаем
        shutil.move(old_file_path, new_file_path)
        logger.info(f"✅ Файл сохранен как: {new_filename}")
        return new_filename

    except Exception as e:
        logger.error(f"❌ Ошибка при перемещении файла: {e}")
        return None
