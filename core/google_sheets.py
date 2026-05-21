"""
Менеджер для работы с Google Sheets API
"""
import logging
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials

from config import SERVICE_ACCOUNT_INFO, SCOPES, GOOGLE_SHEETS_URL

logger = logging.getLogger(__name__)


class GoogleSheetsManager:
    def __init__(self):
        self.client = None
        self._authenticated = False

    def authenticate(self):
        """Аутентификация в Google Sheets API с интегрированным ключом"""
        if self._authenticated and self.client:
            return True

        try:
            creds = Credentials.from_service_account_info(SERVICE_ACCOUNT_INFO, scopes=SCOPES)
            self.client = gspread.authorize(creds)
            self._authenticated = True
            logger.info("Успешная аутентификация в Google Sheets API")
            return True
        except Exception as e:
            logger.error(f"Ошибка аутентификации Google Sheets: {e}")
            self._authenticated = False
            return False

    def get_worksheets(self, spreadsheet_url_or_id=None):
        """Получение списка всех листов в таблице"""
        if not self.client or not self._authenticated:
            if not self.authenticate():
                raise Exception("Не удалось аутентифицироваться в Google Sheets API")

        try:
            if spreadsheet_url_or_id is None:
                spreadsheet_url_or_id = GOOGLE_SHEETS_URL

            spreadsheet = self.client.open_by_url(
                spreadsheet_url_or_id) if 'http' in spreadsheet_url_or_id else self.client.open_by_key(
                spreadsheet_url_or_id)

            worksheets = spreadsheet.worksheets()
            worksheet_names = [ws.title for ws in worksheets]

            logger.info(f"Найдены листы: {worksheet_names}")
            return worksheet_names

        except Exception as e:
            logger.error(f"Ошибка получения листов из Google Sheets: {e}")
            raise

    def get_sheet_data(self, spreadsheet_url_or_id=None, worksheet_name=None):
        """Получение данных из указанного листа"""
        if not self.client:
            if not self.authenticate():
                raise Exception("Не удалось аутентифицироваться в Google Sheets API")
        if not worksheet_name:
            raise ValueError("Имя листа не передано (worksheet_name=None)")
        try:
            if spreadsheet_url_or_id is None:
                spreadsheet_url_or_id = GOOGLE_SHEETS_URL
            spreadsheet = (
                self.client.open_by_url(spreadsheet_url_or_id)
                if "http" in spreadsheet_url_or_id
                else self.client.open_by_key(spreadsheet_url_or_id)
            )
            worksheet = spreadsheet.worksheet(worksheet_name)
            data = worksheet.get_all_records()
            return pd.DataFrame(data)
        except Exception as e:
            logger.error(f"Ошибка чтения листа '{worksheet_name}': {e}")
            raise
