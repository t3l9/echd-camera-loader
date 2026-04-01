"""
Конфигурация приложения ECHD Camera Loader
"""
import os
import logging
from dotenv import load_dotenv

# Загрузка переменных окружения из .env файла
load_dotenv()


# ===== ВЕРСИЯ ПРИЛОЖЕНИЯ =====
APP_VERSION = os.getenv('APP_VERSION', '9.3.0')


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
