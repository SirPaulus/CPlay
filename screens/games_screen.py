from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.chip import MDChip, MDChipText, MDChipLeadingIcon
from models.database import fetch_games_by_criteria, get_all_genres, get_all_platforms, get_current_user, add_game, \
    save_game_image
from kivymd.uix.appbar import MDActionTopAppBarButton
from widgets.game_card import GameCard
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogHeadlineText,
    MDDialogButtonContainer,
    MDDialogContentContainer,
)
from kivy.uix.widget import Widget
from kivymd.uix.label import MDLabel
from kivymd.uix.stacklayout import MDStackLayout
from kivymd.uix.textfield import (
    MDTextField,
    MDTextFieldHintText,
    MDTextFieldHelperText,
)
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.popup import Popup
from kivymd.uix.button import MDButton, MDButtonText
import os


class GamesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_game_button = None
        self.search_text = ''
        self.selected_image_path = None

    def on_enter(self):
        self.admin_button()
        self.create_chips()
        self.load_games()

    def admin_button(self):
        if self.add_game_button:
            self.ids.rec_top_bar_trail.remove_widget(self.add_game_button)
            self.add_game_button = None
        if get_current_user()['role'] == 'admin':
            self.add_game_button = MDActionTopAppBarButton(
                icon="plus",
                theme_icon_color="Custom",
                icon_color="#ffffff",
                on_release=lambda x: self.show_add_game_dialog()
            )
            self.ids.rec_top_bar_trail.add_widget(self.add_game_button)

    def create_chips(self):
        self.ids.genres_chips.clear_widgets()
        self.ids.platforms_chips.clear_widgets()
        genres = [genre['name'] for genre in get_all_genres()]
        platforms = [platform['name'] for platform in get_all_platforms()]

        for genre in genres:
            # Создаем chip как контейнер с дочерним текстом
            chip = MDChip(
                MDChipLeadingIcon(),
                MDChipText(text=genre, theme_text_color="Custom", text_color="#ffffff"),
                type="filter",  # Указываем тип filter
                selected_color=(.25, .62, .63, 0.8),  # Цвет в активном состоянии
                # Опционально: можно задать свои цвета фона
                theme_bg_color="Custom",
                md_bg_color=(.15, .37, .63, 0.8),
            )
            # Привязываем обработчик изменения активного состояния
            chip.bind(active=self.on_chip_active)
            # Сохраняем тип и значение в самом чипе для удобства
            chip.filter_type = 'genre'
            chip.filter_value = genre
            self.ids.genres_chips.add_widget(chip)

        for platform in platforms:
            chip = MDChip(
                MDChipLeadingIcon(),
                MDChipText(text=platform, theme_text_color="Custom", text_color="#ffffff"),
                type="filter",
                selected_color=(.25, .62, .63, 0.8),
                theme_bg_color="Custom",
                md_bg_color=(.15, .37, .63, 0.8),
            )
            chip.bind(active=self.on_chip_active)
            chip.filter_type = 'platform'
            chip.filter_value = platform
            self.ids.platforms_chips.add_widget(chip)

    def on_chip_active(self, chip, active):
        """Вызывается при изменении состояния любого чипа."""
        self.apply_filters()

    def on_chip_toggle(self, value, is_active):
        """Вызывается при изменении состояния любого чипа."""
        # Здесь value - это жанр или платформа, is_active - bool
        # Нужно обновить списки фильтров и перезагрузить игры
        # Для простоты будем собирать все активные чипы заново при каждом изменении
        self.apply_filters()

    def on_search_text(self, text):
        self.search_text = text
        self.apply_filters()

    def apply_filters(self):
        """Собирает все активные чипы и обновляет список игр."""
        selected_genres = []
        selected_platforms = []
        for chip in self.ids.genres_chips.children:
            if chip.active:
                selected_genres.append(chip.filter_value)
        for chip in self.ids.platforms_chips.children:
            if chip.active:
                selected_platforms.append(chip.filter_value)

        search_query = self.ids.search_field.text if hasattr(self.ids, 'search_field') else ''
        self.load_games(selected_genres, selected_platforms, search_query)

    def load_games(self, genres=None, platforms=None, search=None):
        games = fetch_games_by_criteria(genres, platforms, search)
        self.ids.games_list.clear_widgets()
        for game in games:
            item = GameCard(
                game_id=game['id'],
                title=game['title'],
                genres=game['genres'],
                date=game['created_at'][:10],
                rating=str(game['rating']),
                platforms=game['platforms'],
                source=f"./assets/{game['id']}.jpg",
                on_delete_callback=self.load_games
            )
            self.ids.games_list.add_widget(item)

    def show_add_game_dialog(self):
        all_genres = get_all_genres()
        all_platforms = get_all_platforms()

        # Контейнер с прокруткой
        scroll = MDScrollView(size_hint_y=None, height=dp(500), do_scroll_x=False)
        inner_layout = MDBoxLayout(
            orientation='vertical',
            spacing='12dp',
            padding='10dp',
            adaptive_height=True,
        )
        scroll.add_widget(inner_layout)

        # Поля ввода
        title_field = MDTextField(
            MDTextFieldHintText(text='Название'),
            MDTextFieldHelperText(text='', mode='on_error'),
            mode='outlined',
        )
        desc_field = MDTextField(
            MDTextFieldHintText(text='Описание'),
            MDTextFieldHelperText(text='', mode='on_error'),
            mode='outlined',
        )
        rating_field = MDTextField(
            MDTextFieldHintText(text='Рейтинг (0-10)'),
            MDTextFieldHelperText(text='', mode='on_error'),
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
            adaptive_height=False,
        )
        image_filename_label = MDLabel(
            text="Файл не выбран",
            theme_text_color="Custom",
            text_color=(0.7, 0.7, 0.7, 1),
            size_hint_x=0.7,
            halign='left',
        )
        choose_image_btn = MDButton(
            MDButtonText(text="Выбрать изображение"),
            on_release=lambda x: self.choose_image(image_filename_label)
        )
        image_selection_layout.add_widget(image_filename_label)
        image_selection_layout.add_widget(choose_image_btn)
        inner_layout.add_widget(image_selection_layout)

        # --- Выбор жанров (чипы с типом filter) ---
        genre_box = MDBoxLayout(orientation='vertical', spacing='8dp', adaptive_height=True)
        genre_box.add_widget(Widget(size_hint_y=None, height=dp(24)))
        genre_box.add_widget(MDLabel(text='Жанры', font_style='Title'))
        genre_chips = MDStackLayout(spacing='8dp', adaptive_height=True)
        genre_chips.bind(minimum_height=genre_chips.setter('height'))
        genre_box.add_widget(genre_chips)

        selected_genres = []  # список id выбранных жанров
        for g in all_genres:
            chip = MDChip(
                MDChipText(text=g['name']),
                type="filter",
                selected_color="green",
                active=False,
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

        selected_platforms = []  # список id выбранных платформ
        for p in all_platforms:
            chip = MDChip(
                MDChipText(text=p['name']),
                type="filter",
                selected_color="green",
                active=False,
                size_hint=(None, None),
                width=dp(100),
                height=dp(32)
            )
            chip.bind(
                active=lambda instance, value, pid=p['id']: self._toggle_selection(selected_platforms, pid, value))
            platform_chips.add_widget(chip)

        inner_layout.add_widget(platform_box)

        # Диалог
        self._add_dialog = MDDialog(
            MDDialogHeadlineText(text='Добавление игры'),
            MDDialogContentContainer(scroll),
            MDDialogButtonContainer(
                MDButton(
                    MDButtonText(text='Отмена'),
                    style='text',
                    on_release=lambda x: self._add_dialog.dismiss()
                ),
                MDButton(
                    MDButtonText(text='Сохранить'),
                    on_release=lambda x: self._save_new_game(
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
        self._add_dialog.open()

    def _toggle_selection(self, selected_list, item_id, active):
        """Вспомогательная функция для переключения выбранных жанров/платформ."""
        if active:
            if item_id not in selected_list:
                selected_list.append(item_id)
        else:
            if item_id in selected_list:
                selected_list.remove(item_id)

    def _save_new_game(self, title_field, desc_field, rating_field, selected_genres, selected_platforms):
        """Сохраняет новую игру с валидацией."""
        error = False

        title = title_field.text.strip()
        if not title:
            title_field.error = True
            error = True
        else:
            title_field.error = False

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
            game_id = add_game(title, desc_field.text, rating_val, selected_genres, selected_platforms)

            if hasattr(self, 'selected_image_path') and self.selected_image_path:
                save_game_image(game_id, self.selected_image_path)

            if hasattr(self, '_add_dialog') and self._add_dialog:
                self._add_dialog.dismiss()
                self._add_dialog = None

            self.load_games()

            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            snackbar = MDSnackbar(
                MDSnackbarText(text='Игра добавлена'),
                duration=2
            )
            snackbar.open()
        except Exception as e:
            print(f'Ошибка при добавлении: {e}')
            from kivymd.uix.snackbar import MDSnackbar, MDSnackbarText
            snackbar = MDSnackbar(
                MDSnackbarText(text='Ошибка добавления'),
                duration=2
            )
            snackbar.open()

    def choose_image(self, filename_label):
        """Открывает диалог выбора файла изображения."""

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
