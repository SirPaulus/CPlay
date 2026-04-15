# Документация проекта CPlay

## Обзор

CPlay — это кроссплатформенное приложение на Python с использованием KivyMD для каталога компьютерных игр. Приложение позволяет пользователям просматривать игры, фильтровать по жанрам и платформам, добавлять в избранное (для зарегистрированных пользователей), а администраторам — добавлять, редактировать и удалять игры. Данные хранятся в SQLite базе данных.

**Ключевые особенности:**
- Ролевая модель: `user`, `admin`, `guest`.
- Изображения игр сохраняются во внутреннее хранилище приложения (`user_data_dir/images/`), доступное для записи.
- Для корректной работы путей к ресурсам (изображения, KV-файлы) в собранном приложении (Windows `.exe`) используется универсальная функция `resource_path` из `utils/path_utils.py`.
- Поддержка сборки для Windows (через PyInstaller).

---

## Структура проекта

```
CPlay/
├── main.py                      # Точка входа, инициализация приложения
├── screens/                     # Экранные классы
│   ├── login_screen.py
│   ├── register_screen.py
│   ├── games_screen.py
│   └── favorites_screen.py
├── models/
│   └── database.py              # Работа с БД, функции для игр, пользователей, избранного, изображений
├── kv/                          # KV-файлы интерфейсов
│   ├── login.kv
│   ├── register.kv
│   ├── games.kv
│   ├── favorites.kv
│   └── game.kv
├── widgets/
│   └── game_card.py             # Виджет карточки игры
├── utils/
│   ├── auth.py                  # Хэширование паролей
│   └── path_utils.py            # Функция resource_path для работы с ресурсами в сборках
├── assets/                      # Статические ресурсы (фон, иконки, стандартные изображения)
│   ├── background.png
│   ├── cplay.png
│   ├── icon.png
│   └── 1.jpg, 2.jpg, ...        # Стандартные изображения для игр (по ID)
└── data/                        # Папка для базы данных (только для разработки, в сборке БД создаётся в user_data_dir)
```

---

## 1. main.py – CPlayApp

### Класс `CPlayApp` (наследуется от `MDApp`)

| Метод | Описание |
|-------|----------|
| `build()` | Строит интерфейс: загружает KV-файлы, инициализирует БД, создаёт ScreenManager, NavigationDrawer, BottomSheet. Возвращает корневой `MDNavigationLayout`. |
| `load_kv_files()` | Обходит папку `kv/` и загружает все `.kv` файлы через `Builder.load_file()`. |
| `init_database()` | Проверяет существование БД по пути `get_db_path()`, если нет – вызывает `init_db()`. |
| `is_admin()` | Возвращает `True`, если текущий пользователь имеет роль `admin`. |
| `update_navigation_menu()` | Обновляет содержимое навигационного ящика в зависимости от роли пользователя. |
| `logout()` | Очищает текущего пользователя, обновляет меню, переключает экран на `login` и закрывает drawer. |
| `switch_to_screen(screen_name)` | Переключает экран и закрывает drawer. |
| `open_add_game()` | Вызывает метод показа диалога добавления игры на экране `games`. |

**Важно:** В `main.py` также определена (или импортирована) функция `resource_path`, которая используется для получения корректных путей к ресурсам в собранном приложении. В актуальной версии эта функция вынесена в `utils/path_utils.py` и импортируется оттуда.

---

## 2. utils/path_utils.py – универсальная работа с путями

```python
import sys
import os

def resource_path(relative_path):
    """Возвращает абсолютный путь к ресурсу, работая как в разработке, так и в собранном приложении (PyInstaller)."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
```

**Назначение:**  
PyInstaller упаковывают ресурсы во временную папку `_MEIPASS`. Функция `resource_path` автоматически определяет эту папку и возвращает правильный путь к файлу. Используется для загрузки фоновых изображений, логотипов и любых файлов из папки `assets`.

---

## 3. models/database.py – работа с данными

### Глобальные переменные
- `_current_user` – словарь с текущим пользователем (`id`, `username`, `role`).

### Функции работы с БД

| Функция | Описание |
|---------|----------|
| `get_db_path()` | Возвращает путь к базе данных в `user_data_dir/data/games.db`. Если папка не существует – создаёт её. |
| `get_connection()` | Возвращает соединение с SQLite, используя `get_db_path()`. |
| `init_db()` | Создаёт таблицы, роли, жанры, платформы и добавляет тестовые игры (если БД пуста). |

### Пользователи
| Функция | Описание |
|---------|----------|
| `register_user(username, password, role_name='user')` | Регистрирует пользователя. |
| `login_user(username, password)` | Проверяет логин и пароль. |
| `set_current_user(user)`, `get_current_user()` | Управление текущим пользователем. |

### Избранное
| Функция | Описание |
|---------|----------|
| `add_to_favorites(user_id, game_id)` | Добавляет игру в избранное. |
| `remove_from_favorites(user_id, game_id)` | Удаляет из избранного. |
| `is_favorite(user_id, game_id)` | Проверяет наличие. |
| `get_favorite_games(user_id, genres, platforms, search)` | Возвращает список избранных игр с фильтрацией. |

### Игры
| Функция | Описание |
|---------|----------|
| `fetch_games_by_criteria(genres, platforms, search)` | Возвращает список всех игр по фильтрам. |
| `add_game(title, description, rating, genre_ids, platform_ids)` | Добавляет игру, возвращает `game_id`. |
| `get_game_by_id(game_id)` | Возвращает полную информацию об игре (включая списки жанров, платформ и их ID). |
| `update_game(game_id, title, description, rating, genre_ids, platform_ids)` | Обновляет игру и связи. |
| `db_delete_game(game_id)` | Удаляет игру и связанное изображение. |
| `get_all_genres()`, `get_all_platforms()` | Возвращают списки словарей `{'id': ..., 'name': ...}`. |

