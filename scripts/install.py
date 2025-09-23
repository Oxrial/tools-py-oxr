import subprocess
import sys
from pathlib import Path

from environment import BACKEND_DIR, FRONTEND_DIR, get_pnpm_path, get_uv_python


def install_dev():
    """安装开发依赖"""
    print("安装开发依赖...")
    success = True

    # 前端依赖
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


def main():
    # 执行命令
    install_dev()


if __name__ == "__main__":
    main()
