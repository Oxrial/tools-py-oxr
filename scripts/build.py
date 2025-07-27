import subprocess
import sys
from pathlib import Path
from util import run_command

BASE_DIR = Path(__file__).parent.parent


def build_frontend():
    """构建前端"""
    print("🚀 构建前端...")
    run_command(["pnpm", "run", "build"], cwd=BASE_DIR / "app")
    print("✅ 前端构建完成")


def build_backend():
    """构建后端"""
    print("🚀 构建后端...")
    subprocess.run(
        ["uv", "pip", "install", "-e", "."],
        cwd=BASE_DIR / "server",
        check=True,
    )
    print("✅ 后端构建完成")


def main():
    build_frontend()
    build_backend()
    print("🎉 生产构建完成")


if __name__ == "__main__":
    main()
