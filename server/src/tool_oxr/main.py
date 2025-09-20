import multiprocessing
import os
import sys
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path
import socket

import uvicorn
import webview
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from tool_oxr.db import init_db
from tool_oxr.util import PORTS, build_logger
from tool_oxr.api import routers

log = build_logger(__name__)


def get_resource_path(relative_path: str) -> Path:
    try:
        # 打包后资源路径
        base_path = sys._MEIPASS
    except Exception:
        # 开发环境资源路径
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def find_available_port(start_port, max_attempts=10):
    """查找可用的端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    return start_port  # 如果找不到可用端口，返回原始端口


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


API_PORT = find_available_port(PORTS["API"])
DESKTOP_PORT = find_available_port(PORTS["DESKTOP"])
APP_PORT = find_available_port(PORTS["APP"])

_PORTS = {"API": API_PORT, "DESKTOP": DESKTOP_PORT, "APP": APP_PORT}

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

frontend_dist = get_resource_path("dist")

index_file = get_resource_path("dist/index.html")


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    if os.path.exists(index_file):
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not Found X")


# 根路径重定向到前端
@app.get("/")
async def root():
    log.info("访问根index.html")
    return FileResponse(index_file)


# 根路径重定向到前端
@app.get("/404")
async def for404():
    log.info("访问根index.html")
    return FileResponse(index_file)


# 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    log.error(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "内部服务器错误"})


# 挂载 API 路由
for router in routers:
    app.include_router(router, prefix="/api")

if os.path.exists(frontend_dist):
    app.mount("/app", StaticFiles(directory=frontend_dist, html=True), name="dist")


def start_fastapi():
    """启动FastAPI服务器"""
    uvicorn.run(
        "tool_oxr.main:app",
        host="0.0.0.0",
        port=_PORTS["API"],
        reload=True,
        reload_dirs=[str(Path(__file__).parent)],
    )


def run_dev():
    # 开发环境入口（调试用）用子进程启动 FastAPI，避免阻塞主线程
    api_proc = multiprocessing.Process(target=start_fastapi)
    api_proc.start()
    time.sleep(2)
    try:
        webview.create_window(
            "开发模式",
            url=f"http://localhost:{_PORTS['APP']}",
            width=1200,
            height=800,
            http_port=_PORTS["DESKTOP"],
        )
        webview.start(debug=True)
    except Exception as e:
        log.error(f"启动WebView时出错: {e}")


if __name__ == "__main__":
    run_dev()
