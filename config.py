"""
Конфигурация приложения ECHD Camera Loader
"""
import sys
import os
import logging
from dotenv import load_dotenv

# Определяем путь к директории приложения (для работы из exe и из исходников)
if getattr(sys, 'frozen', False):
    # Запущено из PyInstaller exe
    application_path = os.path.dirname(sys.executable)
else:
    # Запущено из исходников Python
    application_path = os.path.dirname(os.path.abspath(__file__))

# Загрузка переменных окружения из .env файла
# Ищем .env в нескольких местах (по порядку):
# 1. Рядом с exe файлом (для packaged версии)
# 2. В текущей рабочей директории (для запуска из любой папки)
# 3. Рядом с config.py (для разработки)
env_paths_to_try = [
    os.path.join(application_path, '.env'),  # рядом с exe
    os.path.join(os.getcwd(), '.env'),        # в текущей директории
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'),  # рядом с config.py
]

env_loaded = False
for env_path in env_paths_to_try:
    if os.path.exists(env_path):
        load_dotenv(env_path, override=True)
        env_loaded = True
        break

if not env_loaded:
    # Тихое предупреждение в лог (не блокирующее)
    import warnings
    warnings.warn(
        f"Файл .env не найден в ожидаемых путях:\n" +
        "\n".join(f"  - {p}" for p in env_paths_to_try) +
        "\nПриложение будет использовать значения по умолчанию."
    )


# ===== ВЕРСИЯ ПРИЛОЖЕНИЯ =====
APP_VERSION = os.getenv('APP_VERSION', '9.4.2')


# ===== РАЙОНЫ =====
areas = [
    "Выхино-Жулебино", "Капотня", "Кузьминки", "Лефортово", "Люблино",
    "Марьино", "Некрасовка", "Нижегородский", "Печатники",
    "Рязанский", "Текстильщики", "Южнопортовый"
]


# ===== URL САЙТА =====
url = os.getenv('ECHD_URL', 'https://echd.mos.ru/login/auth/')


# ===== ПАПКА ЗАГРУЗОК =====
downloads_folder = os.path.join(os.path.expanduser('~'), 'Downloads')


# ===== GOOGLE SHEETS =====
GOOGLE_SHEETS_URL = os.getenv('GOOGLE_SHEETS_URL')
SCOPES = [os.getenv('GOOGLE_SCOPES', 'https://www.googleapis.com/auth/spreadsheets')]

SERVICE_ACCOUNT_INFO = {
    "type": os.getenv('GOOGLE_SERVICE_ACCOUNT_TYPE', 'service_account'),
    "project_id": os.getenv('GOOGLE_SERVICE_ACCOUNT_PROJECT_ID'),
    "private_key_id": os.getenv('GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY_ID'),
    "private_key": os.getenv('GOOGLE_SERVICE_ACCOUNT_PRIVATE_KEY', '').replace('\\n', '\n'),
    "client_email": os.getenv('GOOGLE_SERVICE_ACCOUNT_CLIENT_EMAIL'),
    "client_id": os.getenv('GOOGLE_SERVICE_ACCOUNT_CLIENT_ID'),
    "auth_uri": os.getenv('GOOGLE_SERVICE_ACCOUNT_AUTH_URI'),
    "token_uri": os.getenv('GOOGLE_SERVICE_ACCOUNT_TOKEN_URI'),
    "auth_provider_x509_cert_url": os.getenv('GOOGLE_SERVICE_ACCOUNT_AUTH_PROVIDER_URL'),
    "client_x509_cert_url": os.getenv('GOOGLE_SERVICE_ACCOUNT_CERT_URL'),
    "universe_domain": os.getenv('GOOGLE_SERVICE_ACCOUNT_UNIVERSE_DOMAIN', 'googleapis.com')
}


# ===== НАСТРОЙКИ ЛОГИРОВАНИЯ =====
LOGGING_FORMAT = '%(asctime)s - %(levelname)s - %(message)s'
LOGGING_LEVEL = getattr(logging, os.getenv('LOGGING_LEVEL', 'INFO'))
