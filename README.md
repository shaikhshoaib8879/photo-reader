# Photo Reader OCR

A simple two-part web application that extracts text from images using Tesseract OCR.

## Stack

- Frontend: Static HTML + TailwindCSS + vanilla JS (deploy on Netlify)
- Backend: Flask (Python) with `pytesseract` (deploy on Render / Railway / Heroku)

## Features

- Upload an image from the browser
- Sends it to a Flask `/ocr` endpoint
- Returns extracted text + metadata (word count, average confidence, Tesseract version)
- Displays text nicely in the UI

## Backend (Flask) Setup

### 1. Install System Dependency (Tesseract)

Ubuntu / Debian:
```bash
sudo apt update && sudo apt install -y tesseract-ocr libtesseract-dev
```

(For other OSes, install Tesseract using your package manager: Homebrew on macOS `brew install tesseract` or Windows installer.)

### 2. Create & Activate Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Python Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Run Locally
```bash
python backend/app.py
```
Backend will start at `http://localhost:8000`.

### 5. Run Tests
```bash
pytest -q
```

## Frontend (Static) Local Preview
Open `frontend/index.html` directly OR serve with a simple server:
```bash
python -m http.server --directory frontend 5500
```
Then visit: http://localhost:5500

You can point the UI to a remote backend by adding `?api=https://your-backend.onrender.com` in the URL.

## Deployment

### Deploy Backend to Render
1. Push repository to GitHub.
2. In Render dashboard: New + Web Service.
3. Select repo, set runtime to Python.
4. Environment:
   - Build Command: `pip install -r backend/requirements.txt`
   - Start Command: `python backend/app.py`
5. Add a plan with sufficient memory (Tesseract needs some RAM).
6. Add environment variable (optional): `PORT=10000` (Render sets `PORT` automatically; Flask app already honors it).
7. Add a Render disk only if you need persistence (not required here).

Render will install system packages. To ensure Tesseract availability, add a `render.yaml` (optional advanced) or switch to Docker. Simpler alternative: use Railway.

### Deploy Backend to Railway (Alternative)
1. Create new project -> Deploy from repo.
2. Add a Nixpacks variable to install system packages automatically if needed (Railway usually detects Python). If Tesseract missing, switch to Dockerfile (sample below).

### Minimal Dockerfile (Optional)
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y tesseract-ocr libtesseract-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY backend ./backend
ENV PORT=8000
CMD ["python", "backend/app.py"]
```

### Deploy Frontend to Netlify
1. In Netlify dashboard: Add new site -> Deploy manually or from Git.
2. If manual: drag & drop the `frontend/` folder into Netlify deploy UI.
3. If via Git: set `Publish directory` to `frontend` and no build command (static site).
4. After deploy, visit your site URL and use query param to point to backend:
   `https://your-netlify-site.netlify.app/?api=https://your-backend.onrender.com`

### CORS
CORS is enabled broadly with `flask-cors`. For production tightening, restrict origins:
```python
CORS(app, resources={r"/ocr": {"origins": ["https://your-netlify-site.netlify.app"]}})
```

## API

### GET /health
Response:
```json
{"status": "ok"}
```

### POST /ocr
`multipart/form-data` with field `image`.
Response:
```json
{
  "filename": "sample.png",
  "text": "Detected text...",
  "meta": {
    "word_count": 12,
    "average_confidence": 87.32,
    "tesseract_version": "5.3.0"
  }
}
```
Errors: 400 (missing/invalid file), 500 (OCR failure).

## Roadmap / Possible Enhancements
- URL-based image fetch (`image_url` parameter)
- Language selection (pass `lang` to Tesseract)
- PDF support (convert pages to images)
- Bounding box overlay display
- Batch uploads
- Authentication / rate limiting

## License
MIT
