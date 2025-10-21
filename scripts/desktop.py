#!/usr/bin/env python3
"""
桌面应用打包脚本
使用 Nuitka 将 FastAPI + Vue 应用打包为跨平台桌面应用
支持 Windows (.exe), macOS (.app), Linux (.bin)
"""

import argparse
import os
import platform
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

BASE_DIR1 = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR1))

from environment import (
    BACKEND_DIR,
    BASE_DIR,
    FRONTEND_DIR,
    get_pnpm_path,
    get_uv_python,
)


# 基础配置
class Config:
    # 应用元数据
    APP_NAME = "Tool-oxr"
    APP_VERSION = "1.0.0"
    AUTHOR = "Oxrial"
    COMPANY = "Lin"

    # 目录结构
    DIST_DIR = BASE_DIR / "dist"  # 前端构建输出
    ASSETS_DIR = BASE_DIR / "assets"  # 图标等资源
    OUTPUT_DIR = BASE_DIR / "dist-desktop"  # 最终输出目录
    OUTPUT_MAIN = f"{APP_NAME.lower()}{APP_VERSION}.exe"
    FFMPEG_DIR = BACKEND_DIR / "src" / "for_ffmpeg"
    DB_DIR = BASE_DIR / "data.db"

    # 入口文件
    ENTRY_POINT = BASE_DIR / "launcher.py"

    # 平台特定配置
    ICONS = {
        "Windows": ASSETS_DIR / "oxr.ico",
        "Darwin": ASSETS_DIR / "app_icon.icns",
        "Linux": ASSETS_DIR / "oxr-192x192.png",
    }

    # 平台名称映射
    PLATFORM_NAMES = {"Windows": "windows", "Darwin": "macos", "Linux": "linux"}


