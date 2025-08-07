import multiprocessing
import sys
import threading
import time
from contextlib import asynccontextmanager
from pathlib import Path

import uvicorn
import webview
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from .db import init_db
from .util import PORTS
from .api import routers


def get_resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", Path.cwd())
    return base_path / relative_path


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
    allow_origins=["http://localhost:" + str(PORTS["APP"])],  # 添加前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 挂载 API 路由
for router in routers:
    app.include_router(router)


# 异常处理
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    """HTTP异常处理"""
    return JSONResponse(status_code=exc.status_code, content={"error": exc.detail})


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """通用异常处理"""
    print(f"未处理的异常: {str(exc)}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "内部服务器错误"})


def start_api_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=PORTS["API"])
    server = uvicorn.Server(config)
    server.run()


async def main():
    # 生产环境入口（打包后调用）
    dist_path = get_resource_path("dist")
    if dist_path.exists():
        app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
        print(f"已挂载前端静态文件: {dist_path}")
    else:
        print(f"前端构建目录不存在: {dist_path}")

    print("启动API服务器...")
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    print("API服务器已启动")
    print("启动桌面应用...")
    try:
        webview.create_window(
            "桌面应用",
            url="/",
            width=1200,
            height=800,
            http_port=PORTS["DESKTOP"],
        )
        webview.start()
        print("桌面应用已启动")
    except Exception as e:
        print(f"启动WebView时出错: {e}")


def start_fastapi():
    """启动FastAPI服务器"""
    uvicorn.run(
        "tool_oxr.main:app",
        host="0.0.0.0",
        port=PORTS["API"],
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
            url=f"http://localhost:{PORTS['APP']}",
            width=1200,
            height=800,
            http_port=PORTS["DESKTOP"],
        )
        webview.start(debug=True)
    except Exception as e:
        print(f"启动WebView时出错: {e}")


if __name__ == "__main__":
    run_dev()
