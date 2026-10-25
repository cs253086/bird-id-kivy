# Bird ID

An Android app built with Kivy. Point the camera at a real bird or a picture of one, press **Identify bird**, and the app shows the most likely species.

## Layout

| File | Purpose |
| --- | --- |
| `main.py` | Kivy app entry point. Shows the camera preview and runs identification on the current frame. |
| `bird_id.kv` | Kivy layout: camera preview, status label, button. |
| `classifier.py` | Loads a TFLite model and labels, and returns the top matches for an image. |
| `java/org/example/birdid/BirdClassifier.java` | Android-only TFLite wrapper. Called from Python through pyjnius. |
| `assets/model.tflite` | iNaturalist bird classifier (MobileNetV2, quantized, 965 species). |
| `assets/labels.txt` | One species name per line, in the same order as the model's outputs. |
| `buildozer.spec` | Android build configuration. |

## The model

`assets/model.tflite` and `assets/labels.txt` are copied from `mobilenet_v2_1.0_224_inat_bird_quant.tflite` and `inat_bird_labels.txt` in [google-coral/test_data](https://github.com/google-coral/test_data). Check that repo's license before shipping the app.

The app expects a TFLite image classifier with:

- an input of shape `[1, H, W, 3]` (RGB), float32 scaled to 0–1 or uint8
- one output score per class
- `assets/labels.txt` containing exactly one label per output, in order

To swap in another model, replace both files. Without them the app runs and shows "Model not installed".

## Running on desktop

```
pip install -r requirements.txt
python main.py
```

`classifier.py` uses `ai-edge-litert` if installed, then `tflite-runtime`, then `tensorflow`.

## Building for Android

```
pip install buildozer
buildozer android debug
```

On first use, Buildozer downloads the Android SDK and NDK.

The Android build runs the model with the TFLite Java API:

- `buildozer.spec` adds `java/` as source and pulls in `org.tensorflow:tensorflow-lite:2.14.0` through Gradle.
- `classifier.py` uses `BirdClassifier.java` on Android and the Python interpreter on desktop.

The Java helper compiles against the TFLite 2.14 API, but **it has not been run on a device.** Things to check on the first Android build:

- pyjnius passes the Python `bytes` to the Java `byte[]` argument correctly.
- Kivy's `platform` reports `android` and the model path resolves inside the app directory.
- The app shows "Model not installed" only when the model files are missing.

## Web version (iPad and other browsers)

The `web/` folder is a standalone page. It runs the same model in the browser, using TensorFlow.js TFLite, so it works in Safari on an iPad.

| File | Purpose |
| --- | --- |
| `web/index.html` | Page layout: camera view, status, button. |
| `web/app.js` | Camera, button, and results. Applies the same rules as `classifier.py`. |
| `web/worker.js` | Runs the model in a Web Worker, off the main thread. |
| `web/model.tflite`, `web/labels.txt` | Same model and labels as `assets/`. |

To use it on an iPad:

- The page must be served over **HTTPS** (or `localhost`). Safari only allows camera access on secure pages. GitHub Pages works if you enable it for this repo and point it at the `web/` folder.
- Open the page in Safari and allow camera access when asked.
- The scripts load from jsDelivr, so the first load needs an internet connection.

The web version matches the Python app's results on the sample bird photo: the top match is the same, and the browser's score is 57% against 67% from Python. The difference comes from how the photo is resized. Both versions use a 0.2 minimum score and skip the `background` class.

**Not yet tested on a real iPad.** The page was tested in headless Chromium with the sample photo as the camera feed. The camera, the Web Worker, and the WebAssembly files still need a check on Safari.

## Notes

- Identification runs on a background thread. The camera frame is copied on the UI thread, and the result is handed back to it with `Clock.schedule_once`. The button is disabled while a run is in progress.
- The model has a `background` class. When it is the top match, the app shows "No bird found" and never lists `background` as a species.
