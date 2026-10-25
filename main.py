import threading

from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.properties import BooleanProperty, StringProperty
from kivy.uix.boxlayout import BoxLayout
from PIL import Image, ImageOps

from classifier import BirdClassifier

try:
    from android.permissions import Permission, request_permissions
except ImportError:  # Not running on Android
    request_permissions = None


def format_results(results):
    if not results:
        return "No bird found"
    return "\n".join(f"{name} ({score:.0%})" for name, score in results)


class BirdRoot(BoxLayout):
    status = StringProperty("Point the camera at a bird")
    identifying = BooleanProperty(False)

    def __init__(self, classifier, **kwargs):
        super().__init__(**kwargs)
        self.classifier = classifier
        if not classifier.ready:
            self.status = "Model not installed. See README.md."

    def identify(self):
        if self.identifying or not self.classifier.ready:
            return

        texture = self.ids.camera.texture
        if texture is None:
            self.status = "Camera not ready yet"
            return

        # The texture must be read on the UI thread, so copy the frame here
        # and classify it in the background.
        width, height = texture.size
        pixels = texture.pixels
        mode = "RGBA" if len(pixels) == width * height * 4 else "RGB"
        # OpenGL textures are stored bottom-up, so flip before classifying.
        image = ImageOps.flip(Image.frombytes(mode, (width, height), pixels))

        self.identifying = True
        self.status = "Identifying..."
        threading.Thread(target=self._identify_in_background, args=(image,), daemon=True).start()

    def _identify_in_background(self, image):
        try:
            message = format_results(self.classifier.identify(image))
        except Exception as error:  # Show any failure in the UI instead of crashing.
            message = f"Error: {error}"
        Clock.schedule_once(lambda dt: self._show_result(message))

    def _show_result(self, message):
        self.status = message
        self.identifying = False


class BirdIdApp(App):
    def build(self):
        if request_permissions is not None:
            request_permissions([Permission.CAMERA])

        Builder.load_file("bird_id.kv")
        return BirdRoot(classifier=BirdClassifier())


if __name__ == "__main__":
    BirdIdApp().run()
