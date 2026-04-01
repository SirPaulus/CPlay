[app]

# (str) Title of your application
title = CPlay

# (str) Package name
package.name = cplay

# (str) Package domain (needed for android/ios packaging)
package.domain = com.example

# (str) Version of the application
version = 1.0.0

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,ttf,txt,db

# (list) Requirements
requirements = python3,kivy==2.3.1,kivymd==2.0.1,asynckivy

# (str) Android API to use (default: 31)
android.api = 31

# (int) Minimum API required (default: 21)
android.minapi = 21

# (str) Android NDK version to use
android.ndk = 23b

# (bool) Enable AndroidX (required for KivyMD)
android.enable_androidx = True

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (str) Presplash image (optional)
# android.presplash = presplash.png

# (str) Icon (optional)
# android.icon = icon.png

# (list) Architectures to build for (arm64-v8a, armeabi-v7a, x86, x86_64)
android.arch = arm64-v8a

# (list) Gradle dependencies (if needed)
android.gradle_dependencies = 'androidx.appcompat:appcompat:1.4.1'

# (str) Supported orientation (portrait, landscape, all)
orientation = portrait

# (bool) Allow copy of the source code to the device
fullscreen = 0

# (bool) Allow background activity
wakelock = False

# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (str) Additional Java classes to include
android.add_src = assets,data

# (str) Additional Android manifest elements
# android.manifest_application_attributes = 'android:requestLegacyExternalStorage="true"'
