"""WSGI entrypoint for Gunicorn.

This avoids accidental invocation of the factory function itself as a WSGI app.
Gunicorn start command should use:  gunicorn wsgi:app
"""
from app import create_app  # type: ignore

print("[wsgi] Initializing Flask app via create_app()")
app = create_app()
print("[wsgi] Flask app object ready:", app)
