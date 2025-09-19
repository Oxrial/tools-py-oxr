import multiprocessing
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
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from tool_oxr.db import init_db
from tool_oxr.util import PORTS, build_logger
from tool_oxr.api import routers

log = build_logger(__name__)


# 添加环境检测函数
def is_frozen():
    """检查是否在打包环境中运行"""
    return hasattr(sys, "frozen") or hasattr(sys, "_MEIPASS")


def get_resource_path(relative_path):
    if is_frozen():
        # 打包后的环境
        base_path = Path(sys._MEIPASS)
    else:
        # 开发环境
        base_path = Path.cwd()
    return base_path / relative_path


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

from fastapi.responses import FileResponse


@app.get("/{full_path:path}")
async def spa_fallback(full_path: str):
    index_file = get_resource_path("dist") / "index.html"
    if index_file.exists():
        return FileResponse(index_file)
    raise HTTPException(status_code=404, detail="Not Found")


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


def start_api_server():
    config = uvicorn.Config(app, host="0.0.0.0", port=_PORTS["API"])
    server = uvicorn.Server(config)
    server.run()


async def main():
    # 生产环境入口（打包后调用）
    dist_path = get_resource_path("dist")
    if dist_path.exists():
        app.mount("/static", StaticFiles(directory=dist_path, html=True), name="static")
        log.info(f"已挂载前端静态文件: {dist_path}")
    else:
        log.info(f"前端构建目录不存在: {dist_path}")
        # 尝试其他可能的路径
        alt_paths = [
            Path(__file__).parent.parent / "dist",
            Path(sys.executable).parent / "dist",
            Path.cwd() / "dist",
        ]

        for alt_path in alt_paths:
            if alt_path.exists():
                app.mount(
                    "/", StaticFiles(directory=alt_path, html=True), name="static"
                )
                log.info(f"已挂载前端静态文件: {alt_path}")
                break
        else:
            log.error("所有可能的前端路径都不存在")

    log.info(f"启动API服务器在端口 {_PORTS['API']}...")
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()
    log.info("API服务器已启动")
    log.info("启动桌面应用...")
    try:
        webview.create_window(
            "桌面应用",
            url=f"http://localhost:{_PORTS['API']}",
            width=1200,
            height=800,
        )
        webview.start(debug=True)
        log.info("桌面应用已启动")
    except Exception as e:
        log.error(f"启动WebView时出错: {e}")
        # 在打包环境中，可能需要使用不同的方式启动
        try:
            index_path = dist_path / "index.html"
            if index_path.exists():
                window = webview.create_window(
                    "桌面应用",
                    url=f"file:///{index_path}",
                    width=1200,
                    height=800,
                )
                webview.start()
                log.info("使用本地文件启动成功")
        except Exception as file_err:
            log.error(f"使用本地文件启动也失败: {file_err}")


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
            http_port=PORTS["DESKTOP"],
        )
        webview.start(debug=True)
    except Exception as e:
        log.error(f"启动WebView时出错: {e}")


if __name__ == "__main__":
    # 根据环境选择入口点
    if is_frozen():
        # 打包环境 - 使用生产模式
        log.info(f"运行在打包环境，使用生产模式${ str(is_frozen())}")
        import asyncio

        asyncio.run(main())
    else:
        # 开发环境 - 使用开发模式
        log.info(f"运行在开发环境，使用开发模式${ str(is_frozen())}")
        run_dev()
