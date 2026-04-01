"""
Менеджер обновлений приложения
Проверка новых версий на GitHub
"""
import logging
import json
import requests
from packaging import version

from config import APP_VERSION

logger = logging.getLogger(__name__)


class UpdateManager:
    def __init__(self, current_version):
        self.current_version = current_version
        self.repo_url = "https://api.github.com/repos/t3l9/echd-camera-loader/releases/latest"
        self.headers = {
            'User-Agent': f'EchdCameraLoader/{current_version}',
            'Accept': 'application/vnd.github.v3+json'
        }

    def check_for_updates(self):
        """Проверяет наличие обновлений на GitHub"""
        try:
            logging.info(f"Проверка обновлений: {self.repo_url}")

            response = requests.get(self.repo_url, headers=self.headers, timeout=10)
            logging.info(f"Статус ответа GitHub: {response.status_code}")

            if response.status_code == 200:
                try:
                    release_info = response.json()
                    logging.info(f"Получен релиз: {release_info.get('tag_name', 'No tag')}")

                    # Извлекаем версию из тега
                    tag_name = release_info.get('tag_name', '')
                    if tag_name.startswith('v'):
                        latest_version = tag_name[1:]  # Убираем 'v'
                    else:
                        latest_version = tag_name

                    logging.info(f"Текущая версия: {self.current_version}, Доступная: {latest_version}")

                    # Сравниваем версии
                    if version.parse(latest_version) > version.parse(self.current_version):
                        return {
                            'available': True,
                            'latest_version': latest_version,
                            'release_notes': release_info.get('body', ''),
                            'release_info': release_info
                        }
                    else:
                        logging.info("Установлена актуальная версия")

                except json.JSONDecodeError as e:
                    logging.error(f"Ошибка парсинга JSON: {e}")
                    logging.error(f"Ответ сервера: {response.text[:200]}")

            elif response.status_code == 404:
                logging.warning("Релизы не найдены (404)")
            elif response.status_code == 403:
                logging.warning("Доступ запрещен (403)")
            else:
                logging.warning(f"Неожиданный статус: {response.status_code}")

        except Exception as e:
            logging.error(f"Ошибка проверки обновлений: {e}", exc_info=True)

        return {'available': False}
