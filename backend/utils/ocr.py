import shutil
from typing import Tuple, Dict, Any, Optional
from io import BytesIO

import pytesseract
from PIL import Image

TESSERACT_AVAILABLE = shutil.which("tesseract") is not None

if not TESSERACT_AVAILABLE:
    try:
        import easyocr  # type: ignore
        import numpy as np  # type: ignore
        _easy_reader = easyocr.Reader(['en'])  # You can expand languages
        EASY_AVAILABLE = True
    except Exception:  # noqa: BLE001
        EASY_AVAILABLE = False
else:
    EASY_AVAILABLE = False


def extract_text(stream, lang: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """Extract text from an image file-like object.

    Strategy:
    1. Use Tesseract if the binary is available.
    2. Else attempt EasyOCR if installed.
    3. Raise a clear error if neither engine is available.
    """
    # Read image into PIL (we may need raw bytes for EasyOCR too)
    raw_bytes = stream.read()
    stream.seek(0)
    image = Image.open(BytesIO(raw_bytes))
    if image.mode not in ("L", "RGB"):
        image = image.convert("RGB")

    if TESSERACT_AVAILABLE:
        custom_oem_psm_config = "--oem 3 --psm 3"
        kwargs = {"config": custom_oem_psm_config}
        if lang:
            kwargs["lang"] = lang
        raw_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, **kwargs)
        words = []
        confidences = []
        for i, text in enumerate(raw_data.get("text", [])):
            if text and text.strip():
                words.append(text.strip())
                try:
                    conf = int(raw_data.get("conf", ["-1"])[i])
                except ValueError:
                    conf = -1
                if conf >= 0:
                    confidences.append(conf)
        full_text = " ".join(words)
        avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else None
        meta = {
            "engine": "tesseract",
            "word_count": len(words),
            "average_confidence": avg_conf,
            "tesseract_version": (
                pytesseract.get_tesseract_version().version_string
                if hasattr(pytesseract.get_tesseract_version(), 'version_string')
                else str(pytesseract.get_tesseract_version())
            ),
        }
        return full_text, meta

    if EASY_AVAILABLE:
        # Use EasyOCR
        np_image = np.array(image)  # type: ignore[name-defined]
        # detail=1 returns list: [ (bbox, text, confidence), ... ]
        results = _easy_reader.readtext(np_image, detail=1)  # type: ignore[name-defined]
        words = [r[1] for r in results if r[1].strip()]
        confidences = []
        for r in results:
            try:
                confidences.append(float(r[2]))
            except Exception:  # noqa: BLE001
                pass
        avg_conf = round(sum(confidences) / len(confidences), 2) if confidences else None
        full_text = " ".join(words)
        meta = {
            "engine": "easyocr",
            "word_count": len(words),
            "average_confidence": avg_conf,
            "easyocr_version": getattr(__import__('easyocr'), '__version__', 'unknown'),
        }
        return full_text, meta

    raise RuntimeError(
        "No OCR engine available: tesseract binary not found and easyocr not installed. "
        "Install tesseract or 'pip install easyocr torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu'"
    )
