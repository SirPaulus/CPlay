import sqlite3
import os
import shutil
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'games.db')
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', 'assets')

# Глобальная переменная для хранения текущего пользователя
_current_user = None


def get_connection():
    return sqlite3.connect(DB_PATH)


def init_db():
    """Создаёт все таблицы и заполняет начальными данными."""
    conn = get_connection()
    c = conn.cursor()

    # Таблица ролей
    c.execute('''CREATE TABLE IF NOT EXISTS roles
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL)''')
    # Добавляем роли, если их нет
    c.execute("INSERT OR IGNORE INTO roles (name) VALUES ('user'), ('admin')")

    # Таблица пользователей
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL,
                  role_id INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  FOREIGN KEY (role_id) REFERENCES roles(id))''')

    # Таблица жанров
    c.execute('''CREATE TABLE IF NOT EXISTS genres
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL)''')

    # Таблица платформ
    c.execute('''CREATE TABLE IF NOT EXISTS platforms
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  name TEXT UNIQUE NOT NULL)''')

    # Таблица игр (добавлено поле created_at)
    c.execute('''CREATE TABLE IF NOT EXISTS games
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  title TEXT NOT NULL,
                  description TEXT,
                  rating REAL,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

    # Связующие таблицы
    c.execute('''CREATE TABLE IF NOT EXISTS game_genres
                 (game_id INTEGER,
                  genre_id INTEGER,
                  FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                  FOREIGN KEY (genre_id) REFERENCES genres(id) ON DELETE CASCADE,
                  PRIMARY KEY (game_id, genre_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS game_platforms
                 (game_id INTEGER,
                  platform_id INTEGER,
                  FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE,
                  FOREIGN KEY (platform_id) REFERENCES platforms(id) ON DELETE CASCADE,
                  PRIMARY KEY (game_id, platform_id))''')

    c.execute('''CREATE TABLE IF NOT EXISTS favorites
                 (user_id INTEGER,
                  game_id INTEGER,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                  PRIMARY KEY (user_id, game_id),
                  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                  FOREIGN KEY (game_id) REFERENCES games(id) ON DELETE CASCADE)''')

    # Заполняем жанры и платформы, если таблицы пусты
    AVAILABLE_GENRES = ['RPG', 'Action', 'Adventure', 'Sandbox', 'Survival',
                        'Party', 'Social Deduction', 'FPS', 'Simulation']
    AVAILABLE_PLATFORMS = ['PC', 'PS', 'Xbox', 'Switch', 'Mobile']

    for genre in AVAILABLE_GENRES:
        c.execute("INSERT OR IGNORE INTO genres (name) VALUES (?)", (genre,))
    for platform in AVAILABLE_PLATFORMS:
        c.execute("INSERT OR IGNORE INTO platforms (name) VALUES (?)", (platform,))

    # Добавляем тестовые игры, если таблица games пуста
    c.execute("SELECT COUNT(*) FROM games")
    if c.fetchone()[0] == 0:
        # Сначала добавляем игры
        sample_games = [
            ("The Witcher 3", "Open world RPG about a monster slayer", 9.5),
            ("Minecraft", "Build and survive in a blocky world", 9.0),
            ("Among Us", "Multiplayer game of teamwork and betrayal", 8.0),
            ("Doom Eternal", "Fast-paced first-person shooter", 9.2),
            ("Stardew Valley", "Farming simulation with RPG elements", 9.0)
        ]
        for title, desc, rating in sample_games:
            c.execute("INSERT INTO games (title, description, rating) VALUES (?,?,?)",
                      (title, desc, rating))
            game_id = c.lastrowid

            # Привязываем жанры и платформы (для демо используем упрощённое соответствие)
            if title == "The Witcher 3":
                genre_names = ['RPG', 'Action', 'Adventure']
                platform_names = ['PC', 'PS4', 'Xbox One']
            elif title == "Minecraft":
                genre_names = ['Sandbox', 'Survival']
                platform_names = ['PC', 'PS4', 'Xbox One', 'Switch', 'Mobile']
            elif title == "Among Us":
                genre_names = ['Party', 'Social Deduction']
                platform_names = ['PC', 'Switch', 'Mobile']
            elif title == "Doom Eternal":
                genre_names = ['Action', 'FPS']
                platform_names = ['PC', 'PS4', 'Xbox One', 'Switch']
            elif title == "Stardew Valley":
                genre_names = ['Simulation', 'RPG']
                platform_names = ['PC', 'PS4', 'Xbox One', 'Switch', 'Mobile']
            else:
                continue

            # Получаем id жанров и добавляем связи
            for gname in genre_names:
                c.execute("SELECT id FROM genres WHERE name=?", (gname,))
                genre_id = c.fetchone()
                if genre_id:
                    c.execute("INSERT INTO game_genres (game_id, genre_id) VALUES (?,?)",
                              (game_id, genre_id[0]))

            for pname in platform_names:
                c.execute("SELECT id FROM platforms WHERE name=?", (pname,))
                platform_id = c.fetchone()
                if platform_id:
                    c.execute("INSERT INTO game_platforms (game_id, platform_id) VALUES (?,?)",
                              (game_id, platform_id[0]))

    conn.commit()
    conn.close()


