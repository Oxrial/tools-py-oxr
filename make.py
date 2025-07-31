import sys
import time
import subprocess
from pathlib import Path
from scripts.util import (
    BASE_DIR,
    BACKEND_DIR,
    FRONTEND_DIR,
    run_command,
    get_pnpm_path,
    get_uv_python,
    write_exit_signal,
    remove_exit_signal,
)


def install_dev():
    """安装开发依赖"""
    print("安装开发依赖...")
    success = True

    # 前端依赖
    if not (FRONTEND_DIR / "node_modules").exists():
        print("安装前端依赖...")
        try:
            # 直接执行命令，不通过 run_command
            subprocess.run(
                [get_pnpm_path(), "install"],
                cwd=FRONTEND_DIR,
                stdout=sys.stdout,  # 直接输出到控制台
                stderr=sys.stderr,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"前端安装失败: {e}")
            success = False
    else:
        print("前端依赖已存在，跳过安装")

    # 后端依赖
    venv_dir = BACKEND_DIR / ".venv"

    if success and not venv_dir.exists():
        print("创建 Python 虚拟环境...")
        try:
            subprocess.run(
                ["uv", "venv", ".venv"],
                cwd=BACKEND_DIR,
                stdout=sys.stdout,  # 直接输出到控制台
                stderr=sys.stderr,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"虚拟环境创建失败: {e}")
            success = False
    else:
        print("Python 虚拟环境已存在，跳过创建")

    # 后端依赖安装
    if success:
        print("安装 Python 依赖...")
        try:
            subprocess.run(
                ["uv", "pip", "install", "-e", "."],
                cwd=BACKEND_DIR,
                stdout=sys.stdout,  # 直接输出到控制台
                stderr=sys.stderr,
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"依赖安装失败: {e}")
            success = False

    if success:
        print("开发依赖安装完成")
    else:
        print("开发依赖安装失败")
    return success


def run_dev():
    """启动开发环境"""
    print("启动开发环境...")

    # 确保信号文件不存在
    remove_exit_signal()

    # 确保依赖已安装
    if not (FRONTEND_DIR / "node_modules").exists():
        print("前端依赖未安装，自动安装中...")
        if not install_dev():
            print("安装失败，退出")
            return

    # 直接运行 dev.py
    dev_script = BASE_DIR / "scripts" / "dev.py"
    cmd = [sys.executable, "-u", str(dev_script)]  # 无缓冲输出

    print(f"执行命令: {' '.join(cmd)}")
    print(f"工作目录: {str(BASE_DIR)}")

    try:
        # 创建进程
        proc = subprocess.Popen(
            cmd,
            cwd=str(BASE_DIR),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            text=True,
            bufsize=1,
        )

        # 实时读取输出
        try:
            while True:
                line = proc.stdout.readline()
                if not line and proc.poll() is not None:
                    break
                if line:
                    # 移除可能的额外换行符
                    line = line.rstrip("\n")
                    print(line)
        except KeyboardInterrupt:
            print("\n收到中断信号，停止开发环境...")
            # 发送退出信号
            write_exit_signal()

            # 等待进程退出
            try:
                print("等待开发进程退出...")
                proc.wait(timeout=10)
                print("开发环境已停止")
            except subprocess.TimeoutExpired:
                print("进程未响应，强制终止...")
                proc.kill()
                proc.wait()
        except Exception as e:
            print(f"读取输出时出错: {e}")
        finally:
            # 确保清理信号文件
            remove_exit_signal()
            if proc.poll() is None:
                proc.kill()
                proc.wait()
    except Exception as e:
        print(f"启动开发环境失败: {e}")
    finally:
        # 最终清理
        remove_exit_signal()


def build_prod():
    """构建生产环境"""
    print("构建生产环境...")

    # 构建前端
    print("构建前端生产包...")
    run_command(["pnpm", "run", "build"], cwd="app")

    # 构建后端
    print("构建后端生产包...")
    run_command(["uv", "pip", "install", "--only-binary=:all", "."], cwd="server")

    print("生产构建完成")


def package_desktop():
    """打包桌面应用"""
    print("打包桌面应用...")

    # 确保生产构建已完成
    if not Path("dist").exists():
        print("生产构建不存在，自动构建中...")
        build_prod()

    # 执行打包
    run_command(["python", "scripts/desktop.py"])
    print("桌面应用打包完成")


def main():
    commands = {
        "install": install_dev,
        "dev": run_dev,
        "build": build_prod,
        "desktop": package_desktop,
    }

    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("可用命令:")
        print("  install     安装开发依赖")
        print("  dev         启动开发环境")
        print("  build       构建生产环境")
        print("  desktop     打包桌面应用")
        return

    command_name = sys.argv[1]
    # 执行命令
    commands[command_name]()


if __name__ == "__main__":
    main()
