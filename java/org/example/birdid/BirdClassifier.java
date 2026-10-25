package org.example.birdid;

import java.io.File;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import org.tensorflow.lite.DataType;
import org.tensorflow.lite.Interpreter;
import org.tensorflow.lite.Tensor;

/**
 * Runs a TFLite image classifier on RGB pixels. Called from Python through pyjnius
 * on Android, where the TFLite runtime is available as a Gradle dependency.
 */
public final class BirdClassifier implements AutoCloseable {
    private final Interpreter interpreter;
    private final int inputWidth;
    private final int inputHeight;
    private final boolean inputIsFloat;
    private final boolean outputIsFloat;
    private final int numClasses;
    private final float outputScale;
    private final int outputZeroPoint;

    public BirdClassifier(String modelPath, int numThreads) {
        Interpreter.Options options = new Interpreter.Options().setNumThreads(numThreads);
        interpreter = new Interpreter(new File(modelPath), options);

        // Input shape is [1, height, width, 3].
        Tensor input = interpreter.getInputTensor(0);
        int[] inputShape = input.shape();
        inputHeight = inputShape[1];
        inputWidth = inputShape[2];
        inputIsFloat = input.dataType() == DataType.FLOAT32;

        // Output shape is [1, numClasses].
        Tensor output = interpreter.getOutputTensor(0);
        numClasses = output.shape()[1];
        outputIsFloat = output.dataType() == DataType.FLOAT32;
        Tensor.QuantizationParams quantization = output.quantizationParams();
        outputScale = quantization.getScale();
        outputZeroPoint = quantization.getZeroPoint();
    }

    public int getInputWidth() {
        return inputWidth;
    }

    public int getInputHeight() {
        return inputHeight;
    }

    /**
     * @param rgb inputHeight * inputWidth * 3 bytes, row-major, RGB order
     * @return one score per class, dequantized if the model is quantized
     */
    public float[] run(byte[] rgb) {
        int pixelCount = inputWidth * inputHeight * 3;
        if (rgb.length != pixelCount) {
            throw new IllegalArgumentException(
                    "Expected " + pixelCount + " bytes, got " + rgb.length);
        }

        int bytesPerValue = inputIsFloat ? 4 : 1;
        ByteBuffer input = ByteBuffer.allocateDirect(pixelCount * bytesPerValue)
                .order(ByteOrder.nativeOrder());
        if (inputIsFloat) {
            for (byte value : rgb) {
                input.putFloat((value & 0xFF) / 255f);
            }
        } else {
            input.put(rgb);
        }
        input.rewind();

        float[] scores = new float[numClasses];
        if (outputIsFloat) {
            float[][] output = new float[1][numClasses];
            interpreter.run(input, output);
            System.arraycopy(output[0], 0, scores, 0, numClasses);
        } else {
            byte[][] output = new byte[1][numClasses];
            interpreter.run(input, output);
            for (int i = 0; i < numClasses; i++) {
                int raw = output[0][i] & 0xFF;
                scores[i] = (raw - outputZeroPoint) * outputScale;
            }
        }
        return scores;
    }

    @Override
    public void close() {
        interpreter.close();
    }
}
