from __future__ import annotations
import os
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.api.v1.endpoints import factory
from app.core.logger import setup_logging
from app.core.middleware import logging_middleware

# 取得 templates 資料夾的路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

def create_app() -> FastAPI:
    setup_logging()
    app = FastAPI(title="Factory OS API", version="1.0.0")

    @app.middleware("http")
    async def add_logging(request: Request, call_next):
        return await logging_middleware(request, call_next)

    app.include_router(factory.router, prefix="/api/v1", tags=["Factory Operations"])

    # 讀取外部 HTML 檔案
    @app.get("/", response_class=HTMLResponse, include_in_schema=False)
    async def landing_page(request: Request):
        return templates.TemplateResponse("index.html", {"request": request})

    @app.get("/health", tags=["System Information"])
    async def health_check():
        return {"status": "healthy"}

    return app

app = create_app()