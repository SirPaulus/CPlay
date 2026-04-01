name: Build Android APK

on:
  push:
    branches: [ main, master ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: kivy/buildozer:latest
      # НЕ указываем --user, по умолчанию запуск от root
    steps:
      - uses: actions/checkout@v4
      - name: Build APK
        run: buildozer android debug --verbose
        env:
          BUILDOZER_IGNORE_ROOT: 1   # отключает запрос подтверждения
      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: CPlay-APK
          path: bin/*.apk
