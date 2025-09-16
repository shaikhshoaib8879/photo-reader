"""OCR engine abstraction with lazy loading and fallbacks.

Order of preference (unless overridden by env variables):
1. Tesseract (if binary + pytesseract module available)
2. EasyOCR (if installed + torch stack present)

Environment Flags (optional):
  OCR_DISABLE_TESSERACT=1   -> Skip using Tesseract even if present
  OCR_DISABLE_EASYOCR=1     -> Skip using EasyOCR even if present
  OCR_LANG=en+de            -> Comma/plus separated languages (e.g. en+de)
  OCR_MAX_WIDTH=1600        -> Downscale image width to this before OCR

The goal is to keep import side-effects (like torch model load) out of the
module import path to reduce cold start RAM usage on small containers.
"""

from __future__ import annotations

import os
import shutil
from typing import Tuple, Dict, Any, Optional
from io import BytesIO

from PIL import Image

# --- Environment / configuration -------------------------------------------------
DISABLE_TESS = os.getenv("OCR_DISABLE_TESSERACT") in {"1", "true", "True"}
DISABLE_EASY = os.getenv("OCR_DISABLE_EASYOCR") in {"1", "true", "True"}
LANG_ENV = os.getenv("OCR_LANG", "en")
_LANGS = [p for part in LANG_ENV.replace(",", "+").split("+") if (p := part.strip())]
MAX_WIDTH = None
try:
    if os.getenv("OCR_MAX_WIDTH"):
        MAX_WIDTH = int(os.getenv("OCR_MAX_WIDTH"))
except ValueError:
    MAX_WIDTH = None  # Ignore invalid value

# --- Availability detection (cheap) ----------------------------------------------
_tesseract_binary = shutil.which("tesseract")
_pytesseract_imported = False
_easy_reader = None  # Will hold EasyOCR reader instance once created


def _load_pytesseract() -> bool:
    """Attempt to import pytesseract lazily. Returns availability."""
    global _pytesseract_imported  # noqa: PLW0603
    if _pytesseract_imported:
        return True
    if _tesseract_binary is None or DISABLE_TESS:
        return False
    try:
        import pytesseract  # type: ignore  # noqa: F401
        _pytesseract_imported = True
        return True
    except Exception:  # noqa: BLE001
        return False


def _ensure_easyocr(lang_list: Optional[list[str]] = None):
    """Lazy create EasyOCR reader. Returns (reader or None, error_message)."""
    global _easy_reader  # noqa: PLW0603
    if DISABLE_EASY:
        return None, "EasyOCR disabled via environment"
    if _easy_reader is not None:
        return _easy_reader, None
    try:
        import easyocr  # type: ignore
        # Import torch indirectly triggers load; keep it late.
        _easy_reader = easyocr.Reader(lang_list or ["en"], gpu=False)
        return _easy_reader, None
    except Exception as e:  # noqa: BLE001
        return None, f"EasyOCR unavailable: {e}"


def _maybe_downscale(pil_img: Image.Image) -> Image.Image:
    if MAX_WIDTH and pil_img.width > MAX_WIDTH:
        ratio = MAX_WIDTH / float(pil_img.width)
        new_h = int(pil_img.height * ratio)
        return pil_img.resize((MAX_WIDTH, new_h))
    return pil_img


def extract_text(stream, lang: Optional[str] = None) -> Tuple[str, Dict[str, Any]]:
    """Extract text from an image file-like object with graceful fallbacks.

    Returns (text, metadata). Raises RuntimeError if no engine usable.
    """
    raw_bytes = stream.read()
    stream.seek(0)
    img = Image.open(BytesIO(raw_bytes))
    if img.mode not in ("L", "RGB"):
        img = img.convert("RGB")
    img = _maybe_downscale(img)

    effective_lang = lang or "+".join(_LANGS)

    # Try Tesseract first
    if _load_pytesseract():
        import pytesseract  # type: ignore
        cfg = "--oem 3 --psm 3"
        kwargs = {"config": cfg}
        if effective_lang:
            kwargs["lang"] = effective_lang
        try:
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, **kwargs)
            words: list[str] = []
            confs: list[int] = []
            for i, token in enumerate(data.get("text", [])):
                if token and token.strip():
                    words.append(token.strip())
                    try:
                        v = int(data.get("conf", ["-1"])[i])
                    except Exception:  # noqa: BLE001
                        v = -1
                    if v >= 0:
                        confs.append(v)
            text_out = " ".join(words)
            avg_conf = round(sum(confs) / len(confs), 2) if confs else None
            meta = {
                "engine": "tesseract",
                "word_count": len(words),
                "average_confidence": avg_conf,
                "tesseract_version": str(pytesseract.get_tesseract_version()),
            }
            return text_out, meta
        except Exception as e:  # noqa: BLE001
            # Fall through to EasyOCR
            last_tess_error = f"Tesseract failed: {e}"
    else:
        last_tess_error = None

    # Try EasyOCR
    reader, easy_err = _ensure_easyocr(_LANGS)
    if reader is not None:
        import numpy as np  # type: ignore
        import easyocr  # type: ignore
        np_img = np.array(img)
        try:
            results = reader.readtext(np_img, detail=1)
            words = [r[1] for r in results if r[1].strip()]
            confs: list[float] = []
            for r in results:
                try:
                    confs.append(float(r[2]))
                except Exception:  # noqa: BLE001
                    pass
            avg_conf = round(sum(confs) / len(confs), 2) if confs else None
            meta = {
                "engine": "easyocr",
                "word_count": len(words),
                "average_confidence": avg_conf,
                "easyocr_version": getattr(easyocr, '__version__', 'unknown'),
            }
            return " ".join(words), meta
        except Exception as e:  # noqa: BLE001
            easy_err = f"EasyOCR inference failed: {e}"

    # Neither path succeeded
    pieces = [
        "No OCR engine succeeded.",
        f"Tesseract: {'disabled/unavailable' if not _load_pytesseract() else last_tess_error}",
        f"EasyOCR: {easy_err or 'disabled/unavailable'}",
        "Set OCR_DISABLE_EASYOCR=1 to skip EasyOCR if memory constrained.",
        "Ensure tesseract binary installed or rely on EasyOCR stack.",
    ]
    raise RuntimeError(" | ".join(filter(None, pieces)))
