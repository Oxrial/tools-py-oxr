import threading
import time
import uvicorn
import webview
from server.src.tool_oxr.main import app as fastapi_app, _PORTS

# 全局变量存储服务器状态
server_ready = False


def run_server():
    """在子线程中运行FastAPI服务器"""
    global server_ready

    # 配置UVicorn
    config = uvicorn.Config(
        fastapi_app, host="127.0.0.1", port=_PORTS["API"], log_level="info"
    )
    server = uvicorn.Server(config)

    # 标记服务器已就绪
    server_ready = True

    # 启动服务器
    server.run()


def on_loaded():
    """Webview加载完成后的回调"""
    print("Application loaded successfully")


def main():
    # 启动FastAPI服务器线程
    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    # 等待服务器启动
    while not server_ready:
        time.sleep(0.1)

    # 创建并启动PyWebview窗口
    url = f"http://127.0.0.1:${_PORTS['API']}"
    window = webview.create_window(
        "Tools-OXR",
        url,
        width=1200,
        height=800,
        min_size=(800, 600),
        http_port=_PORTS["API"],
    )

    # 绑定加载完成事件
    window.events.loaded += on_loaded

    # 启动应用
    webview.start(debug=True)


if __name__ == "__main__":
    main()
