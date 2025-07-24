"""Main"""

import sys
import os
import logging
import threading
import time
import webview
from flask import Flask, send_from_directory
from flasgger import Swagger
from flasgger.utils import swag_from
from api.file import file_bp
from api.sys import sys_bp
import waitress

# ====================== 配置区域 ======================
APP_NAME = "Tools-py-oxr"  # 应用名称
PORT = 58462  # 服务器端口（选择不常用端口）
DEBUG_MODE = True  # 调试模式开关（打包时设为False）
LOG_FILE = "app_debug.log"  # 日志文件路径
GUI_ENGINE = "edgechromium"  # WebView引擎: 'edgechromium', 'cef', 'mshtml'
# =====================================================


def setup_logging():
    """配置日志系统，确保在打包环境下也能正确输出"""
    # 创建日志目录
    log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 设置日志文件名（带时间戳）
    log_file = os.path.join(log_dir, f"app_{time.strftime('%Y%m%d_%H%M%S')}.log")

    # 创建日志格式
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 配置根日志记录器
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    # 文件处理器（始终启用）
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # 控制台处理器（仅开发环境启用）
    if getattr(sys, "frozen", False):
        # 打包环境 - 创建特殊控制台处理
        if sys.platform == "win32":
            # Windows 打包环境特殊处理
            try:
                # 尝试附加到父控制台（如果存在）
                import ctypes

                kernel32 = ctypes.WinDLL("kernel32")
                if kernel32.GetConsoleWindow():
                    console_handler = logging.StreamHandler(sys.stdout)
                    console_handler.setFormatter(formatter)
                    logger.addHandler(console_handler)
            except:
                pass
    else:
        # 开发环境 - 标准控制台输出
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    logger.info("=" * 50)
    logger.info(f"应用启动 - 日志文件: {log_file}")
    logger.info(f"Python 版本: {sys.version}")
    logger.info(f"系统平台: {sys.platform}")
    logger.info(f"工作目录: {os.getcwd()}")
    logger.info(f"可执行路径: {sys.executable}")
    logger.info("=" * 50)

    return log_file


LOG_FILE = setup_logging()


def get_base_path():
    """安全获取应用程序基础路径"""
    return getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))


def get_resource_path(relative_path):
    """获取资源的绝对路径（兼容打包环境）"""
    try:
        # PyInstaller/Nuitka 打包后的临时目录
        base_path = sys._MEIPASS
        logging.info(f"检测到打包环境，资源基路径: {base_path}")
    except AttributeError:
        # 开发环境使用当前目录
        base_path = os.path.abspath(".")
        logging.info(f"开发环境，资源基路径: {base_path}")

    path = os.path.join(base_path, relative_path)
    logging.info(f"资源路径解析: {relative_path} -> {path}")
    return path


def create_flask_app():
    """创建并配置Flask服务器"""
    app = Flask(__name__, static_folder=None)
    Swagger(app)
    app.register_blueprint(file_bp)
    app.register_blueprint(sys_bp)
    # 前端静态文件目录
    frontend_dist = get_resource_path("dist")
    logging.info(f"前端静态文件目录: {frontend_dist}")

    # 验证前端文件是否存在
    index_path = os.path.join(frontend_dist, "index.html")
    if not os.path.exists(index_path):
        logging.error(f"index.html 不存在: {index_path}")

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    @swag_from("index.yml")
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
        try:
            if DEBUG_MODE:
                app.run(port=port, debug=False, use_reloader=False)
            else:
                waitress.serve(app, port=port, threads=4)
        except Exception as e:
            logging.exception(f"服务器启动失败: {str(e)}")

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
    while not window.events.loaded:
        elapsed = time.time() - start_time
        if elapsed > timeout:
            logging.error("WebView初始化超时 (%s秒)", timeout)
            return False
        time.sleep(0.5)

    logging.info("WebView初始化成功")
    return True


def create_window():
    """创建WebView窗口"""
    # 根据环境确定URL
    if DEBUG_MODE:
        url = "http://localhost:5173"
        logging.info("开发模式: 使用Vite开发服务器")
    else:
        url = f"http://localhost:{PORT}"
        logging.info(f"生产模式: 使用本地服务器端口 {PORT}")

    logging.info(f"创建WebView窗口，URL: {url}")

    window = webview.create_window(
        title=APP_NAME,
        url=url,
        width=1200,
        height=800,
        min_size=(800, 600),
        text_select=True,
        confirm_close=True,
    )

    # 添加加载事件
    def on_loaded():
        logging.info("WebView窗口加载完成")

    window.events.loaded += on_loaded
    return window


def start_webview():
    """启动WebView"""
    logging.info(f"启动WebView，使用引擎: {GUI_ENGINE}")

    try:
        webview.start(debug=DEBUG_MODE, gui=GUI_ENGINE)
    except Exception as e:
        logging.error(f"引擎 {GUI_ENGINE} 失败: {str(e)}")
        # 尝试备选引擎
        fallback_engines = ["cef", "mshtml", "qt"]
        for engine in fallback_engines:
            try:
                logging.info(f"尝试备选引擎: {engine}")
                webview.start(debug=DEBUG_MODE, gui=engine)
                break
            except Exception:
                continue


def main():
    """主应用逻辑"""
    setup_logging()

    # 1. 创建并启动Flask服务器
    flask_app = create_flask_app()
    server_thread = start_flask_server(flask_app, PORT)

    # 2. 创建WebView窗口
    try:
        url = f"http://localhost:{PORT}" if not DEBUG_MODE else "http://localhost:5173"
        logging.info("创建WebView窗口，URL: %s", url)

        window = create_window()

        # 4. 启动WebView
        start_webview()
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
