import os
import sys
import psutil
import signal
import time
from util import (
    run_command,
    get_uv_python,
    get_pnpm_path,
    ProcessWrapper,
    check_exit_signal,
    remove_exit_signal,
    BACKEND_DIR,
    FRONTEND_DIR,
    PORTS,
)


# 进程管理类
class ProcessManager:
    def __init__(self):
        self.processes = []
        self.running = True
        # 确保启动时信号文件不存在
        remove_exit_signal()
        # 设置信号处理
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        # 添加SIGBREAK处理（Windows特有）
        if sys.platform == "win32":
            try:
                signal.signal(signal.SIGBREAK, self.signal_handler)
            except AttributeError:
                pass  # 某些Python版本可能没有SIGBREAK

    def add_process(self, wrapper: ProcessWrapper):
        """添加进程到管理列表"""
        if wrapper:
            self.processes.append(wrapper)
            print(f"[OK] {wrapper.name} 已启动 (PID: {wrapper.proc.pid})")
            return True
        return False

    def start_backend(self):
        """启动 FastAPI 后端"""
        python_exe = get_uv_python()
        if not python_exe or not python_exe.exists():
            print(f"[ERROR] Python解释器不存在: {python_exe}")
            return None

        print("[START] 启动后端...")
        cmd = [
            str(python_exe),
            "-u",  # 无缓冲输出
            "-m",
            "uvicorn",
            "tool_oxr.main:app",
            "--reload",
            "--port",
            str(PORTS["RELOAD"]),
        ]
        return run_command(cmd, BACKEND_DIR, "Server")

    # APP
    def start_frontend(self):
        """启动 Vue 前端开发服务器"""
        pnpm_path = get_pnpm_path()
        if not pnpm_path:
            print("[ERROR] 未找到 pnpm，请确保已安装 pnpm")
            print("[HINT] 可以通过 npm 安装: npm install -g pnpm")
            return None
        cmd = [pnpm_path, "run", "dev"]
        return run_command(cmd, FRONTEND_DIR, "App")

    # DESKTOP-API
    def start_desktop(self):
        """启动 PyWebview 桌面应用"""
        python_exe = get_uv_python()
        if not python_exe or not python_exe.exists():
            print(f"[ERROR] Python解释器不存在: {python_exe}")
            return None

        cmd = [
            str(python_exe),
            "-u",
            "-c",
            "from tool_oxr.main import run_dev; run_dev()",
        ]
        return run_command(cmd, BACKEND_DIR, "Desktop")

    def signal_handler(self, signum, frame):
        """处理终止信号"""
        print("\n[STOP] 收到终止信号，停止所有进程...")
        self.running = False
        self.stop_processes()
        sys.exit(0)

    def stop_processes(self):
        """停止所有进程"""
        print(f"[INFO] 正在停止 {len(self.processes)} 个进程...")
        for wrapper in self.processes:
            if wrapper.proc.poll() is None:  # 进程仍在运行
                try:
                    print(f"[STOP] 停止 {wrapper.name} (PID: {wrapper.proc.pid})")
                    # 获取进程树
                    parent = psutil.Process(wrapper.proc.pid)
                    children = parent.children(recursive=True)

                    # 先终止子进程
                    for child in children:
                        try:
                            child.terminate()
                        except psutil.NoSuchProcess:
                            pass

                    # 终止主进程
                    try:
                        parent.terminate()
                    except psutil.NoSuchProcess:
                        pass

                    # 等待进程结束
                    gone, alive = psutil.wait_procs(children + [parent], timeout=3)

                    # 强制终止仍在运行的进程
                    for p in alive:
                        try:
                            p.kill()
                        except psutil.NoSuchProcess:
                            pass

                    print(f"[STOPPED] 已停止 {wrapper.name}")
                except Exception as e:
                    print(f"[ERROR] 停止进程 {wrapper.name} 失败: {str(e)}")

    def main_loop(self):
        """主循环，检查退出信号"""
        try:
            while self.running:
                # 检查退出信号文件
                if check_exit_signal():
                    print("\n[STOP] 检测到退出信号，停止所有进程...")
                    self.running = False
                    self.stop_processes()
                    break
                time.sleep(1)
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)


def main():
    # 设置开发模式环境变量
    os.environ["DEV_MODE"] = "1"
    print("=" * 50)
    print("启动开发环境 (UV 管理)")
    print("=" * 50)

    # 检查前端依赖
    if not (FRONTEND_DIR / "node_modules").exists():
        print("[WARN] 前端依赖未安装，正在安装...")
        install_wrapper = run_command(["pnpm", "install"], FRONTEND_DIR, "APP INSTALL")

        # 等待安装完成
        if install_wrapper:
            while install_wrapper.exit_code is None:
                time.sleep(0.5)

            if install_wrapper.exit_code == 0:
                print("[OK] 前端依赖安装完成")
            else:
                print("[ERROR] 前端依赖安装失败")
                sys.exit(1)
        else:
            print("[ERROR] 无法启动前端依赖安装")
            sys.exit(1)

    manager = ProcessManager()

    # 启动后端
    backend_wrapper = manager.start_backend()
    if not manager.add_process(backend_wrapper):
        print("[ERROR] 后端启动失败，退出")
        sys.exit(1)

    # 启动前端
    frontend_wrapper = manager.start_frontend()
    if frontend_wrapper is None:
        print("[ERROR] 前端启动失败，退出")
        manager.stop_processes()
        sys.exit(1)
    if not manager.add_process(frontend_wrapper):
        print("[ERROR] 前端启动失败，退出")
        manager.stop_processes()
        sys.exit(1)

    # 等待前端服务器启动
    print("[INFO] 等待前端服务器准备就绪...")
    time.sleep(5)  # 给前端服务器启动时间

    # 启动桌面应用
    desktop_wrapper = manager.start_desktop()
    if desktop_wrapper is None:
        print("[ERROR] 桌面应用启动失败")
        manager.stop_processes()
        sys.exit(1)
    if not manager.add_process(desktop_wrapper):
        print("[ERROR] 桌面应用启动失败")
        manager.stop_processes()
        sys.exit(1)

    print("[INFO] 所有进程已启动，进入监控循环...")
    manager.main_loop()  # 进入主循环监控退出信号
    print("[INFO] 开发环境已关闭")
    remove_exit_signal()


if __name__ == "__main__":
    main()
