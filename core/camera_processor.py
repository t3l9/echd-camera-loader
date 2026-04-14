"""
Обработчик камер для сайта ECHD
Работа с Selenium, создание снимков, обработка положений
"""
import os
import time
import logging
from datetime import datetime

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PyQt6.QtWidgets import QApplication, QMessageBox

from config import url, downloads_folder
from core.file_utils import is_file_downloaded, move_and_rename_last_downloaded_file

logger = logging.getLogger(__name__)


# Forward reference для избежания циклического импорта
def get_main_window():
    """Получает главное окно приложения"""
    for widget in QApplication.topLevelWidgets():
        if widget.__class__.__name__ == 'MainWindow':
            return widget
    return None


class CameraProcessor:
    """Класс для обработки камер с улучшенной логикой повторных попыток"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.driver = None
        self.problematic_cameras = []
        self.missing_position_cameras = []
        self.progress_callback = None
        self.cancel_check_callback = None
        self._is_cancelled = False
        self._is_authenticated = False
        self.chrome_options = None

    def _initialize_driver(self):
        """Инициализация драйвера Chrome с автоматическим разрешением медиа-доступа"""
        try:
            chrome_options = Options()

            # Существующие опции
            chrome_options.add_argument("--force-device-scale-factor=0.8")
            chrome_options.add_argument("--high-dpi-support=0.8")
            chrome_options.add_argument("--disable-extensions")
            chrome_options.add_argument("--disable-plugins")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")

            # === КЛЮЧЕВЫЕ ОПЦИИ ДЛЯ РАЗРЕШЕНИЯ КАМЕРЫ И МИКРОФОНА ===
            chrome_options.add_argument("--use-fake-ui-for-media-stream")  # Автоматически разрешает доступ

            # Дополнительные опции для стабильности
            chrome_options.add_argument("--disable-web-security")
            chrome_options.add_argument("--allow-running-insecure-content")
            chrome_options.add_argument("--disable-features=WebRtcHideLocalIpsWithMdns")

            # Настройки профиля для автоматического разрешения
            prefs = {
                "profile.default_content_setting_values.media_stream_mic": 1,  # Разрешить микрофон
                "profile.default_content_setting_values.media_stream_camera": 1,  # Разрешить камеру
                "profile.default_content_setting_values.notifications": 2,  # Блокировать уведомления
                "download.default_directory": downloads_folder,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True,
                "safebrowsing.enabled": True,
                "credentials_enable_service": False,  # Отключить сохранение паролей
                "profile.password_manager_enabled": False
            }

            chrome_options.add_experimental_option("prefs", prefs)

            # Дополнительные экспериментальные опции
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option("useAutomationExtension", False)

            # Selenium 4.6+ сам скачивает нужный драйвер
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.maximize_window()

            # Устанавливаем параметры для автоматического разрешения через CDP
            self.driver.execute_cdp_cmd('Browser.setPermission', {
                'origin': url,
                'permission': {'name': 'camera'},
                'setting': 'granted'
            })

            self.driver.execute_cdp_cmd('Browser.setPermission', {
                'origin': url,
                'permission': {'name': 'microphone'},
                'setting': 'granted'
            })

            logger.info("Драйвер Chrome успешно инициализирован с автоматическим разрешением медиа-доступа")
            return True

        except Exception as e:
            logger.error(f"Ошибка инициализации драйвера: {e}")
            return False

    def _setup_media_permissions(self):
        """Настройка разрешений для камеры и микрофона после авторизации"""
        try:
            # Используем Chrome DevTools Protocol для установки разрешений
            permissions = [
                ('camera', 'granted'),
                ('microphone', 'granted'),
                ('geolocation', 'granted'),
                ('notifications', 'denied')
            ]

            for permission_name, setting in permissions:
                try:
                    self.driver.execute_cdp_cmd('Browser.setPermission', {
                        'origin': url,
                        'permission': {'name': permission_name},
                        'setting': setting
                    })
                    logger.info(f"Разрешение {permission_name} установлено в '{setting}'")
                except Exception as e:
                    logger.warning(f"Не удалось установить разрешение {permission_name}: {e}")

            # Альтернативный способ через JavaScript
            self.driver.execute_script("""
                if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                    navigator.mediaDevices.getUserMedia({ video: true, audio: true })
                        .then(function(stream) {
                            console.log("Доступ к камере и микрофону получен");
                            // Останавливаем поток, чтобы не занимать ресурсы
                            stream.getTracks().forEach(track => track.stop());
                        })
                        .catch(function(err) {
                            console.log("Ошибка доступа к медиаустройствам:", err);
                        });
                }
            """)

            time.sleep(1)
            return True

        except Exception as e:
            logger.error(f"Ошибка настройки медиа-разрешений: {e}")
            return False

    def _handle_notifications(self):
        """Обработка уведомлений"""
        try:
            time.sleep(2)

            try:
                notification1 = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[2]/div/div[7]/div[24]/div[3]/div[1]/div[2]/div[2]/div[2]/div[2]/div/button[1]"))
                )
                notification1.click()
                logger.info("Первое уведомление закрыто")
                time.sleep(0.5)
            except Exception:
                logger.debug("Первое уведомление не найдено")

            try:
                notification2 = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[2]/div/div[6]/div/div/div[2]/div[2]/div[2]/div/label/div"))
                )
                notification2.click()
                logger.info("Второе уведомление закрыто")
                time.sleep(0.5)
            except Exception:
                logger.debug("Второе уведомление не найдено")

            try:
                notification3 = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[2]/div/div[6]/div/div/div[2]/div[2]/div[2]/button"))
                )
                notification3.click()
                logger.info("Третье уведомление закрыто")
                time.sleep(0.5)
            except Exception:
                logger.debug("Третье уведомление не найдено")

            self.driver.refresh()
            logger.info("Страница перезагружена после закрытия уведомлений")
            time.sleep(2)

        except Exception as e:
            logger.error(f"Ошибка при обработке уведомлений: {e}")

    def _setup_interface(self):
        """Настройка интерфейса"""
        try:
            # Переход к списку камер
            list_header = WebDriverWait(self.driver, 100).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//*[@id='widget-sidebar-outer-visibility-manager']/div[2]/div[2]/div[2]/div[1]/div/div/div/div[1]/button[2]"))
            )
            list_header.click()

            list_header = WebDriverWait(self.driver, 100).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "//*[@id='widget-sidebar-outer-visibility-manager']/div[2]/div[1]/div[1]/div/div[2]/div[1]/div"))
            )
            list_header.click()

            # Уменьшение масштаба
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL, Keys.SUBTRACT)
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL, Keys.SUBTRACT)
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL, Keys.SUBTRACT)

            return True

        except Exception as e:
            logger.error(f"Ошибка настройки интерфейса: {e}")
            return False

    def set_progress_callback(self, callback):
        """Установка callback для обновления прогресса"""
        self.progress_callback = callback

    def set_cancel_check(self, callback):
        """Установка callback для проверки отмены"""
        self.cancel_check_callback = callback

    def _update_progress(self, current, total, status):
        """Обновление прогресса через callback"""
        if self.progress_callback and (not self.cancel_check_callback or not self.cancel_check_callback()):
            self.progress_callback(current, total, status)

    def fast_process_single_camera(self, row, is_entrance, folder_path):
        """Быстрая обработка одной камеры"""
        try:
            # Используем уже авторизованный драйвер
            if not self.driver or not self._is_authenticated:
                logger.error("Драйвер не инициализирован или не авторизован")
                return False

            if is_entrance:
                return self._process_entrance_camera(
                    row=row,
                    folder_path=folder_path
                )
            else:
                return self._process_common_camera(
                    row=row,
                    folder_path=folder_path
                )

        except Exception as e:
            logger.error(f"Ошибка при обработке камеры: {e}")

            # Пытаемся обновить страницу при ошибке
            try:
                camera_id = row.get('Номер камеры', 'Unknown')
                logger.info(f"🔄 Обновляю страницу после ошибки с камерой {camera_id}")
                self.driver.refresh()
                time.sleep(3)
                # Переход к списку камер
                list_header = WebDriverWait(self.driver, 100).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "//*[@id='widget-sidebar-outer-visibility-manager']/div[2]/div[2]/div[2]/div[1]/div/div/div/div[1]/button[2]"))
                )
                list_header.click()

                list_header = WebDriverWait(self.driver, 100).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "//*[@id='widget-sidebar-outer-visibility-manager']/div[2]/div[1]/div[1]/div/div[2]/div[1]/div"))
                )
                list_header.click()
            except:
                pass

            return False

    def _login_to_site(self):
        """Авторизация на сайте с настройкой разрешений"""
        try:
            # === НАСТРОЙКА ФЕЙКОВОЙ КАМЕРЫ ===
            # Путь к видео для фейковой камеры
            fake_video_path = r"1.mp4"  # Укажите свой путь к видео

            # Сохраняем старые опции, если нужно пересоздать драйвер
            need_restart = False

            # Проверяем существование видеофайла
            if os.path.exists(fake_video_path):
                print(f"📹 Настроена фейковая камера с видео: {fake_video_path}")

                # Вместо получения driver.options, создаем новые опции
                chrome_options = Options()

                # Копируем существующие аргументы, если они есть
                if hasattr(self, 'chrome_options') and self.chrome_options:
                    # Если у нас сохранены опции, используем их
                    chrome_options = self.chrome_options
                else:
                    # Или создаем новые с базовыми настройками
                    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                    chrome_options.add_argument('--disable-extensions')
                    chrome_options.add_argument('--disable-gpu')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                    chrome_options.add_argument('--disable-popup-blocking')

                    # Опции для автоматического разрешения медиа
                    prefs = {
                        'profile.default_content_setting_values.media_stream_camera': 1,
                        'profile.default_content_setting_values.media_stream_mic': 1,
                        'profile.default_content_setting_values.notifications': 1
                    }
                    chrome_options.add_experimental_option('prefs', prefs)

                # Добавляем аргументы для фейковой камеры
                chrome_options.add_argument("--use-fake-device-for-media-stream")
                chrome_options.add_argument("--use-fake-ui-for-media-stream")
                chrome_options.add_argument(f"--use-file-for-fake-video-capture={fake_video_path}")

                # Сохраняем опции для будущего использования
                self.chrome_options = chrome_options

                # Перезапускаем драйвер с новыми опциями
                if self.driver:
                    old_driver = self.driver
                    self.driver = webdriver.Chrome(options=chrome_options)
                    old_driver.quit()
                else:
                    self.driver = webdriver.Chrome(options=chrome_options)

                print("✅ Фейковая камера успешно настроена")
            else:
                print(f"⚠️ Видеофайл не найден: {fake_video_path}. Пропускаем настройку фейковой камеры")
                # Если драйвер еще не создан, создаем его с базовыми настройками
                if not self.driver:
                    chrome_options = Options()
                    chrome_options.add_argument('--disable-blink-features=AutomationControlled')
                    chrome_options.add_argument('--disable-extensions')
                    chrome_options.add_argument('--disable-gpu')
                    chrome_options.add_argument('--no-sandbox')
                    chrome_options.add_argument('--disable-dev-shm-usage')
                    chrome_options.add_argument('--disable-popup-blocking')

                    prefs = {
                        'profile.default_content_setting_values.media_stream_camera': 1,
                        'profile.default_content_setting_values.media_stream_mic': 1,
                        'profile.default_content_setting_values.notifications': 1
                    }
                    chrome_options.add_experimental_option('prefs', prefs)

                    self.chrome_options = chrome_options
                    self.driver = webdriver.Chrome(options=chrome_options)

            # Загружаем страницу
            self.driver.get(url)
            time.sleep(2)

            # Нажимаем кнопку входа
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//*[@id='login_page']/div/div/div[2]"))
            )
            login_button.click()

            # Нажимаем "Войти"
            login_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Войти')]"))
            )
            login_button.click()
            time.sleep(0.5)

            # Вводим логин
            login_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, 'login'))
            )
            login_input.send_keys(self.username)

            # Вводим пароль
            password_input = WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.ID, 'password'))
            )
            password_input.send_keys(self.password)

            # Нажимаем кнопку входа
            submit_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.ID, 'bind'))
            )
            submit_button.click()

            # Небольшая пауза для обработки авторизации
            time.sleep(3)

            # === ПОЛУЧАЕМ ВРЕМЯ ОЖИДАНИЯ ИЗ НОВОЙ ВКЛАДКИ ===
            # Получаем главное окно и вкладку отложенного запуска
            main_window = get_main_window()

            if main_window and hasattr(main_window, 'delayed_tab'):
                wait_seconds = main_window.delayed_tab.get_wait_seconds()

                if wait_seconds > 40:  # Если выбрано время больше стандартного
                    print(f"⏰ Режим отложенного запуска: ожидание {wait_seconds} секунд")

                    # Показываем уведомление
                    try:
                        msg_box = QMessageBox(main_window)
                        msg_box.setWindowTitle("Отложенный запуск")
                        wait_minutes = wait_seconds // 60
                        wait_hours = wait_minutes // 60
                        remaining_minutes = wait_minutes % 60

                        if wait_hours > 0:
                            time_str = f"{wait_hours} ч {remaining_minutes} мин"
                        else:
                            time_str = f"{wait_minutes} мин"

                        msg_box.setText(
                            f"⏰ Режим отложенного запуска\n\nОжидание: {time_str}\n\nНе выключайте компьютер!")
                        msg_box.setStyleSheet("""
                            QMessageBox {
                                background-color: #2E2E2E;
                                color: white;
                            }
                            QLabel {
                                color: white;
                                font-size: 14px;
                                min-width: 300px;
                            }
                            QPushButton {
                                background-color: #6A0DAD;
                                color: white;
                                border: none;
                                border-radius: 5px;
                                padding: 8px 20px;
                                font-size: 13px;
                            }
                            QPushButton:hover {
                                background-color: #7A1DAD;
                            }
                        """)
                        msg_box.exec()
                    except:
                        pass
                else:
                    wait_seconds = 35  # Значение по умолчанию
            else:
                wait_seconds = 35  # Значение по умолчанию

            # === ОЖИДАНИЕ С ПЕРИОДИЧЕСКИМ ОБНОВЛЕНИЕМ ===
            total_wait_seconds = wait_seconds
            refresh_interval = 600  # 15 минут = 600 секунд

            if total_wait_seconds > 0:
                print(f"⏳ Ожидание {total_wait_seconds} секунд перед началом работы...")

                elapsed_time = 0
                while elapsed_time < total_wait_seconds:
                    # Определяем время ожидания до следующего обновления
                    wait_time = min(refresh_interval, total_wait_seconds - elapsed_time)
                    time.sleep(wait_time)
                    elapsed_time += wait_time

                    # Обновляем страницу, если не достигли общего времени ожидания
                    if elapsed_time < total_wait_seconds:
                        minutes_passed = elapsed_time // 60
                        print(f"⏱️ Прошло {minutes_passed} минут. Обновляю страницу...")
                        self.driver.refresh()
                        # Даем странице время на загрузку после обновления
                        time.sleep(5)

                print(f"✅ Ожидание завершено! Начинаю работу...")

            # === НАСТРАИВАЕМ РАЗРЕШЕНИЯ ПОСЛЕ АВТОРИЗАЦИИ ===
            self._setup_media_permissions()

            self._is_authenticated = True
            return True

        except Exception as e:
            logger.error(f"Ошибка авторизации: {e}")
            return False

    def _fast_clear_fields(self):
        """Быстрая очистка полей"""
        try:
            close_selectors = [
                "/html/body/div[2]/div/div[6]/div/div/div[1]/div[2]/div[2]/button[3]",
                "/html/body/div[2]/div/div[7]/div/div/div[1]/div[2]/div[2]/button[3]",
                "/html/body/div[2]/div/div[8]/div[25]/div[1]/div[2]/div[1]/div[3]/div/div/div/button"
            ]

            for selector in close_selectors:
                try:
                    element = WebDriverWait(self.driver, 0.5).until(
                        EC.element_to_be_clickable((By.XPATH, selector))
                    )
                    element.click()
                    time.sleep(0.2)
                except:
                    continue

            # === ДОПОЛНИТЕЛЬНО: ОЧИЩАЕМ ПОЛЕ ПОИСКА ===
            try:
                search_input = WebDriverWait(self.driver, 0.5).until(
                    EC.presence_of_element_located(
                        (By.XPATH,
                         "//input[@data-training-identifier='[WidgetsEchd2]sidebar-cameras-search-panel__search_input']")
                    )
                )
                search_input.clear()
                # Отправляем Escape для снятия фокуса
                search_input.send_keys(Keys.ESCAPE)
            except:
                pass

        except Exception as e:
            logger.debug(f"Быстрая очистка не удалась: {e}")

    def _fast_search_and_select_camera(self, camera_id):
        """Быстрый поиск камеры с очисткой поля"""
        for attempt in range(2):
            try:
                search_input = WebDriverWait(self.driver, 15).until(
                    EC.element_to_be_clickable(
                        (By.XPATH,
                         "//input[@data-training-identifier='[WidgetsEchd2]sidebar-cameras-search-panel__search_input']")
                    )
                )

                # === ИСПРАВЛЕНИЕ: ОЧИСТКА ПОЛЯ ТРЕМЯ СПОСОБАМИ ===
                # Способ 1: Обычная очистка
                search_input.clear()

                # Способ 2: Выделить все и удалить
                search_input.send_keys(Keys.CONTROL + 'a')
                search_input.send_keys(Keys.DELETE)

                # Способ 3: Дополнительно очищаем стрелками
                for _ in range(10):
                    search_input.send_keys(Keys.BACKSPACE)

                # Теперь вводим новый ID
                search_input.send_keys(camera_id)
                search_input.send_keys(Keys.RETURN)
                time.sleep(0.8)

                camera_item = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "item_0"))
                )
                camera_item.click()
                return True

            except Exception as e:
                if attempt == 1:
                    logger.debug(f"Быстрый поиск не удался: {e}")
                time.sleep(0.5)

        return False

    def _fast_wait_for_camera_load(self, camera_id, timeout=30):
        """Быстрое ожидание загрузки камеры"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                element = self.driver.execute_script(
                    'return document.querySelector(\'[data-test-id="zh62wz"]\')'
                )
                if element is None:
                    return True
                time.sleep(0.9)
            return False
        except:
            return False

    def _fast_handle_place(self, place, camera_id, district, address):
        """Быстрая обработка положения с передачей дополнительных данных"""
        try:
            time.sleep(1)
            # 1. Первое нажатие
            selector1 = "/html/body/div[2]/div/div[6]/div/div/div[1]/div[2]/div[2]/div/button[1]"
            button1 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector1))
            )
            button1.click()
            logger.info(f"✅ Кнопка положения (шаг 1) нажата")
            
            time.sleep(0.5)  # Пауза для появления второго меню

            # 2. Второе нажатие
            selector2 = "/html/body/div[2]/div/div[6]/div/div/div[1]/div[3]/div/div[2]/div[1]/div[1]/button[1]"
            button2 = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, selector2))
            )
            button2.click()
            logger.info(f"✅ Кнопка положения (шаг 2) нажата")

            time.sleep(0.7)
            return self._fast_find_place_element(place, camera_id, district, address)

        except Exception as e:
            camera_info = {
                'Район': district,
                'Адрес': address,
                'Номер камеры': camera_id,
                'Положение': place,
                'Ошибка': f'Не удалось открыть меню положения: {str(e)}'
            }
            self.missing_position_cameras.append(camera_info)
            return False

    def _fast_find_place_element(self, place, camera_id, district, address):
        """Быстрый поиск элемента положения с отслеживанием ошибок"""
        try:
            search_input = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//input[@data-test-id='wxbh11' and @placeholder='Поиск']")
                )
            )
            search_input.click()
            search_input.send_keys(place)
            time.sleep(0.7)

            place_element = WebDriverWait(self.driver, 15).until(
                EC.element_to_be_clickable((By.XPATH,
                                            "/html/body/div[2]/div/div[6]/div/div/div[1]/div[3]/div/div[2]/div[1]/div[2]/div[2]/div/div[1]/div"))
            )
            place_element.click()
            return True
        except Exception as e:
            # Записываем информацию о камере с проблемным положением
            camera_info = {
                'Район': district,
                'Адрес': address,
                'Номер камеры': camera_id,
                'Положение': place,
                'Ошибка': str(e) if e else 'Положение не найдено'
            }
            self.missing_position_cameras.append(camera_info)
            logger.warning(f"❌ Положение не найдено для камеры {camera_id}: {place}")
            return False

    def _fast_take_snapshot(self, camera_id, is_entrance=False):
        """Быстрое создание снимка с ожиданием загрузки камеры

        Args:
            camera_id: ID камеры
            is_entrance: True для дворовых камер, False для обычных
        """
        try:
            # Определяем тип камеры для логирования
            camera_type = "ДВОРОВАЯ" if is_entrance else "ОБЫЧНАЯ"
            logger.info(f"📸 Начинаем снимок для {camera_type} камеры {camera_id}")

            # Разные таймауты для разных типов камер
            loader_timeout = 5 if is_entrance else 3
            stable_timeout = 20 if is_entrance else 10

            logger.info(f"⏱️ Таймауты: поиск лоудера={loader_timeout}с, ожидание загрузки={stable_timeout}с")

            # === ПРОВЕРКА НАЛИЧИЯ ЛОУДЕРА ===
            loader_locators = [
                (By.XPATH, "//div[@data-test-id='3z62wz']"),
                (By.XPATH, "//div[@data-test-id='1mhkoy']"),
                (By.XPATH, "//div[@data-test-id='3z62wz']//div[@data-test-id='1mhkoy']")
            ]

            loader_found = False
            start_time = time.time()

            for i, (by, locator) in enumerate(loader_locators, 1):
                try:
                    logger.info(f"  Проверяем локатор {i}: {locator[:50]}...")
                    element = WebDriverWait(self.driver, loader_timeout).until(
                        EC.presence_of_element_located((by, locator))
                    )
                    loader_found = True
                    logger.info(f"  ✅ Лоадер найден по локатору {i} через {time.time() - start_time:.1f}с")
                    break
                except Exception as e:
                    logger.info(f"  ⏱️ Локатор {i} не сработал за {loader_timeout}с")
                    continue

            # === ОЖИДАНИЕ ЗАГРУЗКИ КАМЕРЫ ===
            if loader_found:
                logger.info(f"⏳ Лоадер найден, ждем полной загрузки камеры {camera_id}...")

                # Ждем исчезновения основного лоудера
                wait_start = time.time()
                try:
                    WebDriverWait(self.driver, stable_timeout).until(
                        EC.invisibility_of_element_located((By.XPATH, "//div[@data-test-id='3z62wz']"))
                    )
                    logger.info(f"  ✅ Основной лоудер исчез через {time.time() - wait_start:.1f}с")
                except:
                    logger.warning(f"  ⚠️ Основной лоудер не исчез, но продолжаем")

                # Дополнительная проверка на все лоудеры
                try:
                    WebDriverWait(self.driver, 5).until(
                        lambda driver: (
                                len(driver.find_elements(By.XPATH, "//div[@data-test-id='3z62wz']")) == 0 and
                                len(driver.find_elements(By.XPATH, "//div[@data-test-id='1mhkoy']")) == 0
                        )
                    )
                    logger.info(f"  ✅ Все лоудеры исчезли")
                except:
                    logger.warning(f"  ⚠️ Некоторые лоудеры все еще видны")
            else:
                logger.info(f"⚠️ Лоудер не найден для камеры {camera_id}")

                # Для дворовых камер даем дополнительное время на стабилизацию
                if is_entrance:
                    logger.info(f"  🏠 Дворовая камера: даем доп. время на стабилизацию 2с")
                    time.sleep(2)
                else:
                    time.sleep(0.5)

            # === ФИНАЛЬНАЯ СТАБИЛИЗАЦИЯ ===
            time.sleep(0.3)

            # === ОСНОВНАЯ ЛОГИКА СНИМКА ===
            logger.info(f"📷 Делаем снимок для камеры {camera_id}")

            # 1. Нажимаем кнопку снимка
            try:
                snapshot_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[2]/div/div[6]/div/div/div[1]/div[3]/div/div[3]/div/div/div[2]/div/button[3]"))
                )
                snapshot_button.click()
                logger.info(f"  ✅ Кнопка снимка нажата")
            except Exception as e:
                logger.error(f"  ❌ Не удалось нажать кнопку снимка: {e}")
                return False

            # 2. Быстро ждем появления окна сохранения (1 секунда максимум)
            try:
                save_button = WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[2]/div/div[6]/div[2]/div/div[4]/div/div/button[2]"))
                )
                logger.info(f"  ✅ Окно сохранения открылось")
            except Exception as e:
                logger.error(f"  ❌ Окно сохранения не появилось: {e}")
                return False

            # 3. Нажимаем "Сохранить"
            try:
                save_button.click()
                logger.info(f"  ✅ Кнопка 'Сохранить' нажата")
            except Exception as e:
                logger.error(f"  ❌ Не удалось нажать 'Сохранить': {e}")
                return False

            # 4. Быстрая проверка наличия кнопки закрытия (1 секунда)
            close_start = time.time()
            close_button = None

            try:
                close_button = WebDriverWait(self.driver, 1).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[2]/div/div[6]/div[2]/div/div[1]/div[2]/button[2]"))
                )
                logger.info(f"  ✅ Кнопка закрытия найдена через {time.time() - close_start:.1f}с")
            except:
                logger.info(f"  ⚠️ Кнопка закрытия не найдена за 1с, пробуем Escape")

            # 5. Закрываем окно просмотра
            if close_button:
                try:
                    close_button.click()
                    logger.info(f"  ✅ Окно просмотра закрыто")
                except Exception as e:
                    logger.error(f"  ❌ Не удалось закрыть окно кнопкой: {e}")
                    # Пробуем Escape как запасной вариант
                    try:
                        self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                        logger.info(f"  ✅ Окно закрыто через Escape")
                    except:
                        pass
            else:
                # Если кнопки нет - пробуем Escape
                try:
                    self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                    logger.info(f"  ✅ Окно закрыто через Escape")
                except Exception as e:
                    logger.error(f"  ❌ Не удалось закрыть окно: {e}")

            # 6. Быстрая проверка возврата к основному интерфейсу (0.5 секунды)
            try:
                WebDriverWait(self.driver, 0.5).until(
                    EC.element_to_be_clickable((By.XPATH,
                                                "/html/body/div[2]/div/div[6]/div/div/div[1]/div[3]/div/div[3]/div/div/div[2]/div/button[3]"))
                )
                logger.info(f"  ✅ Вернулись к основному интерфейсу")
            except:
                # Не критично, если не нашли - возможно, интерфейс уже готов
                pass

            # Итоговое время обработки
            total_time = time.time() - start_time
            logger.info(f"✅ Снимок для камеры {camera_id} завершен за {total_time:.1f}с")

            return True

        except Exception as e:
            logger.error(f"❌ Критическая ошибка при создании снимка для камеры {camera_id}: {str(e)}")

            # Пытаемся восстановиться после ошибки
            try:
                # Пробуем закрыть возможные модальные окна
                self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                time.sleep(0.5)
            except:
                pass

            return False

    def _fast_check_file_download(self, camera_id, folder_name, address=None):
        """Проверка загрузки файла с правильными таймаутами"""

        logger.info(f"📥 Ожидаем загрузку файла для камеры {camera_id}")

        # Даем время на начало загрузки (файл может появиться не сразу)
        time.sleep(0.8)

        max_attempts = 10  # Увеличиваем количество попыток
        wait_time = 0.3  # Уменьшаем время между попытками

        start_time = time.time()

        for attempt in range(max_attempts):
            elapsed = time.time() - start_time
            logger.info(f"  Попытка {attempt + 1}/{max_attempts} (прошло {elapsed:.1f}с)")

            if is_file_downloaded(camera_id):
                logger.info(f"  ✅ Файл найден на попытке {attempt + 1}")

                # Даем еще немного времени на завершение записи файла
                time.sleep(0.5)

                new_filename = move_and_rename_last_downloaded_file(
                    folder_name,
                    camera_id,
                    address
                )

                if new_filename:
                    logger.info(f"  ✅ Файл успешно перемещен и переименован в '{new_filename}'")
                    return True
                else:
                    logger.warning(f"  ⚠️ Файл найден, но не удалось переместить")
                    return False

            time.sleep(wait_time)

        # Если файл не найден, проверим папку загрузок вручную
        logger.warning(f"❌ Файл не найден после {max_attempts} попыток ({time.time() - start_time:.1f}с)")

        # Диагностика: покажем какие файлы есть в папке загрузок
        try:
            files = os.listdir(downloads_folder)
            recent_files = [f for f in files if os.path.isfile(os.path.join(downloads_folder, f))]
            recent_files.sort(key=lambda x: os.path.getctime(os.path.join(downloads_folder, x)), reverse=True)

            if recent_files:
                logger.info(f"  📂 Последние файлы в папке загрузок:")
                for i, f in enumerate(recent_files[:3]):
                    file_path = os.path.join(downloads_folder, f)
                    size = os.path.getsize(file_path)
                    mod_time = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime('%H:%M:%S')
                    logger.info(f"    {i + 1}. {f} ({size} bytes, {mod_time})")
        except Exception as e:
            logger.error(f"  Ошибка диагностики: {e}")

        return False

    def _process_common_camera(self, row, folder_path):
        """Обработка обычной камеры"""
        import pandas as pd

        district = row.get("Район")
        camera_id = row.get("Номер камеры")
        place = row.get("Положение")
        address = row.get("Адрес")

        if camera_id is None or (isinstance(camera_id, pd.Series) and camera_id.empty) or pd.isna(camera_id):
            return False

        if district is None or (isinstance(district, pd.Series) and district.empty) or pd.isna(district):
            district = "Без района"
        else:
            district = str(district)

        district_folder = os.path.join(folder_path, district)
        os.makedirs(district_folder, exist_ok=True)

        self._fast_clear_fields()

        if not self._fast_search_and_select_camera(str(camera_id)):
            return False

        if not self._fast_wait_for_camera_load(str(camera_id)):
            return False

        # Передаем дополнительные параметры в метод обработки положения
        if place is not None and not (isinstance(place, pd.Series) and place.empty) and not pd.isna(place):
            self._fast_handle_place(str(place), str(camera_id), district, address)

        if not self._fast_take_snapshot(str(camera_id), is_entrance=False):
            return False

        # Передаем адрес для переименования файла
        address_str = None if address is None or (isinstance(address, pd.Series) and address.empty) or pd.isna(
            address) else str(address)
        return self._fast_check_file_download(str(camera_id), district_folder, address_str)

    def _process_entrance_camera(self, row, folder_path):
        """Обработка дворовой камеры"""
        import pandas as pd

        district = row.get('Район')
        camera_id = row.get('Номер камеры')
        address = row.get('Адрес')

        if camera_id is None or (isinstance(camera_id, pd.Series) and camera_id.empty) or pd.isna(camera_id):
            return False

        if district is None or (isinstance(district, pd.Series) and district.empty) or pd.isna(district):
            return False
        else:
            district = str(district)

        folder_name = os.path.join(folder_path, district)
        os.makedirs(folder_name, exist_ok=True)

        try:
            # Быстрая очистка полей
            self._fast_clear_fields()

            # Быстрый поиск и выбор камеры
            if not self._fast_search_and_select_camera(str(camera_id)):
                return False

            # Ускоренное ожидание загрузки
            if not self._fast_wait_for_camera_load(str(camera_id)):
                logger.warning(f"Камера {camera_id} не загрузилась")
                return False

            # Ускоренное создание снимка
            if not self._fast_take_snapshot(str(camera_id), is_entrance=True):
                return False

            # Проверка файла с передачей адреса для переименования
            address_str = None if address is None or (isinstance(address, pd.Series) and address.empty) or pd.isna(
                address) else str(address)
            return self._fast_check_file_download(str(camera_id), folder_name, address_str)

        except Exception as e:
            logger.warning(f"Ошибка при обработке камеры {camera_id}: {e}")
            return False