# ========== Функции для работы с пользователями ==========

def register_user(username, password, role_name='user'):
    """Регистрирует нового пользователя с указанной ролью (по умолчанию 'user')."""
    conn = get_connection()
    c = conn.cursor()
    try:
        # Получаем id роли
        c.execute("SELECT id FROM roles WHERE name=?", (role_name,))
        role = c.fetchone()
        if not role:
            return False
        role_id = role[0]

        c.execute("INSERT INTO users (username, password, role_id) VALUES (?,?,?)",
                  (username, password, role_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def login_user(username, password):
    """Проверяет логин и пароль, возвращает словарь с данными пользователя или None."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT users.id, users.username, roles.name as role
        FROM users
        JOIN roles ON users.role_id = roles.id
        WHERE users.username=? AND users.password=?
    ''', (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        return {'id': user[0], 'username': user[1], 'role': user[2]}
    return None


def set_current_user(user):
    global _current_user
    _current_user = user


def get_current_user():
    return _current_user


# ========== Функции для работы с играми ==========

def add_to_favorites(user_id: int, game_id: int) -> bool:
    """Добавляет игру в избранное пользователя."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO favorites (user_id, game_id) VALUES (?, ?)", (user_id, game_id))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Уже есть в избранном
        return False
    finally:
        conn.close()


def remove_from_favorites(user_id: int, game_id: int) -> bool:
    """Удаляет игру из избранного пользователя."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM favorites WHERE user_id=? AND game_id=?", (user_id, game_id))
    affected = c.rowcount
    conn.commit()
    conn.close()
    return affected > 0


def is_favorite(user_id: int, game_id: int) -> bool:
    """Проверяет, находится ли игра в избранном у пользователя."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM favorites WHERE user_id=? AND game_id=?", (user_id, game_id))
    exists = c.fetchone() is not None
    conn.close()
    return exists


