from kivy.metrics import dp
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.app import MDApp
from kivymd.uix.fitimage import FitImage
from kivymd.uix.button import MDButton, MDButtonText, MDIconButton
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogSupportingText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivymd.uix.stacklayout import MDStackLayout
from kivy.clock import Clock
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHintText,
    MDTextFieldHelperText,
)
from kivymd.uix.list import MDListItem, MDListItemLeadingIcon, MDListItemSupportingText
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from models.database import get_game_by_id, update_game, get_all_genres, get_all_platforms, db_delete_game, \
    get_current_user, add_to_favorites, remove_from_favorites, is_favorite, save_game_image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
import os
from kivymd.uix.card import MDCard
from utils.path_utils import resource_path


class GameCard(MDCard):
    """Implements a material card."""
    title = StringProperty('')
    genres = ListProperty([])
    date = StringProperty('')
    rating = StringProperty('')
    platforms = ListProperty([])
    game_id = NumericProperty(0)

    source = StringProperty('')
    platforms_display_text = StringProperty('')
    platform_icon = StringProperty('')

    icon_map = {
        'PC': 'microsoft-windows',
        'PS': 'sony-playstation',
        'Xbox': 'microsoft-xbox',
        'Switch': 'nintendo-switch',
        'Mobile': 'android',
    }

    def __init__(self, **kwargs):
        self.on_delete_callback = kwargs.pop('on_delete_callback', None)
        self.on_favorite_callback = kwargs.pop('on_favorite_callback', None)
        super().__init__(**kwargs)
        self.bind(platforms=self._update_platforms_display)
        self._dialog = None
        self._edit_dialog = None
        self._confirm_dialog = None
        self.selected_image_path = None

    def open_details(self, *args):
        """Открывает BottomSheet с деталями игры."""
        app = MDApp.get_running_app()
        # Получаем свежие данные из БД (на случай, если что-то изменилось)
        game_data = get_game_by_id(self.game_id)
        if not game_data:
            return

        # Очищаем предыдущее содержимое
        app.bottom_sheet_content.clear_widgets()

        # Заполняем контейнер деталями игры

        # Изображение и жанры
        poster_and_genres = MDBoxLayout(orientation='horizontal',
                                        spacing=dp(16),
                                        padding=dp(16),
                                        size_hint=(1, None),
                                        adaptive_height=True)
        poster_image = FitImage(
            pos_hint={"center_x": 0.5, "y": 0},
            source=self._get_image_source(),
            size_hint=(None, None),
            size=("180dp", "225dp"),
            allow_stretch=True,
            keep_ratio=False,
            radius=[18, 18, 18, 18],
        )
        poster_and_genres.add_widget(poster_image)
        # Жанры (чипами)
        genres_box = MDStackLayout(spacing='8dp', size_hint_y=None, adaptive_height=True, pos_hint={'top': 1})
        for genre in game_data['genres']:
            chip = MDChip(
                MDChipText(text=genre, theme_text_color="Custom", text_color="#ffffff"),
                theme_bg_color="Custom",
                md_bg_color=(0.2, 0.6, 0.8, 1),
            )
            genres_box.add_widget(chip)
        poster_and_genres.add_widget(genres_box)
        app.bottom_sheet_content.add_widget(poster_and_genres)

        # Дата публикации
        pub_date = MDLabel(
            text=f"Дата публикации: {game_data['created_at']}",
            font_style='Body',
            role='small',
            size_hint_y=None,
            height=dp(30),
        )
        app.bottom_sheet_content.add_widget(pub_date)

        # Заголовок
        title_label = MDLabel(
            text=game_data['title'],
            font_style='Headline',
            bold=True,
            size_hint_y=None,
            height=dp(40),
        )
        app.bottom_sheet_content.add_widget(title_label)

        # Описание
        desc_label = MDLabel(
            text=game_data['description'],
            font_style='Body',
            role='medium',
            size_hint_y=None,
            text_size=(app.bottom_sheet_content.width - dp(32), None),
            halign='left',
            valign='top',
        )
        desc_label.bind(
            width=lambda *x: setattr(desc_label, 'text_size', (desc_label.width, None)),
            texture_size=lambda *x: setattr(desc_label, 'height', desc_label.texture_size[1])
        )
        app.bottom_sheet_content.add_widget(desc_label)

        # Платформы
        platforms_box = MDBoxLayout(orientation='horizontal', spacing='8dp', size_hint_y=None, height=dp(40))
        for platform in game_data['platforms']:
            chip = MDChip(
                MDChipText(text=platform, theme_text_color="Custom", text_color="#ffffff"),
                theme_bg_color="Custom",
                md_bg_color=(0.4, 0.4, 0.4, 1),
            )
            platforms_box.add_widget(chip)
        app.bottom_sheet_content.add_widget(platforms_box)

        # Рейтинг
        rating_label = MDLabel(
            text=f"Рейтинг: {game_data['rating']}",
            font_style='Body',
            role='large',
            size_hint_y=None,
            height=dp(30),
        )
        app.bottom_sheet_content.add_widget(rating_label)

        # Кнопки в зависимости от роли (как в GameCard)
        user = get_current_user()
        if user and user.get('role') == 'admin':
            # Кнопки редактирования и удаления
            button_box = MDBoxLayout(orientation='horizontal', spacing='16dp', size_hint_y=None, height=dp(48))
            edit_btn = MDButton(
                MDButtonText(text='Редактировать'),
                on_release=lambda x: self.edit_game()  # переиспользуем существующий метод
            )
            delete_btn = MDButton(
                MDButtonText(text='Удалить'),
                on_release=lambda x: self.delete_game()
            )
            button_box.add_widget(edit_btn)
            button_box.add_widget(delete_btn)
            app.bottom_sheet_content.add_widget(button_box)
        elif user and user.get('role') == 'user':
            # Кнопка избранного
            fav_btn = MDIconButton(
                icon='heart' if is_favorite(user['id'], self.game_id) else 'heart-outline',
                on_release=lambda x: self.toggle_favorite(x)
            )
            app.bottom_sheet_content.add_widget(fav_btn)

        # Принудительно обновляем высоту BottomSheet, чтобы подстроиться под контент
        app.bottom_sheet_content.height = app.bottom_sheet_content.minimum_height
        app.bottom_sheet.height = app.bottom_sheet_content.height + dp(84)  # + высота drag handle

        # Открываем панель
        app.bottom_sheet.set_state("open")

    def _update_platforms_display(self, *args):
        """Update chip text based on platforms list."""

        if not self.platforms:
            self.platforms_display_text = ''
        elif len(self.platforms) == 1:
            self.platforms_display_text = self.platforms[0]
        else:
            self.platforms_display_text = f"+{len(self.platforms) - 1}"
        self.platform_icon = self.icon_map.get(self.platforms[0], 'gamepad-variant')

    def show_platforms_dialog(self):
        """Open a dialog with the full list of platforms."""
        if not self.platforms or self._dialog:
            return

        # Icon mapping (same as before)

        # Create list items
        list_items = []
        for platform in self.platforms:
            icon = self.icon_map.get(platform, 'gamepad-variant')
            item = MDListItem(
                MDListItemLeadingIcon(icon=icon),
                MDListItemSupportingText(text=platform.capitalize()),
                theme_bg_color="Custom",
                md_bg_color=self.theme_cls.transparentColor,  # Use theme transparent color
                size_hint_y=None,
                height=dp(48),
            )
            list_items.append(item)

        # Build dialog
        self._dialog = MDDialog(
            # --- Headline ---
            MDDialogHeadlineText(
                text="Платформы",
                halign="left",
            ),
            # --- Content Container (the list) ---
            MDDialogContentContainer(
                *list_items,  # Unpack the list items
                orientation="vertical",
                spacing="4dp",
            ),
            # --- Button Container (optional close button) ---
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text="Закрыть"),
                    style="text",
                    on_release=lambda x: self._dialog.dismiss(),
                ),
                spacing="8dp",
            ),
            # --- Dialog properties ---
            auto_dismiss=True,  # Allow closing by clicking outside
            size_hint=(None, None),
            height=dp(400),  # Fixed height, but will adapt to content
        )
        self._dialog.open()
        # Clean up reference when closed
        self._dialog.bind(on_dismiss=lambda *x: setattr(self, '_dialog', None))

    def admin_panel(self):
        edit_button = MDIconButton(icon="pencil",
                                   style="standard",
                                   pos_hint={"right": 0.77, "top": 1},
                                   theme_icon_color="Custom",
                                   icon_color=(0, .45, 1, 0.9),
                                   on_release=self.edit_game)
        delete_button = MDIconButton(icon="trash-can",
                                     style="standard",
                                     theme_icon_color="Custom",
                                     icon_color=(.82, 0, 0, 0.9),
                                     pos_hint={"right": 0.97, "top": 1},
                                     on_release=self.delete_game)
        self.ids.poster_container.add_widget(edit_button)
        self.ids.poster_container.add_widget(delete_button)

    def user_panel(self):
        self.favorite_icon = MDIconButton(icon="heart-outline",
                                          style="standard",
                                          pos_hint={"right": 0.95, "top": 1},
                                          theme_icon_color="Custom",
                                          icon_color=(.75, .15, 0, 0.9),
                                          on_release=self.toggle_favorite)
        self.ids.poster_container.add_widget(self.favorite_icon)

    def edit_game(self, *args):
        """Открывает диалог редактирования игры."""
        if not self.game_id:
            return

        game_data = get_game_by_id(self.game_id)
        if not game_data:
            return

        all_genres = get_all_genres()
        all_platforms = get_all_platforms()

        # --- Scroll-контейнер с фиксированной высотой ---
        scroll = MDScrollView(size_hint_y=None, height=dp(500), do_scroll_x=False)
        inner_layout = MDBoxLayout(
            orientation='vertical',
            spacing='12dp',
            padding='5dp',
            adaptive_height=True,  # высота подстраивается под содержимое
        )
        scroll.add_widget(inner_layout)

        # Поля ввода
        title_field = MDTextField(
            MDTextFieldHintText(text='Название'),
            MDTextFieldHelperText(text='', mode='on_error'),
            text=game_data['title'],
            mode='outlined',
        )
        desc_field = MDTextField(
            MDTextFieldHintText(text='Описание'),
            text=game_data['description'],
            mode='outlined',
        )
        rating_field = MDTextField(
            MDTextFieldHintText(text='Рейтинг (0-10)'),
            MDTextFieldHelperText(text='', mode='on_error'),
            text=str(game_data['rating']),
            input_filter='float',
            mode='outlined',
        )

        inner_layout.add_widget(title_field)
        inner_layout.add_widget(desc_field)
        inner_layout.add_widget(rating_field)

        # --- Выбор изображения ---
        image_selection_layout = MDBoxLayout(
            orientation='horizontal',
            spacing='8dp',
            size_hint_y=None,
            height=dp(48),
        )
        image_filename_label = MDLabel(
            text="Текущее изображение",
            theme_text_color="Custom",
            text_color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.7,
            halign='left',
        )
        choose_image_btn = MDButton(
            MDButtonText(text="Выбрать новое"),
            on_release=lambda x: self.choose_image_for_edit(image_filename_label)
        )
        image_selection_layout.add_widget(image_filename_label)
        image_selection_layout.add_widget(choose_image_btn)
        inner_layout.add_widget(image_selection_layout)

        # --- Выбор жанров ---
        genre_box = MDBoxLayout(orientation='vertical', spacing='8dp', adaptive_height=True)
        genre_box.add_widget(Widget(size_hint_y=None, height=dp(24)))
        genre_box.add_widget(MDLabel(text='Жанры', font_style='Title'))
        genre_chips = MDStackLayout(spacing='8dp', adaptive_height=True)
        genre_chips.bind(minimum_height=genre_chips.setter('height'))
        genre_box.add_widget(genre_chips)

        selected_genres = game_data['genre_ids']
        for g in all_genres:
            chip = MDChip(
                MDChipText(text=g['name']),
                type="filter",
                selected_color="green",
                active=g['id'] in selected_genres,
                size_hint=(None, None),
                width=dp(100),
                height=dp(32)
            )
            chip.bind(active=lambda instance, value, gid=g['id']: self._toggle_selection(selected_genres, gid, value))
            genre_chips.add_widget(chip)

        inner_layout.add_widget(genre_box)

        # --- Выбор платформ ---
        platform_box = MDBoxLayout(orientation='vertical', spacing='8dp', adaptive_height=True)
        platform_box.add_widget(Widget(size_hint_y=None, height=dp(24)))
        platform_box.add_widget(MDLabel(text='Платформы', font_style='Title'))
        platform_chips = MDStackLayout(spacing='8dp', adaptive_height=True)
        platform_chips.bind(minimum_height=platform_chips.setter('height'))
        platform_box.add_widget(platform_chips)

        selected_platforms = game_data['platform_ids']
        for p in all_platforms:
            chip = MDChip(
                MDChipText(text=p['name']),
                type="filter",
                selected_color="green",
                active=p['id'] in selected_platforms,
                size_hint=(None, None),
                width=dp(100),
                height=dp(32)
            )
            chip.bind(
                active=lambda instance, value, pid=p['id']: self._toggle_selection(selected_platforms, pid, value))
            platform_chips.add_widget(chip)

        inner_layout.add_widget(platform_box)

        # --- Диалог ---
        self._edit_dialog = MDDialog(
            MDDialogHeadlineText(text='Редактирование игры'),
            MDDialogContentContainer(scroll),  # scroll напрямую
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text='Отмена'),
                    style='text',
                    on_release=lambda x: self._edit_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text='Сохранить'),
                    on_release=lambda x: self._save_edit(
                        game_id=self.game_id,
                        title_field=title_field,
                        desc_field=desc_field,
                        rating_field=rating_field,
                        selected_genres=selected_genres,
                        selected_platforms=selected_platforms
                    )
                ),
                spacing='8dp'
            ),
            auto_dismiss=False,
            size_hint=(None, None)
        )
        self._edit_dialog.open()

        # Закрыть BottomSheet, если он открыт
        app = MDApp.get_running_app()
        app.bottom_sheet.set_state("close")

    def _toggle_selection(self, selected_list, item_id, active):
        """Вспомогательная функция для переключения выбранных жанров/платформ."""
        if active:
            if item_id not in selected_list:
                selected_list.append(item_id)
        else:
            if item_id in selected_list:
                selected_list.remove(item_id)

    def _save_edit(self, game_id, title_field, desc_field, rating_field, selected_genres, selected_platforms):
        """Сохраняет изменения и обновляет карточку с валидацией."""
        error = False

        # Проверка названия
        title = title_field.text.strip()
        if not title:
            title_field.error = True
            error = True
        else:
            title_field.error = False

        # Проверка рейтинга (необязательный, но если введён – должно быть число)
        rating_str = rating_field.text.strip()
        if rating_str:
            try:
                rating_val = float(rating_str)
                if rating_val < 0 or rating_val > 10:
                    rating_field.error = True
                    error = True
                    rating_field.helper_text = "Рейтинг должен быть от 0 до 10"
                else:
                    rating_field.error = False
            except ValueError:
                rating_field.error = True
                error = True
                rating_field.helper_text = "Введите число"
        else:
            rating_val = 0.0
            rating_field.error = False

        # Проверка выбора хотя бы одного жанра и платформы (по желанию)
        if not selected_genres:
            error = True
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            snackbar = MDSnackbar(
                MDSnackbarText(text="Выберите хотя бы один жанр"),
                duration=2
            )
            snackbar.open()
        if not selected_platforms:
            error = True
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            snackbar = MDSnackbar(
                MDSnackbarText(text="Выберите хотя бы одну платформу"),
                duration=2
            )
            snackbar.open()

        if error:
            return

        try:
            update_game(game_id, title, desc_field.text, rating_val, selected_genres, selected_platforms)

            if hasattr(self, 'selected_image_path') and self.selected_image_path:
                save_game_image(game_id, self.selected_image_path)

            # Обновление свойств карточки
            self.title = title
            self.rating = str(rating_val)

            all_genres_dict = {g['id']: g['name'] for g in get_all_genres()}
            all_platforms_dict = {p['id']: p['name'] for p in get_all_platforms()}
            self.genres = [all_genres_dict[gid] for gid in selected_genres if gid in all_genres_dict]
            self.platforms = [all_platforms_dict[pid] for pid in selected_platforms if pid in all_platforms_dict]

            if self._edit_dialog:
                self._edit_dialog.dismiss()
                self._edit_dialog = None

            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            snackbar = MDSnackbar(
                MDSnackbarText(text='Игра обновлена'),
                duration=2
            )
            snackbar.open()
            if self.on_delete_callback:
                Clock.schedule_once(lambda dt: self.on_delete_callback(), 0)  # обновляем список игр
            # Обновляем текущее изображение, если карточка ещё на экране
            if hasattr(self.ids, 'poster_image'):
                self.ids.poster_image.source = self._get_image_source()
                self.ids.poster_image.reload()
        except Exception as e:
            print(f'Ошибка при обновлении: {e}')
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            snackbar = MDSnackbar(
                MDSnackbarText(text='Ошибка сохранения'),
                duration=2
            )
            snackbar.open()

    def delete_game(self, *args):
        """Удаление игры с подтверждением."""
        if not self.game_id:
            return

        def confirm_delete(instance):
            try:
                db_delete_game(self.game_id)
                if self.on_delete_callback:
                    Clock.schedule_once(lambda dt: self.on_delete_callback(), 0)  # обновляем список игр
                if hasattr(self, '_confirm_dialog') and self._confirm_dialog:
                    self._confirm_dialog.dismiss()
                app = MDApp.get_running_app()
                app.bottom_sheet.set_state("close")
            except Exception as e:
                print(f'Ошибка при удалении: {e}')

        def cancel_delete(instance):
            if hasattr(self, '_confirm_dialog') and self._confirm_dialog:
                self._confirm_dialog.dismiss()

        self._confirm_dialog = MDDialog(
            MDDialogHeadlineText(text='Подтверждение удаления'),
            MDDialogSupportingText(text=f'Вы уверены, что хотите удалить игру "{self.title}"?'),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text='Отмена'),
                    style='text',
                    on_release=cancel_delete
                ),
                MDButton(
                    MDButtonText(text='Удалить'),
                    on_release=confirm_delete
                ),
                spacing='8dp'
            ),
            auto_dismiss=False,
            size_hint=(0.8, None),
            height=dp(200)
        )
        self._confirm_dialog.open()

    def on_kv_post(self, base_widget):
        super().on_kv_post(base_widget)
        self._update_platforms_display()
        self.source = self._get_image_source()
        user = get_current_user()
        if user['role'] == 'admin':
            self.admin_panel()
        elif user['role'] == 'user':
            self.user_panel()
            self.is_favorite = is_favorite(user['id'], self.game_id)
            self.favorite_icon.icon = 'heart' if self.is_favorite else 'heart-outline'

    def toggle_favorite(self, instance):
        user = get_current_user()
        if not user or not user.get('id'):
            # показать сообщение о необходимости входа
            return
        if self.is_favorite:
            success = remove_from_favorites(user['id'], self.game_id)
            if success:
                self.is_favorite = False
                self.favorite_icon.icon = 'heart-outline'
                if self.on_favorite_callback:
                    Clock.schedule_once(lambda dt: self.on_favorite_callback(), 0)
        else:
            success = add_to_favorites(user['id'], self.game_id)
            if success:
                self.is_favorite = True
                self.favorite_icon.icon = 'heart'

    def choose_image_for_edit(self, filename_label):
        filechooser = FileChooserListView(
            filters=['*.jpg', '*.jpeg', '*.png'],
            path=os.path.expanduser('~')
        )

        def select(*args):
            if filechooser.selection:
                self.selected_image_path = filechooser.selection[0]
                filename_label.text = os.path.basename(self.selected_image_path)
            popup.dismiss()

        def cancel(*args):
            popup.dismiss()

        layout = MDBoxLayout(orientation='vertical', spacing='10dp', padding='10dp')
        layout.add_widget(filechooser)
        button_box = MDBoxLayout(orientation='horizontal', size_hint_y=None, height=dp(48), spacing='10dp')
        button_box.add_widget(MDButton(MDButtonText(text="Выбрать"), on_release=select))
        button_box.add_widget(MDButton(MDButtonText(text="Отмена"), on_release=cancel))
        layout.add_widget(button_box)
        popup = Popup(title="Выберите изображение", content=layout, size_hint=(0.9, 0.9))
        popup.open()

    def _get_image_source(self):
        app = MDApp.get_running_app()
        images_dir = os.path.join(app.user_data_dir, 'images')
        user_path = os.path.join(images_dir, f"{self.game_id}.jpg")
        if os.path.exists(user_path):
            return user_path
        else:
            # Для встроенных изображений используем resource_path
            # Функцию resource_path нужно импортировать (лучше вынести в utils)
            return resource_path(f'assets/{self.game_id}.jpg')
