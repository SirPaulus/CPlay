from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogIcon,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivy.uix.widget import Widget
from kivymd.uix.button import MDButton, MDButtonText
from utils.auth import hash_password
from models.database import login_user, set_current_user


class LoginScreen(MDScreen):
    dialog = None

    def try_login(self):
        """Пытается войти с введёнными данными."""
        username = self.ids.username.text.strip()
        password = self.ids.password.text

        if not username or not password:
            self.show_dialog("Заполните все поля")
            return

        user = login_user(username, hash_password(password))
        if user:
            # Успешный вход
            set_current_user(user)
            # Переходим на главный экран (preferences)
            self.manager.current = 'games'
        else:
            self.show_dialog("Неверное имя пользователя или пароль")

    def guest_login(self):
        """Вход как гость (без регистрации)."""
        # Устанавливаем гостевого пользователя с ролью 'guest'
        set_current_user({'username': 'Гость', 'role': 'guest'})
        self.manager.current = 'games'

    def show_dialog(self, text):
        """Показывает диалог с ошибкой."""
        if not self.dialog:
            self.dialog = MDDialog(
                MDDialogHeadlineText(text=text),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="OK"),
                        style='text', on_release=lambda x: self.dialog.dismiss()),
                    Widget()
                )
            )
        else:
            self.dialog.text = text
        self.dialog.open()

    def go_to_register(self):
        """Переходит на экран регистрации."""
        self.manager.current = 'register'