def get_favorite_games(user_id: int, genres=None, platforms=None, search=None):
    """
    Возвращает список игр из избранного пользователя с возможностью фильтрации и поиска.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT game_id FROM favorites WHERE user_id=?", (user_id,))
    favorite_ids = [row[0] for row in c.fetchall()]
    conn.close()
    if not favorite_ids:
        return []
    return _fetch_games_by_ids(favorite_ids, genres, platforms, search)


def _fetch_games_by_ids(game_ids, genres=None, platforms=None, search=None):
    """Вспомогательная функция для получения игр по списку id с фильтрацией и поиском."""
    if not game_ids:
        return []
    conn = get_connection()
    c = conn.cursor()
    placeholders = ','.join('?' * len(game_ids))
    query = f'''
        SELECT DISTINCT games.id, games.title, games.description, games.rating, games.created_at,
               GROUP_CONCAT(DISTINCT genres.name) as genre_names,
               GROUP_CONCAT(DISTINCT platforms.name) as platform_names
        FROM games
        LEFT JOIN game_genres ON games.id = game_genres.game_id
        LEFT JOIN genres ON game_genres.genre_id = genres.id
        LEFT JOIN game_platforms ON games.id = game_platforms.game_id
        LEFT JOIN platforms ON game_platforms.platform_id = platforms.id
        WHERE games.id IN ({placeholders})
    '''
    params = list(game_ids)

    if genres:
        query += " AND games.id IN (SELECT game_id FROM game_genres JOIN genres ON game_genres.genre_id = genres.id WHERE genres.name IN ("
        query += ",".join(["?"] * len(genres))
        query += "))"
        params.extend(genres)

    if platforms:
        query += " AND games.id IN (SELECT game_id FROM game_platforms JOIN platforms ON game_platforms.platform_id = platforms.id WHERE platforms.name IN ("
        query += ",".join(["?"] * len(platforms))
        query += "))"
        params.extend(platforms)

    if search:
        query += " AND games.title LIKE ?"
        params.append(f"%{search}%")

    query += " GROUP BY games.id ORDER BY games.rating DESC"

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    games = []
    for row in rows:
        games.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'rating': row[3],
            'created_at': row[4],
            'genres': row[5].split(',') if row[5] else [],
            'platforms': row[6].split(',') if row[6] else []
        })
    return games


def fetch_games_by_criteria(genres=None, platforms=None, search=None):
    """
    Возвращает список игр, соответствующих указанным жанрам, платформам и поисковому запросу.
    Параметры genres и platforms — списки названий (строк).
    Если списки пусты, возвращаются все игры.
    search — строка для поиска по названию игры (регистронезависимо).
    """
    conn = get_connection()
    c = conn.cursor()

    query = '''
        SELECT DISTINCT games.id, games.title, games.description, games.rating, games.created_at,
               GROUP_CONCAT(DISTINCT genres.name) as genre_names,
               GROUP_CONCAT(DISTINCT platforms.name) as platform_names
        FROM games
        LEFT JOIN game_genres ON games.id = game_genres.game_id
        LEFT JOIN genres ON game_genres.genre_id = genres.id
        LEFT JOIN game_platforms ON games.id = game_platforms.game_id
        LEFT JOIN platforms ON game_platforms.platform_id = platforms.id
        WHERE 1=1
    '''
    params = []

    if genres:
        query += " AND games.id IN (SELECT game_id FROM game_genres JOIN genres ON game_genres.genre_id = genres.id WHERE genres.name IN ("
        query += ",".join(["?"] * len(genres))
        query += "))"
        params.extend(genres)

    if platforms:
        query += " AND games.id IN (SELECT game_id FROM game_platforms JOIN platforms ON game_platforms.platform_id = platforms.id WHERE platforms.name IN ("
        query += ",".join(["?"] * len(platforms))
        query += "))"
        params.extend(platforms)

    if search:
        query += " AND games.title LIKE ?"
        params.append(f"%{search}%")

    query += " GROUP BY games.id ORDER BY games.rating DESC"

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    games = []
    for row in rows:
        games.append({
            'id': row[0],
            'title': row[1],
            'description': row[2],
            'rating': row[3],
            'created_at': row[4],
            'genres': row[5].split(',') if row[5] else [],
            'platforms': row[6].split(',') if row[6] else []
        })
    return games


def add_game(title, description, rating, genre_ids, platform_ids):
    """Добавляет новую игру с привязкой к жанрам и платформам."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO games (title, description, rating) VALUES (?,?,?)",
                  (title, description, rating))
        game_id = c.lastrowid

        for gid in genre_ids:
            c.execute("INSERT INTO game_genres (game_id, genre_id) VALUES (?,?)", (game_id, gid))
        for pid in platform_ids:
            c.execute("INSERT INTO game_platforms (game_id, platform_id) VALUES (?,?)", (game_id, pid))

        conn.commit()
        return game_id
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def db_delete_game(game_id):
    """Удаляет игру и все связи (каскадно)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM games WHERE id=?", (game_id,))
    conn.commit()
    conn.close()
    delete_game_image(game_id)


def get_all_genres():
    """Возвращает список всех жанров (id, name)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name FROM genres ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1]} for row in rows]


