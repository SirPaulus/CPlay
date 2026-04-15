# CPlay

Приложение для подбора видеоигр.

## Установка зависимостей

Перед запуском убедитесь, что у вас установлен Python и pip. Затем выполните команду для установки необходимых библиотек:

```bash
pip install -r requirements.txt
```
## Запуск

Для запуска программы используйте команду:
```bash
python main.py
```

# Инструкция по сборке Windows-версии приложения CPlay через PyInstaller

## 1. Подготовка окружения

1. Убедитесь, что у вас установлен **Python 3.9–3.12** (рекомендуется 3.11).
2. Откройте командную строку (cmd) или PowerShell в папке проекта `CPlay/`.
3. Создайте и активируйте виртуальное окружение (рекомендуется):
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows cmd
   ```
4. Установите все зависимости:
   ```bash
   pip install -r requirements.txt
   ```

## 2. Установка PyInstaller и дополнительных модулей

```bash
pip install pyinstaller
pip install kivy_deps.sdl2 kivy_deps.glew
```

## 3. Сборка приложения

Выполните в терминале:

```bash
pyinstaller CPlay.spec --clean
```

Процесс займёт 1–3 минуты. Готовый исполняемый файл появится в папке `dist/CPlay.exe`.
