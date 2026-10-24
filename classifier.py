import os

import numpy as np
from PIL import Image

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "assets", "model.tflite")
LABELS_PATH = os.path.join(BASE_DIR, "assets", "labels.txt")


def load_interpreter(model_path):
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError:
        from tensorflow.lite import Interpreter

    interpreter = Interpreter(model_path=model_path)
    interpreter.allocate_tensors()
    return interpreter


class BirdClassifier:
    """Runs a TFLite image classifier with one label per output class."""

    def __init__(self, model_path=MODEL_PATH, labels_path=LABELS_PATH):
        self.interpreter = None
        self.labels = []

        if os.path.exists(model_path) and os.path.exists(labels_path):
            with open(labels_path, encoding="utf-8") as f:
                self.labels = [line.strip() for line in f if line.strip()]
            self.interpreter = load_interpreter(model_path)

    @property
    def ready(self):
        return self.interpreter is not None

    def identify(self, image, top_k=3):
        """Return the top_k (label, score) pairs, best first."""
        if not self.ready:
            raise RuntimeError("No model loaded")

        input_detail = self.interpreter.get_input_details()[0]
        output_detail = self.interpreter.get_output_details()[0]
        _, height, width, _ = input_detail["shape"]

        resized = image.convert("RGB").resize((width, height))
        pixels = np.asarray(resized)
        if input_detail["dtype"] == np.uint8:
            tensor = pixels.astype(np.uint8)
        else:
            tensor = pixels.astype(np.float32) / 255.0
        self.interpreter.set_tensor(input_detail["index"], tensor[np.newaxis])
        self.interpreter.invoke()

        scores = self.interpreter.get_tensor(output_detail["index"])[0]
        if output_detail["dtype"] != np.float32:
            scale, zero_point = output_detail["quantization"]
            scores = (scores.astype(np.float32) - zero_point) * scale

        if len(scores) != len(self.labels):
            raise ValueError(
                f"Model has {len(scores)} outputs but labels.txt has {len(self.labels)} lines"
            )

        best = np.argsort(scores)[::-1][:top_k]
        return [(self.labels[i], float(scores[i])) for i in best]
