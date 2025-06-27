from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
import os
import tempfile

from preprocessor import preprocess_image
from ocr_engine import extract_text_tesseract

from pdf2image import convert_from_path

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
            # Convert PDF to images (one per page)
            images = convert_from_path(temp_path)
            all_text = []
            for img in images:
                # Save PIL image to a temporary file for preprocessing
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as img_temp:
                    img.save(img_temp.name)
                    cleaned_image = preprocess_image(img_temp.name)
                    text = extract_text_tesseract(cleaned_image)
                    all_text.append(text)
                    os.remove(img_temp.name)
            return jsonify({"text": "\n\n".join(all_text)}), 200

        # For images
        cleaned_image = preprocess_image(temp_path)
        text = extract_text_tesseract(cleaned_image)
        return jsonify({"text": text}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        os.remove(temp_path)

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0", port=5000)
