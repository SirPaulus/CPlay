from kivymd.uix.screen import MDScreen
from kivy.uix.widget import Widget
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
)
from kivymd.uix.button import MDButton, MDButtonText
from utils.auth import hash_password
from models.database import register_user


class RegisterScreen(MDScreen):
    dialog = None

    def try_register(self):
        """Пытается зарегистрировать нового пользователя."""
        username = self.ids.username.text.strip()
        password = self.ids.password.text
        confirm = self.ids.confirm.text

        if not username or not password or not confirm:
            self.show_dialog("Заполните все поля")
            return

        if password != confirm:
            self.show_dialog("Пароли не совпадают")
            return

        if len(password) < 4:
            self.show_dialog("Пароль должен быть не менее 4 символов")
            return

        success = register_user(username, hash_password(password))
        if success:
            self.show_success("Регистрация успешна! Теперь вы можете войти.")
            self.manager.current = 'login'
        else:
            self.show_dialog("Пользователь с таким именем уже существует")

    def show_dialog(self, text):
        if not self.dialog:
            self.dialog = MDDialog(
                MDDialogHeadlineText(text=text),
                MDDialogButtonContainer(
                    Widget(),
                    MDButton(
                        MDButtonText(text="OK"), style='text', on_release=lambda x: self.dialog.dismiss()),
                    Widget())
            )
        else:
            self.dialog.text = text
        self.dialog.open()

    def go_to_login(self):
        """Возврат на экран входа."""
        self.manager.current = 'login'

    def show_success(self, text):
        # Используем тот же диалог для простоты
        self.show_dialog(text)
