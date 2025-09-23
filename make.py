import subprocess
import sys

from environment import get_uv_python


def run_cmd(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, check=True)


def package_desktop():
    """打包桌面应用"""
    print("打包桌面应用...")
    cmd = [get_uv_python(), "scripts/desktop.py"]
    print(cmd)
    # 执行打包
    run_cmd(cmd)
    print("桌面应用打包完成")


def package_install():
    print("安装依赖...")

    # 执行打包
    run_cmd([get_uv_python(), "scripts/install.py"])
    print("安装依赖完成")


def main():
    commands = {
        "install": package_install,
        "desktop": package_desktop,
    }
    # 如果未传入命令或者命令不在列表中，默认使用 "desktop"
    cmd = sys.argv[1] if len(sys.argv) >= 2 and sys.argv[1] in commands else "desktop"
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print("未指定有效命令，默认使用 'desktop'")
        print("可用命令:")
        print("  install     安装开发依赖")
        print("  desktop     打包桌面应用")

    # 执行命令
    commands[cmd]()


if __name__ == "__main__":
    main()
