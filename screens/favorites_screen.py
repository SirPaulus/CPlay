from kivy.metrics import dp
from kivymd.uix.screen import MDScreen
from kivymd.uix.chip import MDChip, MDChipText, MDChipLeadingIcon
from kivymd.uix.button import MDButton, MDButtonIcon, MDButtonText
from models.database import get_favorite_games, get_all_genres, get_all_platforms, get_current_user, add_game
from kivymd.uix.appbar import MDActionTopAppBarButton
from widgets.game_card import GameCard
from kivymd.uix.label import MDLabel



class FavoritesScreen(MDScreen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.search_text = ""

    def on_enter(self):
        self.create_chips()
        self.load_games()

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

        # Собираем жанры
        for chip in self.ids.genres_chips.children:
            if chip.active:
                selected_genres.append(chip.filter_value)

        # Собираем платформы
        for chip in self.ids.platforms_chips.children:
            if chip.active:
                selected_platforms.append(chip.filter_value)

        self.load_games(selected_genres, selected_platforms, self.search_text)

    def load_games(self, genres=None, platforms=None, search=None):
        user = get_current_user()
        self.ids.favorites_list.clear_widgets()
        games = get_favorite_games(user['id'], genres, platforms, search)
        for game in games:
            item = GameCard(
                game_id=game['id'],
                title=game['title'],
                genres=game['genres'],
                date=game['created_at'][:10],
                rating=str(game['rating']),
                platforms=game['platforms'],
                source=f"./assets/{game['id']}.jpg",
                on_delete_callback=self.load_games,
                on_favorite_callback=self.load_games
            )
            self.ids.favorites_list.add_widget(item)
