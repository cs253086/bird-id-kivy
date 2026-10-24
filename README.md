# Bird ID

An Android app built with Kivy. Point the camera at a real bird or a picture of one, press **Identify bird**, and the app shows the most likely species.

## Layout

| File | Purpose |
| --- | --- |
| `main.py` | Kivy app entry point. Shows the camera preview and runs identification on the current frame. |
| `bird_id.kv` | Kivy layout: camera preview, status label, button. |
| `classifier.py` | Loads a TFLite model and labels, and returns the top matches for an image. |
| `assets/model.tflite` | Image classifier (not in the repo; see below). |
| `assets/labels.txt` | One species name per line, in the same order as the model's outputs. |
| `buildozer.spec` | Android build configuration. |

## Adding the model

The app expects an image classifier in TFLite format with:

- an input of shape `[1, H, W, 3]` (RGB), float32 scaled to 0–1 or uint8
- one output score per class
- `assets/labels.txt` containing exactly one label per output, in order

Put the files at `assets/model.tflite` and `assets/labels.txt`. Without them the app runs and shows "Model not installed".

## Running on desktop

```
pip install -r requirements.txt
python main.py
```

`tflite-runtime` has no wheels for every platform. If it fails to install, use `pip install tensorflow` instead. `classifier.py` falls back to it automatically.

## Building for Android

```
pip install buildozer
buildozer android debug
```

On first use, Buildozer downloads the Android SDK and NDK.

**Open item:** the Android build does not include TFLite. `tflite-runtime` is not available for Android through python-for-android, so on-device inference still needs a recipe or a Java/pyjnius bridge to the TFLite Android library. Until that is added, `classifier.py` will report that no model is loaded on Android.

## Notes

- Identification runs on the UI thread, so the app may pause briefly on each press. Moving it to a background thread is the next step if this is noticeable on device.
