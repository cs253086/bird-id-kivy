import os

import numpy as np
from kivy.utils import platform
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "assets", "model.tflite")
LABELS_PATH = os.path.join(BASE_DIR, "assets", "labels.txt")
JAVA_CLASSIFIER = "org.example.birdid.BirdClassifier"
JAVA_THREADS = 4


def load_interpreter(model_path):
    try:
        from ai_edge_litert.interpreter import Interpreter
    except ImportError:
        try:
            from tflite_runtime.interpreter import Interpreter
        except ImportError:
            from tensorflow.lite import Interpreter

    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


class PythonBackend:
    """Runs the model with a Python TFLite interpreter (desktop)."""

    def __init__(self, model_path):
        self.interpreter = load_interpreter(model_path)
        self.input_detail = self.interpreter.get_input_details()[0]
        self.output_detail = self.interpreter.get_output_details()[0]
        _, height, width, _ = self.input_detail["shape"]
        self.input_size = (width, height)

    def run(self, rgb):
        if self.input_detail["dtype"] == np.uint8:
            tensor = rgb
        else:
            tensor = rgb.astype(np.float32) / 255.0
        self.interpreter.set_tensor(self.input_detail["index"], tensor[np.newaxis])
        self.interpreter.invoke()

        scores = self.interpreter.get_tensor(self.output_detail["index"])[0]
        if self.output_detail["dtype"] != np.float32:
            scale, zero_point = self.output_detail["quantization"]
            scores = (scores.astype(np.float32) - zero_point) * scale
        return scores


class JavaBackend:
    """Runs the model through org.example.birdid.BirdClassifier (Android)."""

    def __init__(self, model_path):
        from jnius import autoclass

        classifier_class = autoclass(JAVA_CLASSIFIER)
        self.classifier = classifier_class(model_path, JAVA_THREADS)
        self.input_size = (
            self.classifier.getInputWidth(),
            self.classifier.getInputHeight(),
        )

    def run(self, rgb):
        scores = self.classifier.run(rgb.tobytes())
        return np.array(list(scores), dtype=np.float32)


def create_backend(model_path):
    if platform == "android":
        return JavaBackend(model_path)
    return PythonBackend(model_path)


class BirdClassifier:
    """Classifies an image into one of the species in labels.txt."""

    def __init__(self, model_path=MODEL_PATH, labels_path=LABELS_PATH):
        self.backend = None
        self.labels = []

        if os.path.exists(model_path) and os.path.exists(labels_path):
            with open(labels_path, encoding="utf-8") as f:
                self.labels = [line.strip() for line in f if line.strip()]
            self.backend = create_backend(model_path)

    @property
    def ready(self):
        return self.backend is not None

    def identify(self, image, top_k=3):
        """Return the top_k (label, score) pairs, best first."""
        if not self.ready:
            raise RuntimeError("No model loaded")

        width, height = self.backend.input_size
        rgb = np.asarray(image.convert("RGB").resize((width, height)), dtype=np.uint8)
        scores = self.backend.run(rgb)

        if len(scores) != len(self.labels):
            raise ValueError(
                f"Model has {len(scores)} outputs but labels.txt has {len(self.labels)} lines"
            )

        best = np.argsort(scores)[::-1][:top_k]
        return [(self.labels[i], float(scores[i])) for i in best]
