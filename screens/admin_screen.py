from kivymd.uix.screen import MDScreen
from models.database import fetch_games_by_criteria
from widgets.game_card import GameCard

class AdminScreen(MDScreen):
    def on_enter(self):
        self.load_games()

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