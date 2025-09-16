"""Sanity script to verify WSGI app import.
Run with: python backend/sanity.py (from repo root)
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import app  # type: ignore
import wsgi  # type: ignore

print("app.create_app:", app.create_app)
print("app.app instance:", app.app)
print("wsgi.app instance:", wsgi.app)
print("Same object?", app.app is wsgi.app)

from inspect import signature
print("create_app signature:", signature(app.create_app))

try:
    test_instance = app.create_app()
    print("Factory returns Flask instance:", test_instance)
except Exception as e:  # noqa
    print("Factory invocation failed:", e)
