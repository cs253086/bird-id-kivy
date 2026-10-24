[app]

title = Bird ID
package.name = birdid
package.domain = org.example
source.dir = .
source.include_exts = py,kv,png,jpg,txt,tflite
version = 0.1

requirements = python3,kivy==2.3.0,pillow,numpy

orientation = portrait
fullscreen = 0

android.permissions = CAMERA
android.archs = arm64-v8a
android.api = 33
android.minapi = 24

[buildozer]
log_level = 2
warn_on_root = 1