def validate_environment():
    """验证打包环境是否就绪"""
    print("🔍 验证打包环境...")

    # 检查 Python 版本
    if sys.version_info < (3, 11):
        print("需要 Python 3.11 或更高版本")
        return False

    # 检查 Nuitka 是否安装
    try:
        from nuitka.Version import getNuitkaVersion

        print(f"Nuitka 版本: { getNuitkaVersion()}")
    except ImportError:
        print("Nuitka 未安装，请运行: pip install nuitka")
        return False

    # 检查前端构建是否存在
    if not Config.DIST_DIR.exists():
        print("前端构建不存在，尝试构建前端...")
        try:
            subprocess.run(
                ["pnpm", "run", "build"],
                cwd=Config.FRONTEND_DIR,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            print("前端构建成功")
        except subprocess.CalledProcessError as e:
            print(f"前端构建失败: {str(e)}")
            if e.stderr:
                print(e.stderr.decode().strip())
            return False

    # 检查入口文件
    if not Config.ENTRY_POINT.exists():
        print(f"入口文件不存在: {Config.ENTRY_POINT}")
        return False

    # 检查平台图标
    current_os = platform.system()
    if not Config.ICONS.get(current_os).exists():
        print(f"{current_os} 平台图标不存在: {Config.ICONS[current_os]}")

    print("环境验证通过")
    return True


def build_nuitka_command(target_os=None):
    """构建 Nuitka 打包命令"""
    target_os = target_os or platform.system()
    platform_name = Config.PLATFORM_NAMES.get(target_os, target_os.lower())
    output_dir = Config.OUTPUT_DIR / platform_name

    # 确保输出目录存在
    output_dir.mkdir(parents=True, exist_ok=True)

    # 获取 Python 解释器
    python_exe = get_uv_python()

    # 基础命令
    command = [
        str(python_exe),
        "-m",
        "nuitka",
        "--standalone",
        "--onefile",
        f"--output-dir={output_dir}",
        f"--output-filename={Config.OUTPUT_MAIN}",
        f"--include-data-dir={Config.DIST_DIR}=dist",
        f"--include-data-dir={Config.ASSETS_DIR}=assets",
        f"--include-data-file={Config.DB_DIR}=data.db",  # 新增的data.db配置
    ]
    command.extend(
        [
            "--enable-plugin=tk-inter",  # 启用 Tkinter 插件
            "--enable-plugin=upx",  # 启用 UPX
            "--assume-yes-for-downloads",  # 自动确认下载
            "--lto=yes",
            "--remove-output",  # 清理临时文件
            # "--show-modules",
            # "--report=compilation-report.xml",
            # "--report=imported-modules.txt",
        ]
    )

    # 平台特定配置
    if target_os == "Windows":
        command.extend(
            [
                f"--windows-icon-from-ico={Config.ICONS['Windows']}",
                f"--windows-product-name={Config.APP_NAME}",
                f"--windows-company-name={Config.COMPANY}",
                f"--windows-file-version={Config.APP_VERSION}",
                f"--windows-console-mode=disable",
            ]
        )
    # elif target_os == "Darwin":
    #     command.extend(
    #         [
    #             f"--macos-app-icon={Config.ICONS['Darwin']}",
    #             "--macos-create-app-bundle",
    #             f"--macos-app-name={Config.APP_NAME}",
    #             f"--macos-app-version={Config.APP_VERSION}",
    #             "--macos-signed-app-name=My Signed App",
    #             "--macos-app-protected-resource=all",
    #         ]
    #     )
    # elif target_os == "Linux":
    #     command.extend(
    #         [
    #             f"--linux-icon={Config.ICONS['Linux']}",
    #             f"--linux-onefile-icon={Config.ICONS['Linux']}",
    #             "--linux-disable-console",
    #         ]
    #     )
    # 排除不必要的模块
    nofollow_import = [
        "*.test",
        "*.tests",
        "unittest",
        "setuptools",
        "pip",
        "pkg_resources",
        "doctest",
        "matplotlib",
        "scipy",
        "notebook",
        "pytest",
        "ipython",
        "jupyter",
        "tkinter.tix",
        "tkinter.test",
        "sqlalchemy.dialects.mysql",
        "sqlalchemy.dialects.postgresql",
        "sqlalchemy.dialects.oracle",
        "sqlalchemy.dialects.mssql",
        "webview.platforms.android",
        "webview.platforms.cocoa",
        "webview.platforms.gtk",
        "webview.platforms.qt",
    ]

    for module in nofollow_import:
        command.append(f"--nofollow-import-to={module}")
    # 包含 PyWebView 的 JS 文件
    # 包含必要的 Python 包
    include_packages = [
        "fastapi",
        # "pydantic",
    ]
    for pkg in include_packages:
        command.append(f"--include-package={pkg}")
    command.append(f"--noinclude-default-mode=error")
    # 添加入口点
    command.append(str(Config.ENTRY_POINT))

    return command, output_dir


def package_for_platform(target_os=None):
    """为特定平台打包应用"""
    target_os = target_os or platform.system()
    platform_name = Config.PLATFORM_NAMES.get(target_os, target_os.lower())

    print(f"开始打包 {platform_name} 平台应用...")

    # 构建命令
    command, output_dir = build_nuitka_command(target_os)

    # 显示完整命令（用于调试）
    print("Nuitka 命令: " + " ".join(command))
    print(f"输出目录: {output_dir}")
    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmp_dir:
        env = os.environ.copy()
        env["NUITKA_TEMP_DIR"] = tmp_dir

        try:
            final_command = f'start cmd /c "{" ".join(command)}"'
            # 执行打包命令
            subprocess.run(
                final_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
                text=True,
                env=env,
            )
            print(f"{platform_name} 平台打包结束，输出目录: {output_dir}")

            return True
        except subprocess.CalledProcessError as e:
            print(f"{platform_name} 平台打包失败，退出码: {e.returncode}")
            if e.stderr:
                print("错误信息:\n" + e.stderr.strip())
            if e.stdout:
                print("输出信息:\n" + e.stdout.strip())
            return False


def cleanup_output():
    """清理输出目录"""
    if Config.OUTPUT_DIR.exists():
        print("清理旧输出目录...")
        shutil.rmtree(Config.OUTPUT_DIR)
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def package_all_platforms():
    """为所有支持的平台打包"""
    platforms = ["Windows"]  # , "Darwin", "Linux"
    success = True

    for target_os in platforms:
        # 跳过当前不支持打包的平台
        # if target_os == "Darwin" and platform.system() != "Darwin":
        #     print("macOS 应用只能在 macOS 系统上打包，跳过...")
        #     continue

        # if target_os == "Linux" and platform.system() not in ["Linux", "Darwin"]:
        #     print("Linux 应用建议在 Linux 系统上打包，跳过...")
        #     continue

        if not package_for_platform(target_os):
            success = False

    return success


def build_prod():
    # 构建前端
    print("构建前端生产包...")
    subprocess.run(
        [get_pnpm_path(), "run", "build"],
        cwd=FRONTEND_DIR,
        stdout=sys.stdout,  # 直接输出到控制台
        stderr=sys.stderr,
        check=True,
    )


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="桌面应用打包工具")
    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux", "all"],
        default="all",
        help="目标平台 (默认: 所有平台)",
    )
    args = parser.parse_args()

    # # 设置调试模式
    # if args.debug:
    #     print("调试模式已启用")

    # 验证环境
    if not validate_environment():
        sys.exit(1)

    # 清理输出目录
    cleanup_output()

    # 确保生产构建已完成
    if not Path("dist").exists():
        print("前端生产构建不存在，自动构建中...")
        build_prod()
    # 执行打包
    success = False

    if args.platform == "all":
        success = package_all_platforms()
    else:
        # 映射平台名称
        platform_map = {"windows": "Windows", "macos": "Darwin", "linux": "Linux"}
        target_os = platform_map[args.platform]
        success = package_for_platform(target_os)
    print(f"打包完成${str(success)}")


if __name__ == "__main__":
    main()
