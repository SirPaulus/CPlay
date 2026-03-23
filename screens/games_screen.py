from kivy.logger import Logger
from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.chip import MDChip, MDChipText
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from models.database import fetch_games_by_criteria, get_all_genres, get_all_platforms, get_current_user
from widgets.game_card import GameCard


class GamesScreen(MDScreen):
    def on_enter(self):
        self.check_role()
        self.create_chips()
        self.load_games()

    def check_role(self):
        self.ids.admin_button.clear_widgets()
        if get_current_user()['role'] == 'admin':
            edit_button = MDButton(
                MDButtonIcon(
                    pos_hint={"center_x": .3, "center_y": .5},
                    icon="pencil",
                ),
                MDButtonText(
                    id='text',
                    text="Редактировать Игры",
                    pos_hint={"center_x": .5, "center_y": .5},
                ),
                style="elevated",
                theme_width="Custom",
                size_hint_x=1,
                pos_hint={"center_x": 0.5, "center_y": 0.5},
                on_release=lambda x: self.open_admin(),
            )
            self.ids.admin_button.add_widget(edit_button)

    def create_chips(self):
        self.ids.genres_chips.clear_widgets()
        self.ids.platforms_chips.clear_widgets()
        genres = [genre['name'] for genre in get_all_genres()]
        platforms = [platform['name'] for platform in get_all_platforms()]

        for genre in genres:
            # Создаем chip как контейнер с дочерним текстом
            chip = MDChip(
                MDChipText(text=genre),  # <-- Обязательный дочерний элемент
                type="filter",  # Указываем тип filter
                selected_color=self.theme_cls.primaryColor,  # Цвет в активном состоянии
                # Опционально: можно задать свои цвета фона
                # theme_bg_color="Custom",
                # md_bg_color="#303A29",
            )
            # Привязываем обработчик изменения активного состояния
            chip.bind(active=self.on_chip_active)
            # Сохраняем тип и значение в самом чипе для удобства
            chip.filter_type = 'genre'
            chip.filter_value = genre
            self.ids.genres_chips.add_widget(chip)

        for platform in platforms:
            chip = MDChip(
                MDChipText(text=platform),
                type="filter",
                selected_color=self.theme_cls.primaryColor,
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

    def apply_filters(self):
        """Собирает все активные чипы и обновляет список игр."""
        selected_genres = []
        selected_platforms = []

        # Собираем жанры
        for chip in self.ids.genres_chips.children:
            if chip.active:
                selected_genres.append(chip.filter_value)

        # Собираем платформы
        for chip in self.ids.platforms_chips.children:
            if chip.active:
                selected_platforms.append(chip.filter_value)

        self.load_games(selected_genres, selected_platforms)

    def load_games(self, genres=None, platforms=None):
        games = fetch_games_by_criteria(genres, platforms)
        self.ids.games_list.clear_widgets()
        for game in games:
            item = GameCard(
                title=game['title'],
                genres=game['genres'],
                date=game['created_at'][:10],
                rating=str(game['rating']),
                platforms=game['platforms'],
                source=f"./assets/{game['id']}.jpg"
            )
            self.ids.games_list.add_widget(item)

    def open_admin(self):
        self.manager.current = 'admin'
