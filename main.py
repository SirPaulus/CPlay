"""
Главный файл приложения. Загружает конфигурацию, инициализирует БД и запускает приложение.
"""
import os
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivymd.app import MDApp
from kivy.graphics import Color, Rectangle
from kivymd.uix.navigationdrawer import (
    MDNavigationLayout,
    MDNavigationDrawer,
    MDNavigationDrawerMenu,
    MDNavigationDrawerItem,
    MDNavigationDrawerItemLeadingIcon,
    MDNavigationDrawerItemText,
    MDNavigationDrawerHeader,
    MDNavigationDrawerDivider,
)
from kivymd.uix.label import MDLabel
from screens.login_screen import LoginScreen
from screens.register_screen import RegisterScreen
from screens.games_screen import GamesScreen
from screens.favorites_screen import FavoritesScreen
from kivymd.uix.bottomsheet import MDBottomSheet, MDBottomSheetDragHandle, MDBottomSheetDragHandleTitle, \
    MDBottomSheetDragHandleButton
from kivymd.uix.boxlayout import MDBoxLayout
from models.database import init_db, DB_PATH, get_current_user, set_current_user
from kivymd.theming import ThemableBehavior


class CPlayApp(MDApp):
    def build(self):
        self.theme_cls.theme_style = "Dark"
        # Загрузка KV-файлов экранов
        self.load_kv_files()
        # Инициализация БД при первом запуске
        self.init_database()

        # Менеджер экранов
        self.sm = ScreenManager()
        self.sm.add_widget(LoginScreen(name='login'))
        self.sm.add_widget(RegisterScreen(name='register'))
        self.sm.add_widget(GamesScreen(name='games'))
        self.sm.add_widget(FavoritesScreen(name='favorites'))

        self.nav_drawer = MDNavigationDrawer(
            id='nav_drawer',  # id для доступа из kv
            radius=(0, 16, 16, 0),
            drawer_type='modal'  # можно изменить на 'standard'
        )
        # Первоначальное наполнение меню
        self.update_navigation_menu()

        drag_handle = MDBottomSheetDragHandle(
            MDBottomSheetDragHandleTitle(
                text="",
                pos_hint={"center_y": .5},
                theme_text_color="Custom",
                text_color=(1, 1, 1, 1),  # белый текст
            ),
            MDBottomSheetDragHandleButton(
                icon="close",
                on_release=lambda x: self.bottom_sheet.set_state("close"),
                theme_icon_color="Custom",
                icon_color=(1, 1, 1, 1),  # белая иконка
            ),
            drag_handle_color="white",  # цвет полоски
        )
        # Устанавливаем фон ручки после создания
        with drag_handle.canvas.before:
            Color(0.1, 0.1, 0.1, 1)  # тёмно-серый
            Rectangle(size=drag_handle.size, pos=drag_handle.pos)

        # BottomSheet (пока пустой, наполним динамически)
        self.bottom_sheet = MDBottomSheet(
            drag_handle,
            id='game_bottom_sheet',
            sheet_type='modal',
            size_hint_y=None,
            adaptive_height=True,
            theme_bg_color="Custom",
            md_bg_color=(0.1, 0.1, 0.1, 1)  # фон всей панели
        )
        # Контейнер для содержимого (будем заполнять при открытии)
        self.bottom_sheet_content = MDBoxLayout(
            orientation='vertical',
            spacing='12dp',
            padding='16dp',
            size_hint_y=None,
            adaptive_height=True,
        )
        self.bottom_sheet.add_widget(self.bottom_sheet_content)

        # Корневой контейнер
        layout = MDNavigationLayout()
        layout.add_widget(self.sm)
        layout.add_widget(self.nav_drawer)
        layout.add_widget(self.bottom_sheet)
        return layout

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

    def update_navigation_menu(self):
        """Обновляет содержимое навигационного ящика в зависимости от роли пользователя."""
        self.nav_drawer.clear_widgets()
        menu = MDNavigationDrawerMenu()
        user = get_current_user()

        if user:
            # Заголовок с именем пользователя
            header = MDNavigationDrawerHeader(
                MDLabel(
                    text=user.get('username', 'Пользователь'),
                    theme_text_color="Custom",
                    adaptive_height=True,
                    padding_x="16dp",
                    font_style="Display",
                    role="small",
                ),
                orientation="vertical",
                adaptive_height=True,
            )
            menu.add_widget(header)
            menu.add_widget(MDNavigationDrawerDivider())

            # Пункт "Игры"
            item_games = MDNavigationDrawerItem(
                MDNavigationDrawerItemLeadingIcon(icon="gamepad"),
                MDNavigationDrawerItemText(text="Игры"),
                on_release=lambda x: self.switch_to_screen('games')
            )
            menu.add_widget(item_games)

            if user.get('role') == 'user':
                item_favorite = MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(icon="heart"),
                    MDNavigationDrawerItemText(text="Избранное"),
                    on_release=lambda x: self.switch_to_screen('favorites')
                )
                menu.add_widget(item_favorite)

            if user.get('role') == 'admin':
                # Пункт "Добавить игру" (опционально, если вы оставляете кнопку "+" в верхней панели)
                item_add_game = MDNavigationDrawerItem(
                    MDNavigationDrawerItemLeadingIcon(icon="plus"),
                    MDNavigationDrawerItemText(text="Добавить игру"),
                    on_release=lambda x: self.open_add_game()
                )
                menu.add_widget(item_add_game)

            # Пункт "Выйти"
            item_logout = MDNavigationDrawerItem(
                MDNavigationDrawerItemLeadingIcon(icon="logout"),
                MDNavigationDrawerItemText(text="Выйти"),
                on_release=lambda x: self.logout()
            )
            menu.add_widget(item_logout)
        else:
            # Гостевой режим – можно добавить пункты "Войти" и "Зарегистрироваться"
            item_login = MDNavigationDrawerItem(
                MDNavigationDrawerItemLeadingIcon(icon="login"),
                MDNavigationDrawerItemText(text="Войти"),
                on_release=lambda x: self.switch_to_screen('login')
            )
            menu.add_widget(item_login)
            item_register = MDNavigationDrawerItem(
                MDNavigationDrawerItemLeadingIcon(icon="account-plus"),
                MDNavigationDrawerItemText(text="Зарегистрироваться"),
                on_release=lambda x: self.switch_to_screen('register')
            )
            menu.add_widget(item_register)

        self.nav_drawer.add_widget(menu)

    def logout(self):
        set_current_user(None)
        self.update_navigation_menu()
        self.sm.current = 'login'
        self.nav_drawer.set_state("close")

    def switch_to_screen(self, screen_name):
        self.sm.current = screen_name
        self.nav_drawer.set_state("close")

    def open_add_game(self):
        if self.sm.current == 'games':
            games_screen = self.sm.get_screen('games')
            games_screen.show_add_game_dialog()
        self.nav_drawer.set_state("close")


if __name__ == '__main__':
    CPlayApp().run()
