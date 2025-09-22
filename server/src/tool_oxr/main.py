import multiprocessing
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
from util import PORTS, get_resource_path
from tool_oxr.api import routers


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


# 挂载 API 路由
for router in routers:
    app.include_router(router, prefix="/api")


app.mount(
    "/static", StaticFiles(directory=get_resource_path("dist/static")), name="static"
)


@app.get("/{full_path:path}")
async def catch_all(request: Request, full_path: str):
    # 排除API和静态文件请求
    if not full_path.startswith(("api/", "static/")):
        return FileResponse(get_resource_path("dist/index.html"))
    else:
        return JSONResponse(status_code=404, content={"detail": "Not Found X"})


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
        print(f"启动WebView时出错: {e}")


if __name__ == "__main__":
    run_dev()
