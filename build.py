import subprocess
import sys
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


def run_cmd(cmd, cwd=None):
    print("Executing:", " ".join(cmd))
    subprocess.run(cmd, cwd=cwd, check=True)


def build_frontend():
    print("构建前端生产包...")
    # 调用 pnpm 构建前端生产包，前端代码位于 app 目录
    run_cmd([get_pnpm_path(), "run", "build"], cwd=Path("app"))


def build_backend():
    print("构建后端生产包...")
    # 使用 uv 安装后端依赖或构建生产包，后端代码位于 server 目录
    run_cmd(["uv", "pip", "install", "--only-binary=:all", "."], cwd=Path("server"))


def package_desktop():
    print("打包桌面应用...")
    # 执行桌面打包脚本，此处假设使用 scripts/desktop.py 进行打包
    run_cmd([get_uv_python(), "scripts/desktop.py"], cwd=Path("."))


def main():
    try:
        build_frontend()
        build_backend()
        package_desktop()
        print("桌面程序打包完成")
    except subprocess.CalledProcessError as e:
        print(f"打包过程中出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
