from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile

from preprocessor import preprocess_image
from ocr_engine import extract_text_tesseract  # Only use light OCR method

app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def ocr_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    ext = os.path.splitext(secure_filename(file.filename))[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
        file.save(temp.name)
        temp_path = temp.name

    try:
        if ext == ".pdf":
            return jsonify({"error": "PDF support disabled in lightweight version"}), 400

        cleaned_image = preprocess_image(temp_path)
        text = extract_text_tesseract(cleaned_image)

        return jsonify({"text": text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        os.remove(temp_path)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)