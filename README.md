# Bird ID

An Android app built with Kivy. Point the camera at a real bird or a picture of one, press **Identify bird**, and the app shows the most likely species.

## Layout

| File | Purpose |
| --- | --- |
| `main.py` | Kivy app entry point. Shows the camera preview and runs identification on the current frame. |
| `bird_id.kv` | Kivy layout: camera preview, status label, button. |
| `classifier.py` | Loads a TFLite model and labels, and returns the top matches for an image. |
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

**Open item:** the Android build does not include TFLite. `tflite-runtime` is not available for Android through python-for-android, so on-device inference still needs a recipe or a Java/pyjnius bridge to the TFLite Android library. Until that is added, `classifier.py` will report that no model is loaded on Android.

## Notes

- Identification runs on the UI thread, so the app may pause briefly on each press. Moving it to a background thread is the next step if this is noticeable on device.
