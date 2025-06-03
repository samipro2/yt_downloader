[app]
title = YouTube Downloader Pro
package.name = ytdownloaderpro
package.domain = com.hamzasami.ytdownloader
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,txt
version = 1.0
requirements = python3,kivy==2.1.0,yt-dlp,certifi,urllib3,requests,pycryptodome,websockets,mutagen
icon.filename = icon.png
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.private_storage = False
android.archs = arm64-v8a, armeabi-v7a
android.allow_backup = True

[buildozer]
log_level = 2
warn_on_root = 1