def get_all_platforms():
    """Возвращает список всех платформ (id, name)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT id, name FROM platforms ORDER BY name")
    rows = c.fetchall()
    conn.close()
    return [{'id': row[0], 'name': row[1]} for row in rows]


def get_game_by_id(game_id):
    """Возвращает игру по id со всеми связями (включая названия жанров и платформ)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT games.id, games.title, games.description, games.rating, games.created_at
        FROM games
        WHERE games.id = ?
    ''', (game_id,))
    game = c.fetchone()
    if not game:
        return None

    # Получаем названия жанров
    c.execute('''
        SELECT genres.name FROM game_genres
        JOIN genres ON game_genres.genre_id = genres.id
        WHERE game_genres.game_id = ?
    ''', (game_id,))
    genres = [row[0] for row in c.fetchall()]

    # Получаем названия платформ
    c.execute('''
        SELECT platforms.name FROM game_platforms
        JOIN platforms ON game_platforms.platform_id = platforms.id
        WHERE game_platforms.game_id = ?
    ''', (game_id,))
    platforms = [row[0] for row in c.fetchall()]

    # Получаем id жанров и платформ (для редактирования)
    c.execute('SELECT genre_id FROM game_genres WHERE game_id = ?', (game_id,))
    genre_ids = [row[0] for row in c.fetchall()]

    c.execute('SELECT platform_id FROM game_platforms WHERE game_id = ?', (game_id,))
    platform_ids = [row[0] for row in c.fetchall()]

    conn.close()
    return {
        'id': game[0],
        'title': game[1],
        'description': game[2],
        'rating': game[3],
        'created_at': game[4],
        'genres': genres,
        'platforms': platforms,
        'genre_ids': genre_ids,
        'platform_ids': platform_ids
    }


def update_game(game_id, title, description, rating, genre_ids, platform_ids):
    """Обновляет игру и её связи."""
    conn = get_connection()
    c = conn.cursor()
    try:
        c.execute("UPDATE games SET title=?, description=?, rating=? WHERE id=?",
                  (title, description, rating, game_id))
        # Удаляем старые связи
        c.execute("DELETE FROM game_genres WHERE game_id=?", (game_id,))
        c.execute("DELETE FROM game_platforms WHERE game_id=?", (game_id,))
        # Добавляем новые
        for gid in genre_ids:
            c.execute("INSERT INTO game_genres (game_id, genre_id) VALUES (?,?)", (game_id, gid))
        for pid in platform_ids:
            c.execute("INSERT INTO game_platforms (game_id, platform_id) VALUES (?,?)", (game_id, pid))
        conn.commit()
        return True
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()


def save_game_image(game_id, image_path):
    """
    Копирует выбранное изображение в папку assets и переименовывает в <game_id>.jpg.
    Если image_path пуст или None, ничего не делает.
    """
    if not image_path or not os.path.exists(image_path):
        return False
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    target_path = os.path.join(assets_dir, f"{game_id}.jpg")
    try:
        shutil.copy2(image_path, target_path)
        return True
    except Exception as e:
        print(f"Ошибка копирования изображения: {e}")
        return False


def delete_game_image(game_id):
    """Удаляет изображение игры, если оно существует."""
    assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets')
    image_path = os.path.join(assets_dir, f"{game_id}.jpg")
    if os.path.exists(image_path):
        try:
            os.remove(image_path)
            return True
        except Exception as e:
            print(f"Ошибка удаления изображения {image_path}: {e}")
            return False
    return False
