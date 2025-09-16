# Frontend Deployment (Render Static Site)

This project includes a static frontend (`frontend/index.html`) that talks to the backend OCR API.

## 1. Backend URL
The current backend deployment URL is:

```
https://textify-b0iv.onrender.com
```

The frontend auto-detects environment:
- If loaded from `localhost`, it uses `http://localhost:8001` (adjust if your local backend port differs).
- Otherwise it defaults to the production backend above.
- You can override at runtime with a query parameter: `?api=<FULL_BACKEND_URL>`.

Example:
```
https://your-frontend.onrender.com/?api=https://textify-b0iv.onrender.com
```

## 2. Render Static Site Configuration
The `render.yaml` now contains a `staticSites` entry:
```yaml
staticSites:
  - name: photo-reader-frontend
    buildCommand: ''
    publishPath: frontend
    environment:
      - key: BACKEND_URL
        value: https://textify-b0iv.onrender.com
```
`BACKEND_URL` is available for future JavaScript enhancements (currently not required because the page logic already contains a default + override mechanism).

## 3. Deploy Steps
1. Commit & push changes:
   ```bash
   git add render.yaml DEPLOYMENT_FRONTEND.md frontend/index.html
   git commit -m "Add static site deployment config"
   git push origin main
   ```
2. In Render dashboard, the blueprint (if using repo auto deploy) will detect the new `staticSites` section and create the static site automatically. If not, create a New + Static Site and point to this repo; specify root directory (no subdirectory needed). Publish path: `frontend`.
3. Wait for build (should be instant—no build command).
4. Open the static site URL provided by Render. Example placeholder:
   ```
   https://photo-reader-frontend.onrender.com
   ```

## 4. Verification
Open browser dev tools (Network tab) while performing an OCR request:
- File upload POST to: `https://textify-b0iv.onrender.com/ocr` (unless overridden)
- Response JSON includes extracted text & metadata.

CLI test of backend (optional):
```bash
curl -s -X POST -F image=@/path/to/sample.png https://textify-b0iv.onrender.com/ocr | jq .text
```

## 5. Overriding the Backend at Runtime
Useful for staging vs production testing:
```
https://photo-reader-frontend.onrender.com/?api=https://staging-backend.onrender.com
```

## 6. Cache Control
`Cache-Control: no-cache` header is set for all paths to ensure you always get the latest HTML/JS changes on deploy. Adjust later for asset optimization if needed.

## 7. Local Development Workflow
- Run backend locally:
  ```bash
  cd backend
  flask --app app run --port 8001
  ```
  (Or your gunicorn command)
- Serve frontend by opening `frontend/index.html` directly or using a simple server:
  ```bash
  python -m http.server 5173 -d frontend
  ```
  Then visit: `http://localhost:5173/?api=http://localhost:8001`

## 8. Future Enhancements
- Add a small JS snippet to read `BACKEND_URL` from a meta tag or injected environment mapping at build time.
- Implement drag & drop and paste-from-clipboard.
- Add progress bar for large images.

---
Deployment config complete. Redeploy or trigger the Render blueprint to provision the static site.
