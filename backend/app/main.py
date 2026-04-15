from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.routers import shops, photos, uploads


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Ensure upload directory exists on startup
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="桜探記 API",
    description="日本店舖探訪記錄平台後端接口",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS（允許前端 dev server 跨域） ─────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static files（本地開發圖片訪問） ─────────────────────────────
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")

# ── Routers ──────────────────────────────────────────────────────
app.include_router(shops.router,   prefix="/api")
app.include_router(photos.router,  prefix="/api")
app.include_router(uploads.router, prefix="/api")


@app.get("/", tags=["health"])
async def root():
    return {"status": "ok", "service": "桜探記 API", "version": "1.0.0"}
