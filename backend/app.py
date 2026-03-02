from flask import Flask, request, jsonify
from flask_cors import CORS
import tensorflow as tf
import numpy as np
from PIL import Image
import io

app = Flask(__name__)
CORS(app)

# ===== LOAD MODEL =====
model = tf.keras.models.load_model("../model/best_model.h5")
# ✅ Updated classes
classes = ['Straight', 'Wavy', 'bald', 'curly', 'dreadlocks',
           'dry', 'frizzy', 'hairfall', 'healthy', 'kinky', 'notbald']

# ===== PREDICT ROUTE =====
@app.route('/predict', methods=['POST'])
def predict():
    try:
        file = request.files['image']
        img = Image.open(io.BytesIO(file.read())).resize((224, 224)).convert("RGB")
        img_array = np.array(img, dtype=np.float32)
        img_array = np.expand_dims(img_array, axis=0)

        prediction = model.predict(img_array)
        result = classes[np.argmax(prediction)]

        # ✅ FIX: No softmax needed — model already uses softmax output
        confidence = float(np.max(prediction)) * 100

        return jsonify({
            "hair_type": result,
            "confidence": round(confidence, 2)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ===== HEALTH CHECK =====
@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "running"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)