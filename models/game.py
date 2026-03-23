"""
Класс Game для представления игры.
Может быть использован для более сложной логики (например, векторизация).
"""

class Game:
    def __init__(self, title, genres, platforms, description, rating):
        self.title = title
        self.genres = genres.split(',') if genres else []
        self.platforms = platforms.split(',') if platforms else []
        self.description = description
        self.rating = rating

    @classmethod
    def from_db_row(cls, row):
        """Создаёт объект Game из строки БД (кортежа)."""
        return cls(
            title=row[0],
            genres=row[1],
            platforms=row[2],
            description=row[3],
            rating=row[4]
        )

    def __repr__(self):
        return f"<Game {self.title}>"