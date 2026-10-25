// Camera, button, and results for the bird identifier.
// The same rules as classifier.py: skip background, keep the top 3 birds,
// and show only birds scoring at least 0.2.

const INPUT_SIZE = 224;
const TOP_K = 3;
const MIN_SCORE = 0.2;
const BACKGROUND_LABEL = "background";

const video = document.getElementById("camera");
const button = document.getElementById("identify");
const status = document.getElementById("status");
const captureCanvas = document.createElement("canvas");
captureCanvas.width = INPUT_SIZE;
captureCanvas.height = INPUT_SIZE;
const captureContext = captureCanvas.getContext("2d", { willReadFrequently: true });

const worker = new Worker("worker.js");
let labels = [];
let busy = false;

// Pure function, so it can be tested without a camera or a model.
function pickBirds(scores, labels, topK = TOP_K, minScore = MIN_SCORE) {
  const ranked = scores
    .map((score, index) => ({ name: labels[index], score }))
    .sort((a, b) => b.score - a.score);

  if (ranked[0].name === BACKGROUND_LABEL) {
    return [];
  }

  const birds = ranked.filter((item) => item.name !== BACKGROUND_LABEL).slice(0, topK);
  return birds.filter((item) => item.score >= minScore);
}

function showStatus(message) {
  status.textContent = message;
}

function setBusy(value) {
  busy = value;
  button.disabled = value;
  button.textContent = value ? "Identifying..." : "Identify bird";
}

function frameToRgb() {
  // Squash the whole frame to a square, the same as the Python app does.
  captureContext.drawImage(video, 0, 0, video.videoWidth, video.videoHeight, 0, 0, INPUT_SIZE, INPUT_SIZE);

  const rgba = captureContext.getImageData(0, 0, INPUT_SIZE, INPUT_SIZE).data;
  const rgb = new Uint8Array(INPUT_SIZE * INPUT_SIZE * 3);
  for (let i = 0, j = 0; i < rgba.length; i += 4, j += 3) {
    rgb[j] = rgba[i];
    rgb[j + 1] = rgba[i + 1];
    rgb[j + 2] = rgba[i + 2];
  }
  return rgb;
}

function identify() {
  if (busy) {
    return;
  }
  if (video.readyState < 2) {
    showStatus("Camera not ready yet");
    return;
  }

  setBusy(true);
  showStatus("Identifying...");
  const rgb = frameToRgb();
  worker.postMessage({ type: "classify", size: INPUT_SIZE, rgb: rgb.buffer }, [rgb.buffer]);
}

worker.onmessage = (event) => {
  const message = event.data;

  if (message.type === "ready") {
    showStatus("Point the camera at a bird");
    button.disabled = false;
    return;
  }

  if (message.type === "scores") {
    const birds = pickBirds(message.scores, labels);
    showStatus(
      birds.length === 0
        ? "No bird found"
        : birds.map((bird) => `${bird.name} (${Math.round(bird.score * 100)}%)`).join("\n")
    );
    setBusy(false);
    return;
  }

  if (message.type === "error") {
    showStatus(`Error: ${message.error}`);
    setBusy(false);
  }
};

async function startCamera() {
  const stream = await navigator.mediaDevices.getUserMedia({
    video: { facingMode: { ideal: "environment" } },
    audio: false,
  });
  video.srcObject = stream;
  await video.play();
}

async function main() {
  showStatus("Loading model...");
  button.disabled = true;
  button.addEventListener("click", identify);

  try {
    labels = (await (await fetch("labels.txt")).text())
      .split("\n")
      .map((line) => line.trim())
      .filter((line) => line.length > 0);

    const modelUrl = new URL("model.tflite", location.href).href;
    worker.postMessage({ type: "load", url: modelUrl });
    await startCamera();
  } catch (error) {
    showStatus(`Could not start: ${error.message}`);
  }
}

main();
