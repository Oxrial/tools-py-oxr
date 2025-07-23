"""Main"""

import sys
import os
import logging
import threading
import time
import webview
from flask import Flask, send_from_directory
from routes.create_api import file_bp
import waitress

# ====================== 配置区域 ======================
APP_NAME = "Tools-py-oxr"  # 应用名称
PORT = 58462  # 服务器端口（选择不常用端口）
DEBUG_MODE = False  # 调试模式开关（打包时设为False）
LOG_FILE = "app_debug.log"  # 日志文件路径
GUI_ENGINE = "edgechromium"  # WebView引擎: 'edgechromium', 'cef', 'mshtml'
# =====================================================


def setup_logging():
    """配置日志系统"""
    logging.basicConfig(
        filename=LOG_FILE if not DEBUG_MODE else None,
        level=logging.DEBUG,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # 同时输出到控制台（仅调试模式）
    if DEBUG_MODE:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        )
        logging.getLogger().addHandler(console_handler)

    logging.info("=" * 50)
    logging.info("%s 启动", APP_NAME)
    logging.info("Python 版本: %s", sys.version)
    logging.info("系统平台: %s", sys.platform)
    logging.info("工作目录: %s", os.getcwd())
    logging.info("=" * 50)


def get_base_path():
    """安全获取应用程序基础路径"""
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path):
    """
    获取资源的绝对路径（兼容打包环境）
    打包后资源位于 sys._MEIPASS 指向的临时目录
    """
    try:
        # PyInstaller/Nuitka 打包后的临时目录
        base_path = get_base_path()
    except AttributeError:
        # 开发环境使用当前目录
        base_path = os.path.abspath(".")

    path = os.path.join(base_path, relative_path)
    logging.debug("资源路径解析: %s => %s", relative_path, path)
    return path


def create_flask_app():
    """创建并配置Flask服务器"""
    app = Flask(__name__, static_folder=None)

    # 前端静态文件目录
    frontend_dist = get_resource_path("dist")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        """服务前端文件"""
        if not path or path == "index.html":
            return send_from_directory(frontend_dist, "index.html")

        # 检查文件是否存在
        file_path = os.path.join(frontend_dist, path)
        if os.path.exists(file_path):
            return send_from_directory(frontend_dist, path)

        # 处理Vue Router的路由回退
        return send_from_directory(frontend_dist, "index.html")

    logging.info("Flask应用初始化完成，静态文件目录: %s", frontend_dist)
    return app


def start_flask_server(app, port):
    """在后台线程中启动Flask服务器"""

    def run_server():
        logging.info("启动Flask服务器，端口: %s", port)
        if DEBUG_MODE:
            # 调试模式使用Flask自带服务器
            app.run(port=port, debug=False, use_reloader=False)
        else:
            # 生产环境使用waitress
            waitress.serve(app, port=port, threads=4)

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()
    return server_thread


def check_webview_ready(window, timeout=30):
    """
    检查WebView是否初始化完成
    :param window: WebView窗口实例
    :param timeout: 超时时间（秒）
    """
    start_time = time.time()
    while not window.loaded:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            logging.error("WebView初始化超时 (%s秒)", timeout)
            return False
        time.sleep(0.5)

    logging.info("WebView初始化成功")
    return True


def main():
    """主应用逻辑"""
    # setup_logging()

    # 1. 创建并启动Flask服务器
    flask_app = create_flask_app()
    server_thread = start_flask_server(flask_app, PORT)

    # 2. 创建WebView窗口
    try:
        url = f"http://localhost:{PORT}" if not DEBUG_MODE else "http://localhost:5173"
        logging.info("创建WebView窗口，URL: %s", url)

        window = webview.create_window(
            title=APP_NAME,
            url=url,
            width=1200,
            height=800,
            min_size=(800, 600),
            text_select=True,
            confirm_close=True,
        )

        # 3. 启动WebView
        logging.info("启动WebView，使用引擎: %s", GUI_ENGINE)
        webview.start(
            func=lambda: check_webview_ready(window),
            gui=GUI_ENGINE,
            debug=DEBUG_MODE,
            http_server=True,
        )
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logging.exception("应用启动失败")
        # 显示错误消息
        err_html = f"""
        <html><body style="font-family: Arial; padding: 20px; color: #721c24; background-color: #f8d7da;">
            <h1>应用启动失败</h1>
            <p><strong>错误信息:</strong> {str(e)}</p>
            <p>请查看日志文件获取详细信息: {os.path.abspath(LOG_FILE)}</p>
        </body></html>
        """
        webview.create_window("启动错误", html=err_html, width=600, height=400)
        webview.start(gui=GUI_ENGINE)
    finally:
        # 确保服务器线程结束
        if server_thread.is_alive():
            logging.info("停止Flask服务器")
            # 实际生产环境中需要更优雅的关闭方式
            # 这里简单等待线程结束
            server_thread.join(timeout=5.0)

        logging.info("应用退出")


if __name__ == "__main__":
    # 异常捕获
    try:
        main()
    except SystemExit:
        pass
    # pylint: disable=broad-exception-caught
    except Exception as e:
        logging.exception("未捕获的全局异常")
        # 创建错误窗口
        ERROR_HTML = f"""
        <html><body style="font-family: Arial; padding: 20px; color: #721c24; background-color: #f8d7da;">
            <h1>致命错误</h1>
            <p><strong>错误信息:</strong> {str(e)}</p>
            <p>请查看日志文件获取详细信息: {os.path.abspath(LOG_FILE)}</p>
        </body></html>
        """
        webview.create_window("致命错误", html=ERROR_HTML, width=600, height=400)
        webview.start(gui=GUI_ENGINE)
