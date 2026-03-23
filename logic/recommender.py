"""
Модуль с логикой рекомендаций.
Сейчас использует простой SQL-запрос, но здесь можно реализовать более сложные алгоритмы.
"""

from models.database import fetch_games_by_criteria


def recommend_games(selected_genres, selected_platforms):
    """
    Возвращает список игр, соответствующих выбранным жанрам и платформам.
    В будущем здесь можно добавить сортировку по релевантности, коллаборативную фильтрацию и т.д.
    """
    if not selected_genres and not selected_platforms:
        # Если ничего не выбрано, можно вернуть все игры или пустой список
        return fetch_games_by_criteria()  # все игры
    return fetch_games_by_criteria(selected_genres, selected_platforms)