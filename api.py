from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile

from preprocessor import preprocess_image
from pdfocr import process_pdf
from ocr_engine import perform_ocr

app = Flask(__name__)

@app.route("/ocr", methods=["POST"])
def ocr_route():
    if 'file' not in request.files:
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    filename = secure_filename(file.filename)
    ext = os.path.splitext(filename)[1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as temp:
        file.save(temp.name)
        temp_path = temp.name

    try:
        if ext == ".pdf":
            ocr_result = process_pdf(temp_path)
        else:
            cleaned_image = preprocess_image(temp_path)
            ocr_result = perform_ocr(cleaned_image)

        os.remove(temp_path)
        return jsonify({"text": ocr_result}), 200

    except Exception as e:
        os.remove(temp_path)
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)