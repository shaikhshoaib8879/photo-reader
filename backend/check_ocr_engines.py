"""Quick diagnostic script to verify OCR engine availability.

Usage:
  python backend/check_ocr_engines.py [optional-image-path]

Environment flags that affect behavior (see utils/ocr.py for more):
  OCR_DISABLE_TESSERACT=1  -> Skip Tesseract
  OCR_DISABLE_EASYOCR=1    -> Skip EasyOCR
  OCR_LANG=en+de           -> Language choices
  OCR_MAX_WIDTH=1600       -> Downscale wide images

If you supply an image path it will run extract_text and show the result.
If not, it will only report engine availability.
"""
from __future__ import annotations

import os
import sys
import time
import shutil
from pathlib import Path

from utils import ocr  # noqa: E402


def check_tesseract():
    binary = shutil.which("tesseract")
    if not binary or os.getenv("OCR_DISABLE_TESSERACT") in {"1", "true", "True"}:
        return False, "Disabled or binary not found"
    # Lazy load attempt
    ok = ocr._load_pytesseract()  # type: ignore[attr-defined]
    return ok, "Loaded" if ok else "Import failed"


def check_easyocr():
    if os.getenv("OCR_DISABLE_EASYOCR") in {"1", "true", "True"}:
        return False, "Disabled via env"
    start = time.time()
    reader, err = ocr._ensure_easyocr(["en"])  # type: ignore[attr-defined]
    if reader is None:
        return False, err or "Unknown error"
    return True, f"Reader ready in {time.time() - start:.2f}s"


def test_image(path: Path):
    from io import BytesIO
    print(f"\nRunning OCR on: {path}")
    with path.open("rb") as f:
        from utils.ocr import extract_text
        text, meta = extract_text(f)
        print("Engine:", meta.get("engine"))
        print("Average confidence:", meta.get("average_confidence"))
        print("Word count:", meta.get("word_count"))
        print("--- TEXT (truncated 500 chars) ---")
        print(text[:500])


def main():
    print("OCR Engine Diagnostic")
    print("Languages:", os.getenv("OCR_LANG", "en"))
    print("Disable Flags: TESSERACT=", os.getenv("OCR_DISABLE_TESSERACT"),
          "EASYOCR=", os.getenv("OCR_DISABLE_EASYOCR"))

    t_ok, t_msg = check_tesseract()
    print(f"Tesseract: {'AVAILABLE' if t_ok else 'UNAVAILABLE'} - {t_msg}")

    e_ok, e_msg = check_easyocr()
    print(f"EasyOCR: {'AVAILABLE' if e_ok else 'UNAVAILABLE'} - {e_msg}")

    if len(sys.argv) > 1:
        img_path = Path(sys.argv[1])
        if img_path.exists():
            try:
                test_image(img_path)
            except Exception as e:  # noqa: BLE001
                print("Image OCR failed:", e)
        else:
            print("Provided image path does not exist:", img_path)


if __name__ == "main":  # pragma: no cover
    main()