### Работа с изображениями (изменено для записи в user_data_dir)

| Функция | Описание |
|---------|----------|
| `save_game_image(game_id, image_path)` | Копирует изображение в `app.user_data_dir/images/<game_id>.jpg`. Очищает кэш Kivy по этому пути (`CoreImage._cache.pop`). |
| `delete_game_image(game_id)` | Удаляет изображение из `user_data_dir/images/`. |

**Важно:**  
- на Windows – на `%APPDATA%\cplay`.  
- Благодаря этому пользовательские изображения сохраняются и загружаются корректно на всех платформах.

---

## 4. widgets/game_card.py – карточка игры

### Класс `GameCard` (наследуется от `MDCard`)

**Свойства:**  
`title`, `genres`, `date`, `rating`, `platforms`, `game_id`, `source`, `platforms_display_text`, `platform_icon`.

**Ключевые методы:**

| Метод | Описание |
|-------|----------|
| `__init__(**kwargs)` | Инициализирует карточку, сохраняет колбэки, привязывает обновление отображения платформ. |
| `_get_image_source()` | **Возвращает путь к изображению:** сначала проверяет наличие файла в `user_data_dir/images/<game_id>.jpg`. Если есть – возвращает абсолютный путь (с прямыми слешами). Если нет – возвращает путь через `resource_path(f'assets/{game_id}.jpg')`. Это обеспечивает приоритет пользовательских изображений. |
| `on_kv_post(base_widget)` | После загрузки KV-разметки устанавливает `self.source = self._get_image_source()`, добавляет кнопки администратора/избранного. |
| `open_details(*args)` | Открывает BottomSheet с деталями игры, используя `_get_image_source()` для изображения. |
| `edit_game(*args)` | Открывает диалог редактирования игры. |
| `_save_edit(...)` | Сохраняет изменения, обновляет карточку и изображение. После сохранения вызывает `on_delete_callback` для обновления списка и принудительно перезагружает `poster_image` через `reload()`. |
| `delete_game(*args)` | Подтверждение и удаление игры. |
| `toggle_favorite(instance)` | Переключает избранное для текущего пользователя. |

**Особенности:**  
- Метод `_get_image_source` использует `resource_path` для доступа к встроенным изображениям из `assets`.  
- Для обновления текстуры после замены изображения вызывается `reload()` на виджете `FitImage`.

---

## 5. Экранные классы (screens/)

### LoginScreen
- `try_login()` – аутентификация.
- `guest_login()` – вход без регистрации.
- `go_to_register()` – переход на регистрацию.

### RegisterScreen
- `try_register()` – регистрация нового пользователя.
- `go_to_login()` – возврат к входу.

### GamesScreen
- `create_chips()` – создание чипов фильтров.
- `apply_filters()` – сбор активных чипов и перезагрузка игр.
- `load_games()` – загрузка игр через `fetch_games_by_criteria()` и создание `GameCard`.
- `show_add_game_dialog()` – диалог добавления игры.
- `_save_new_game()` – сохранение новой игры с вызовом `save_game_image()`.

### FavoritesScreen
Аналогичен GamesScreen, но использует `get_favorite_games()` и обновляется по `on_favorite_callback`.

---

## 6. KV-файлы (kv/)

Все KV-файлы используют привязку к свойствам приложения и виджетов. **Важное изменение:** в `games.kv`, `favorites.kv`, `login.kv`, `register.kv` пути к фоновым изображениям и логотипу теперь задаются через `app.background_source` и `app.cplay_logo_source`, которые вычисляются через `resource_path`.

Пример из `games.kv`:
```kv
FitImage:
    source: app.background_source
    size_hint: 1, 1
```

---

## 7. Сборка для Windows (PyInstaller)

### Файл спецификации `CPlay.spec` (основные секции)

```python
from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

# -*- mode: python ; coding: utf-8 -*-

from kivy_deps import sdl2, glew
from kivymd import hooks_path as kivymd_hooks_path

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('kv', 'kv'),               # вся папка kv
        ('assets', 'assets'),       # вся папка assets
        ('data', 'data'),           # вся папка data (БД)
    ],
    hiddenimports=[
        'kivy',
        'kivymd',
        'kivymd.icon_definitions',
        'kivymd.font_definitions',
        'win32timezone',   # <-- решает ошибку FileChooser
        'win32file',
        'win32api',
        'win32con',
        'pywintypes',
        'pythoncom',
        'PIL',             # на всякий случай для изображений
        'PIL.Image',
    ],
    hookspath=[kivymd_hooks_path],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='CPlay',
    debug=False,
    console=False,      # скрыть консоль
    icon='assets/icon.ico',  # убедитесь, что файл существует
    upx=True,
)a = Analysis(
    ['main.py'],
    datas=[
        ('kv', 'kv'),
        ('assets', 'assets'),
        ('data', 'data'),
    ],
    hiddenimports=[
        'kivy', 'kivymd', 'kivymd.icon_definitions', 'kivymd.font_definitions',
        'win32timezone', 'win32file', 'win32api', 'win32con', 'pywintypes', 'pythoncom',
        'PIL', 'PIL.Image',
    ],
    hookspath=[kivymd_hooks_path],
    ...
)

exe = EXE(
    ...,
    *[Tree(p) for p in (sdl2.dep_bins + glew.dep_bins)],
    name='CPlay',
    console=False,
    icon='assets/icon.ico',
)
```

### Сборка

```bash
pyinstaller CPlay.spec --clean
```

**Результат:** `dist/CPlay.exe` – самодостаточный исполняемый файл.

---
