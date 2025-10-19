import multiprocessing
import threading
import time

import uvicorn
import webview

from environment import PORTS, get_resource_path, isProd

# 全局变量存储服务器状态
server_ready = False

print(PORTS["API"])


def dev_fastapi():
    """启动FastAPI服务器"""
    uvicorn.run(
        "for_ffmpeg.main:app",
        host="0.0.0.0",
        port=PORTS["API"],
        reload=True,
        reload_dirs=[str(get_resource_path("server/src/for_ffmpeg"))],
    )


def run_dev():
    # 开发环境入口（调试用）用子进程启动 FastAPI，避免阻塞主线程
    api_proc = multiprocessing.Process(target=dev_fastapi)
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


def main_fastapi():
    """在子线程中运行FastAPI服务器"""

    from for_ffmpeg.main import app as fastapi_app

    global server_ready
    # 配置UVicorn
    config = uvicorn.Config(
        fastapi_app, host="127.0.0.1", port=PORTS["API"], log_level="debug"
    )
    server = uvicorn.Server(config)

    # 标记服务器已就绪
    server_ready = True

    # 启动服务器
    server.run()


def main():
    # 启动FastAPI服务器线程
    server_thread = threading.Thread(target=main_fastapi, daemon=True)
    server_thread.start()

    # 等待服务器启动
    while not server_ready:
        time.sleep(0.1)
    API_PORT_STR = str(PORTS["API"])
    # 创建并启动PyWebview窗口
    window = webview.create_window(
        "Tools-OXR",
        url=f"http://127.0.0.1:{API_PORT_STR}",
        width=1200,
        height=800,
        min_size=(800, 600),
        server_args={
            "port": PORTS["API"],  # 指定端口
            "directory": "dist",  # 托管静态文件目录
            "cors": True,  # 启用CORS
            "host": "127.0.0.1",  # 绑定本地地址
        },
    )

    # 启动应用
    webview.start(window)


if __name__ == "__main__":
    if isProd():
        main()
    else:
        run_dev()
