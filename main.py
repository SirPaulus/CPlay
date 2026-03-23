"""
Главный файл приложения. Загружает конфигурацию, инициализирует БД и запускает приложение.
"""

import os
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp

from screens.admin_screen import AdminScreen
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.games_screen import GamesScreen
from models.database import init_db, DB_PATH, get_current_user, set_current_user


class CPlayApp(MDApp):
    def build(self):
        # Настройка темы
        self.theme_cls.theme_style = "Light"
        self.theme_cls.primary_palette = "Indigo"

        # Загрузка KV-файлов экранов
        self.load_kv_files()

        # Инициализация БД при первом запуске
        self.init_database()

        # Менеджер экранов
        sm = ScreenManager()
        sm.add_widget(LoginScreen(name='login'))
        sm.add_widget(RegisterScreen(name='register'))
        sm.add_widget(GamesScreen(name='games'))
        sm.add_widget(AdminScreen(name='admin'))
        return sm

    def load_kv_files(self):
        """Загружает все .kv файлы из папки kv/."""
        kv_dir = os.path.join(os.path.dirname(__file__), 'kv')
        if os.path.exists(kv_dir):
            for filename in os.listdir(kv_dir):
                if filename.endswith('.kv'):
                    Builder.load_file(os.path.join(kv_dir, filename))

    def init_database(self):
        """Создаёт структуру БД, если она отсутствует."""
        if not os.path.exists(DB_PATH):
            init_db()  # создаёт таблицы и добавляет тестовые данные

    def is_admin(self):
        user = get_current_user()
        return user and user.get('role') == 'admin'

    def open_admin(self):
        self.root.current = 'admin'

    def back_to_games(self):
        self.root.current = 'games'

    def logout(self):
        set_current_user(None)
        self.root.current = 'login'

    def add_game(self):
        # Заглушка для добавления игры (можно реализовать позже)
        pass


if __name__ == '__main__':
    CPlayApp().run()
