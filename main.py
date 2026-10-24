from kivy.app import App
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from PIL import Image, ImageOps

from classifier import BirdClassifier

try:
    from android.permissions import Permission, request_permissions
except ImportError:  # Not running on Android
    request_permissions = None


class BirdRoot(BoxLayout):
    status = StringProperty("Point the camera at a bird")

    def __init__(self, classifier, **kwargs):
        super().__init__(**kwargs)
        self.classifier = classifier
        if not classifier.ready:
            self.status = "Model not installed. See README.md."

    def identify(self):
        if not self.classifier.ready:
            return

        texture = self.ids.camera.texture
        if texture is None:
            self.status = "Camera not ready yet"
            return

        width, height = texture.size
        pixels = texture.pixels
        mode = "RGBA" if len(pixels) == width * height * 4 else "RGB"
        # OpenGL textures are stored bottom-up, so flip before classifying.
        image = ImageOps.flip(Image.frombytes(mode, (width, height), pixels))

        results = self.classifier.identify(image)
        self.status = "\n".join(f"{name} ({score:.0%})" for name, score in results)


class BirdIdApp(App):
    def build(self):
        if request_permissions is not None:
            request_permissions([Permission.CAMERA])

        Builder.load_file("bird_id.kv")
        return BirdRoot(classifier=BirdClassifier())


if __name__ == "__main__":
    BirdIdApp().run()
