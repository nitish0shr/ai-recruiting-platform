# apps/backend/main.py - bridge so "uvicorn main:app" works
try:
    from src.main import app  # real app
except Exception:
    from fastapi import FastAPI
    app = FastAPI()
    @app.get("/health")
    def _health():
        return {"status": "fallback-up"}
