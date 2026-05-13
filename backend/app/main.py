from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import auth, shops, photos, uploads


class StripPrefixMiddleware(BaseHTTPMiddleware):
    """剥离 nginx 未剥离的 /Sakura 前缀，对所有 HTTP 方法均生效。"""
    async def dispatch(self, request: Request, call_next):
        path = request.scope["path"]
        if path.startswith("/Sakura"):
            new_path = path[len("/Sakura"):] or "/"
            request.scope["path"] = new_path
            if "raw_path" in request.scope:
                request.scope["raw_path"] = new_path.encode()
        return await call_next(request)


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield


app = FastAPI(
    title="桜探記 API",
    description="日本店舖探訪記錄平台後端接口",
    version="1.0.0",
    lifespan=lifespan,
)

# ── CORS ─────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.origins_list + ["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Strip /Sakura prefix（处理 nginx 未剥离前缀的情况）──────────────
app.add_middleware(StripPrefixMiddleware)

# ── Routers ──────────────────────────────────────────────────────
app.include_router(auth.router,    prefix="/api")
app.include_router(shops.router,   prefix="/api")
app.include_router(photos.router,  prefix="/api")
app.include_router(uploads.router, prefix="/api")


# ── Health check ─────────────────────────────────────────────────
@app.get("/health", tags=["health"])
async def health():
    return {"status": "ok", "service": "桜探記 API", "version": "1.0.0"}


# ── 前端静态文件托管（catch-all，仅服务 SPA 页面与静态资源）──────────
FRONTEND_DIST = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"

@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # API 路径不应落入此处；若真的到了这里，说明该接口不存在，返回 404
    if full_path.startswith("api/") or full_path == "api":
        raise HTTPException(status_code=404, detail="API endpoint not found")

    # 优先匹配实际文件（JS/CSS/图片等静态资源）
    file_path = FRONTEND_DIST / full_path
    if file_path.is_file():
        return FileResponse(str(file_path))

    # 兼容 nginx 未剥离前缀时的路径（备用，中间件已覆盖大多数情况）
    stripped = full_path.split("/", 1)[-1] if "/" in full_path else full_path
    file_path2 = FRONTEND_DIST / stripped
    if file_path2.is_file():
        return FileResponse(str(file_path2))

    # 其余所有路径均返回 index.html，交由 Vue Router 处理
    index = FRONTEND_DIST / "index.html"
    if not index.exists():
        raise HTTPException(status_code=503, detail="Frontend not built")
    return FileResponse(str(index))
