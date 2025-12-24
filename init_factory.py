import os
import subprocess
import sys
from pathlib import Path

def create_factory_structure():
    # 1. 定義資料夾結構
    dirs = [
        "app/api/v1/endpoints",
        "app/core",
        "app/models",
        "app/adapters",
        "tests",
    ]

    # 2. 定義所有檔案內容
    files = {
        "pyproject.toml": """
[tool.poetry]
name = "factory-backend-standard"
version = "0.1.0"
package-mode = false

[tool.poetry.dependencies]
python = ">=3.8,<4.0"
fastapi = "^0.100.0"
uvicorn = {extras = ["standard"], version = "^0.23.0"}
sqlalchemy = {extras = ["asyncio"], version = "^2.0.0"}
structlog = "^23.1.0"
pydantic-settings = "^2.0.0"
aiosqlite = "^0.19.0"
httpx = "^0.24.0"

[tool.poetry.group.dev.dependencies]
pytest = "^7.0.0"
pytest-asyncio = "^0.21.0"

[tool.pytest.ini_options]
asyncio_mode = "auto"
""",

        "app/core/database.py": """
from __future__ import annotations
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator

class Base(DeclarativeBase): pass

DATABASE_URL = "sqlite+aiosqlite:///./factory.db"
engine = create_async_engine(DATABASE_URL)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session
""",

        "app/models/device.py": """
from __future__ import annotations
from sqlalchemy.orm import Mapped, mapped_column
from app.core.database import Base

class Device(Base):
    __tablename__ = "devices"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(index=True)
    status: Mapped[str] = mapped_column(default="offline")
    factory_id: Mapped[str] = mapped_column(index=True)
""",

        "app/core/logger.py": """
import structlog
def setup_logging():
    structlog.configure(
        processors=[
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer()
        ],
        logger_factory=structlog.PrintLoggerFactory()
    )
logger = structlog.get_logger()
""",

        "app/core/middleware.py": """
import uuid, time
from app.core.logger import logger
async def logging_middleware(request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        "http_request", 
        path=request.url.path, 
        status_code=response.status_code, 
        duration=f"{duration:.4f}s", 
        request_id=request_id
    )
    return response
""",

        "app/api/v1/endpoints/factory.py": """
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.device import Device
from app.core.database import get_db
from pydantic import BaseModel

router = APIRouter()

class LoginRequest(BaseModel):
    username: str
    password: str

@router.post("/login")
async def login(request: LoginRequest):
    if request.username == "admin":
        return {"access_token": "mock-token-123", "token_type": "bearer"}
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.get("/devices/{device_id}")
async def get_device(device_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Device).filter(Device.id == device_id))
    device = result.scalar_one_or_none()
    if not device: 
        raise HTTPException(status_code=404, detail="Device not found")
    return {"name": device.name, "metadata": {"firmware": "v1.2.3"}}
""",

        "app/api/v1/endpoints/ai.py": """
from fastapi import APIRouter, Query
router = APIRouter()
@router.post("/ask")
async def ask_ai(prompt: str = Query(...)):
    return {"factory_response": "Mocked AI Response", "input_received": prompt}
""",

        "app/main.py": """
from __future__ import annotations
from fastapi import FastAPI
from app.api.v1.endpoints import ai, factory
from app.core.logger import setup_logging
from app.core.middleware import logging_middleware

def create_app():
    setup_logging()
    app = FastAPI(title="Factory OS Enterprise")
    @app.middleware("http")
    async def add_logging(request, call_next):
        return await logging_middleware(request, call_next)
    app.include_router(ai.router, prefix="/api/v1/ai")
    app.include_router(factory.router, prefix="/api/v1")
    return app
app = create_app()
""",

        "tests/mock_data.py": """
MOCK_DEVICES = [{"id": 1, "name": "CNC-001", "status": "running", "factory_id": "TW_01"}]
""",

        "tests/conftest.py": """
from __future__ import annotations
import pytest, pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.main import app
from app.core.database import Base, get_db
from app.models.device import Device
from tests.mock_data import MOCK_DEVICES

@pytest_asyncio.fixture()
async def db_session():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, class_=AsyncSession)
    async with session_factory() as session:
        for d in MOCK_DEVICES: session.add(Device(**d))
        await session.commit()
        yield session

@pytest_asyncio.fixture()
async def client(db_session):
    async def _get_db(): yield db_session
    app.dependency_overrides[get_db] = _get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as c:
        yield c
    app.dependency_overrides.clear()
""",

        "tests/test_api.py": """
import pytest
@pytest.mark.asyncio
async def test_ai_ask_endpoint(client):
    res = await client.post("/api/v1/ai/ask?prompt=Hello")
    assert res.status_code == 200
""",

        "tests/test_complex_logic.py": """
import pytest
@pytest.mark.asyncio
async def test_admin_can_access_device_metadata(client):
    login_res = await client.post("/api/v1/login", json={"username": "admin", "password": "123"})
    token = login_res.json()["access_token"]
    res = await client.get("/api/v1/devices/1", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["name"] == "CNC-001"
"""
    }

    # 3. 生成檔案
    print("🛠️  1. Generating Industrial Structure...")
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        (Path(d) / "__init__.py").touch()

    for path, content in files.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(content.strip())
        print(f"   ✅ Created: {path}")

    # 4. 自動化安裝與版本鎖定 (修復版)
    print("\n📦 2. Synchronizing Environment with Poetry...")
    
    try:
        # 移除 --no-update，確保相容舊版 Poetry
        print("   👉 Running: poetry lock")
        subprocess.run(["poetry", "lock"], check=True)
        
        print("   👉 Running: poetry install")
        subprocess.run(["poetry", "install"], check=True)
        print("   ✅ Environment synchronized and packages installed!")
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(f"\n   ❌ Poetry execution failed.")
        print("   👉 If you have poetry installed, try running these manually:")
        print("      poetry lock")
        print("      poetry install")

    print("\n" + "="*45)
    print("🎉 FACTORY OS DEPLOYED SUCCESSFULLY!")
    print("="*45)
    print("Quick Start Commands:")
    print("1. poetry shell")
    print("2. PYTHONPATH=. pytest")
    print("3. uvicorn app.main:app --reload")
    print("="*45)

if __name__ == "__main__":
    create_factory_structure()