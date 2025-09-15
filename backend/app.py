import os
from flask import Flask, request, jsonify
import requests
import traceback
from flask_cors import CORS
from werkzeug.utils import secure_filename
from utils.ocr import extract_text

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp", "tiff", "bmp"}
MAX_CONTENT_LENGTH = 10 * 1024 * 1024  # 10MB


def create_app():
    app = Flask(__name__)
    CORS(app)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    @app.get("/health")
    def health():
        return {"status": "ok"}

    def allowed_file(filename: str) -> bool:
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    @app.post("/ocr")
    def ocr_endpoint():
        lang = request.form.get("lang")  # optional language code(s)
        image_url = request.form.get("image_url")

        file_storage = request.files.get("image")

        if not file_storage and not image_url:
            return jsonify({"error": "Provide an uploaded file (field 'image') or an 'image_url'"}), 400
        if file_storage and image_url:
            return jsonify({"error": "Provide only one of file upload or image_url"}), 400

        stream = None
        filename = None
        if file_storage:
            if file_storage.filename == "":
                return jsonify({"error": "Empty filename"}), 400
            if not allowed_file(file_storage.filename):
                return jsonify({"error": "Unsupported file type"}), 400
            filename = secure_filename(file_storage.filename)
            stream = file_storage.stream
        else:
            try:
                resp = requests.get(image_url, timeout=10)
                resp.raise_for_status()
            except Exception as e:  # noqa: BLE001
                return jsonify({"error": f"Failed to fetch image_url: {e}"}), 400
            content_type = resp.headers.get("Content-Type", "")
            # Basic allow list check
            if not any(fmt in content_type for fmt in ["png", "jpeg", "jpg", "gif", "webp", "tiff", "bmp"]):
                return jsonify({"error": "image_url does not appear to be an image"}), 400
            from io import BytesIO
            stream = BytesIO(resp.content)
            filename = image_url.split("?")[0].rsplit("/", 1)[-1] or "remote_image"

        try:
            text, meta = extract_text(stream, lang=lang)
        except Exception as e:  # pylint: disable=broad-except
            traceback.print_exc()
            return jsonify({"error": f"OCR failed: {e}"}), 500
        return jsonify({"filename": filename, "text": text, "meta": meta})

    return app


app = create_app()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
