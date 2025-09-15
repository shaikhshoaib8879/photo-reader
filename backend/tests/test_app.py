import io
import os
import sys
from PIL import Image, ImageDraw
import shutil
import pytest

# Ensure backend root is on path when running from project root
CURRENT_DIR = os.path.dirname(__file__)
BACKEND_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, ".."))
if BACKEND_ROOT not in sys.path:
    sys.path.insert(0, BACKEND_ROOT)

from app import create_app  # noqa: E402


def generate_test_image(text: str = "Hello OCR"):
    image = Image.new("RGB", (400, 120), color=(255, 255, 255))
    draw = ImageDraw.Draw(image)
    draw.text((10, 40), text, fill=(0, 0, 0))
    buf = io.BytesIO()
    image.save(buf, format="PNG")
    buf.seek(0)
    return buf


def test_health():
    app = create_app()
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json == {"status": "ok"}


@pytest.mark.skipif(shutil.which("tesseract") is None, reason="tesseract binary not installed in environment")
def test_ocr():
    app = create_app()
    client = app.test_client()
    img = generate_test_image()
    data = {"image": (img, "test.png")}
    resp = client.post("/ocr", data=data, content_type='multipart/form-data')
    assert resp.status_code == 200
    payload = resp.json
    assert "text" in payload
    assert "Hello" in payload["text"]
