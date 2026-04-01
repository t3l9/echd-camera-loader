"""
Вспомогательные функции для работы с адресами и именами файлов
"""
import re
import pandas as pd


def format_address_for_filename(address):
    """Форматирует адрес для использования в имени файла"""
    if pd.isna(address):
        return "Без адреса"

    addr_str = str(address)

    # Убираем кавычки и лишние знаки препинания
    addr_str = addr_str.replace('"', '').replace("'", "")

    # Заменяем тире на обычное (для единообразия)
    addr_str = addr_str.replace('–', '-').replace('—', '-')

    # Убираем точки после сокращений (ул., д., кв. и т.д.)
    addr_str = re.sub(r'(\bул|\bд|\bкв|\bк|)\.', r'\1', addr_str)

    # Очищаем от недопустимых символов
    addr_str = re.sub(r'[<>:"/\\|?*]', '', addr_str)

    # Убираем лишние пробелы
    addr_str = re.sub(r'\s+', ' ', addr_str).strip()

    # Если строка пустая после очистки
    if not addr_str:
        return "Без адреса"

    return addr_str[:150]


def clean_filename(name):
    """Очищает строку для использования в имени файла, сохраняя читаемость"""
    return format_address_for_filename(name)
