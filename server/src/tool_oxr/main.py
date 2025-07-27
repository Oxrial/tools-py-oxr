import os
import sys
import webview
import threading
import uvicorn
import signal
import atexit
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from scripts.util import PORTS

# 导入 API 路由
from .api import router as api_router
from scripts.util import remove_exit_signal, write_exit_signal, PORTS

# 全局变量用于控制服务器
server_running = True
api_thread = None

# 创建 FastAPI 应用
app = FastAPI(
    title="桌面应用后端",
    version="1.0.0",
    description="为桌面应用提供API服务的FastAPI后端",
    openapi_url="/api/openapi.json",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# 配置 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:" + str(PORTS["APP"])],  # 添加前端开发服务器地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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


# 挂载 API 路由
app.include_router(api_router)


def get_resource_path(relative_path):
    """跨平台资源路径获取"""
    base_path = getattr(sys, "_MEIPASS", Path.cwd())
    return base_path / relative_path


def start_api_server():
    """启动 FastAPI 服务器"""
    global server_running
    config = uvicorn.Config(app, host="0.0.0.0", port=PORTS["API"])
    server = uvicorn.Server(config)

    try:
        while server_running:
            server.run()
    except Exception as e:
        print(f"服务器错误: {e}")


def run_dev():
    """开发模式运行"""
    global server_running, api_thread
    print(f"启动WebView端口: {str(PORTS['DESKTOP'])}，API：{str(PORTS['API'])}")
    # 设置无缓冲输出
    sys.stdout = os.fdopen(sys.stdout.fileno(), "w", buffering=1)
    sys.stderr = os.fdopen(sys.stderr.fileno(), "w", buffering=1)

    # 确保信号文件不存在
    remove_exit_signal()

    # 设置信号处理
    def shutdown(signum=None, frame=None):
        global server_running
        if not server_running:
            return  # 防止重复调用
        print("\n收到关闭信号，正在停止服务...")
        server_running = False

        write_exit_signal()

        # 关闭所有webview窗口
        try:
            for window in webview.windows:
                try:
                    window.destroy()
                except Exception as e:
                    print(f"关闭窗口时出错: {e}")
        except Exception as e:
            print(f"获取窗口列表时出错: {e}")

        # 确保API线程正确退出
        if api_thread and api_thread.is_alive():
            try:
                api_thread.join(timeout=1.0)
                print(f"API线程退出")
            except Exception as e:
                print(f"等待API线程退出时出错: {e}")

        print("\n服务结束...")
        # 强制退出进程
        sys.exit(0)

    # 更强大的信号处理注册
    for sig in [signal.SIGINT, signal.SIGTERM, signal.SIGBREAK]:
        try:
            signal.signal(sig, shutdown)
        except AttributeError:
            pass  # 某些信号在特定平台上不可用

    # Windows特有信号
    if sys.platform == "win32":
        try:
            signal.signal(signal.SIGBREAK, shutdown)
        except AttributeError:
            pass
    atexit.register(shutdown)

    # 启动 API 服务器线程
    api_thread = threading.Thread(target=start_api_server, daemon=True)
    api_thread.start()

    # 挂载前端静态文件（生产环境）
    if not os.getenv("DEV_MODE"):
        dist_path = get_resource_path("dist")
        if dist_path.exists():
            app.mount("/", StaticFiles(directory=dist_path, html=True), name="static")
            print(f"已挂载前端静态文件: {dist_path}")
        else:
            print(f"前端构建目录不存在: {dist_path}")

    try:
        # 创建窗口
        window = webview.create_window(
            "开发模式",
            url=f"http://localhost:{PORTS['APP']}" if os.getenv("DEV_MODE") else "/",
            width=1200,
            height=800,
            http_port=PORTS["DESKTOP"],
        )
        webview.start(debug=bool(os.getenv("DEV_MODE")))
    except Exception as e:
        print(f"启动WebView时出错: {e}")
        shutdown()
    finally:
        shutdown()
