import os
from contextlib import asynccontextmanager

from environment import get_resource_path, isProd
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from for_ffmpeg.api import routers
from for_ffmpeg.db import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


# 创建 FastAPI 应用
app = FastAPI(
    title="桌面应用后端",
    version="1.0.0",
    description="为桌面应用提供API服务的FastAPI后端",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许所有来源
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

print(f"当前环境: {isProd()}")
if isProd():
    # 挂载 API 路由
    for router in routers:
        app.include_router(router, prefix="/api")

    app.mount(
        "/static",
        StaticFiles(directory=get_resource_path("dist/static")),
        name="static",
    )

    @app.get("/{full_path:path}")
    async def catch_all(request: Request, full_path: str):
        # 排除API和静态文件请求
        if not full_path.startswith(("api/", "static/")):
            return FileResponse(get_resource_path("dist/index.html"))
        else:
            return JSONResponse(status_code=404, content={"detail": "Not Found X"})

else:
    # 挂载 API 路由
    for router in routers:
        app.include_router(router)


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception):
    return JSONResponse(
        content={"error5": "Internal server error", "detail": str(exc)}, status_code=500
    )


# 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(status_code=exc.status_code, content={"errorH": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    print(f"未处理的异常: {str(exc)}")
    return JSONResponse(status_code=500, content={"errorE": "内部服务器错误"})
