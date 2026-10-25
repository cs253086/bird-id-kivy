// Runs the TFLite bird model off the main thread.

importScripts(
  "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-core@4.22.0/dist/tf-core.min.js",
  "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-backend-cpu@4.22.0/dist/tf-backend-cpu.min.js",
  "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-tflite@0.0.1-alpha.10/dist/tf-tflite.min.js"
);

tflite.setWasmPath(
  "https://cdn.jsdelivr.net/npm/@tensorflow/tfjs-tflite@0.0.1-alpha.10/wasm/"
);

let model = null;

// The model's output is quantized: score = raw / 256 (scale 1/256, zero point 0).
const OUTPUT_SCALE = 1 / 256;

self.onmessage = async (event) => {
  const message = event.data;

  if (message.type === "load") {
    try {
      await tf.setBackend("cpu");
      model = await tflite.loadTFLiteModel(message.url);
      self.postMessage({ type: "ready" });
    } catch (error) {
      self.postMessage({ type: "error", error: String(error) });
    }
    return;
  }

  if (message.type === "classify") {
    try {
      const size = message.size;
      const rgb = new Uint8Array(message.rgb);
      const scores = tf.tidy(() => {
        const input = tf.tensor4d(rgb, [1, size, size, 3], "int32");
        const output = model.predict(input);
        return output.dataSync();
      });
      const dequantized = Array.from(scores, (raw) => raw * OUTPUT_SCALE);
      self.postMessage({ type: "scores", scores: dequantized });
    } catch (error) {
      self.postMessage({ type: "error", error: String(error) });
    }
  }
};
