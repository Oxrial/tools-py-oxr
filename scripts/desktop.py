#!/usr/bin/env python3
"""
桌面应用打包脚本
使用 Nuitka 将 FastAPI + Vue 应用打包为跨平台桌面应用
支持 Windows (.exe), macOS (.app), Linux (.bin)
"""

import os
import sys
import shutil
import subprocess
import platform
import argparse
import tempfile
from util import (
    get_uv_python,
    BASE_DIR,
    BACKEND_DIR,
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

    # 入口文件
    ENTRY_POINT = BACKEND_DIR / "src" / "tool_oxr" / "main.py"

    # 平台特定配置
    ICONS = {
        "Windows": ASSETS_DIR / "app_icon.ico",
        "Darwin": ASSETS_DIR / "app_icon.icns",
        "Linux": ASSETS_DIR / "app_icon.png",
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
        import nuitka

        print(f"Nuitka 版本: {nuitka.__version__}")
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
        f"--include-data-dir={Config.DIST_DIR}=dist",
        f"--include-data-dir={Config.ASSETS_DIR}=assets",
        "--enable-plugin=pywebview",
        "--remove-output",  # 清理临时文件
        "--assume-yes-for-downloads",  # 自动确认下载
    ]

    # 包含必要的 Python 包
    include_packages = [
        "fastapi",
        "uvicorn",
        "jinja2",
        "pydantic",
        "pywebview",
        "websockets",
        "psutil",
    ]

    for pkg in include_packages:
        command.append(f"--include-package={pkg}")

    # 平台特定配置
    if target_os == "Windows":
        command.extend(
            [
                f"--windows-icon={Config.ICONS['Windows']}",
                "--windows-disable-console",
                f"--windows-product-name={Config.APP_NAME}",
                f"--windows-company-name={Config.COMPANY}",
                f"--windows-file-version={Config.APP_VERSION}",
            ]
        )
    elif target_os == "Darwin":
        command.extend(
            [
                f"--macos-app-icon={Config.ICONS['Darwin']}",
                "--macos-create-app-bundle",
                f"--macos-app-name={Config.APP_NAME}",
                f"--macos-app-version={Config.APP_VERSION}",
                "--macos-signed-app-name=My Signed App",
                "--macos-app-protected-resource=all",
            ]
        )
    elif target_os == "Linux":
        command.extend(
            [
                f"--linux-icon={Config.ICONS['Linux']}",
                f"--linux-onefile-icon={Config.ICONS['Linux']}",
                "--linux-disable-console",
            ]
        )

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

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmp_dir:
        env = os.environ.copy()
        env["NUITKA_TEMP_DIR"] = tmp_dir

        try:
            # 执行打包命令
            result = subprocess.run(
                command,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env,
            )

            # 记录输出
            if result.stdout:
                print("Nuitka 输出:\n" + result.stdout)

            print(f"{platform_name} 平台打包成功")
            print(f"输出目录: {output_dir}")

            # 在 Windows 上添加版本信息文件
            if target_os == "Windows":
                create_version_file(output_dir)

            return True
        except subprocess.CalledProcessError as e:
            print(f"{platform_name} 平台打包失败，退出码: {e.returncode}")
            if e.stderr:
                print("错误信息:\n" + e.stderr.strip())
            if e.stdout:
                print("输出信息:\n" + e.stdout.strip())
            return False


def create_version_file(output_dir):
    """创建 Windows 版本信息文件（增强元数据）"""
    version_file = output_dir / "version_info.txt"
    content = f"""\
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers={tuple(map(int, Config.APP_VERSION.split('.')))},
    prodvers={tuple(map(int, Config.APP_VERSION.split('.')))},
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [
            StringStruct(u'CompanyName', u"{Config.COMPANY}"),
            StringStruct(u'FileDescription', u"{Config.APP_NAME}"),
            StringStruct(u'FileVersion', u"{Config.APP_VERSION}"),
            StringStruct(u'InternalName', u"{Config.APP_NAME}"),
            StringStruct(u'LegalCopyright', u"Copyright © {Config.COMPANY}"),
            StringStruct(u'OriginalFilename', u"{Config.APP_NAME}.exe"),
            StringStruct(u'ProductName', u"{Config.APP_NAME}"),
            StringStruct(u'ProductVersion', u"{Config.APP_VERSION}")
          ])
      ]),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])]
  ]
)
"""
    with open(version_file, "w") as f:
        f.write(content)
    print(f"已创建版本信息文件: {version_file}")


def cleanup_output():
    """清理输出目录"""
    if Config.OUTPUT_DIR.exists():
        print("清理旧输出目录...")
        shutil.rmtree(Config.OUTPUT_DIR)
    Config.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def package_all_platforms():
    """为所有支持的平台打包"""
    platforms = ["Windows", "Darwin", "Linux"]
    success = True

    for target_os in platforms:
        # 跳过当前不支持打包的平台
        if target_os == "Darwin" and platform.system() != "Darwin":
            print("macOS 应用只能在 macOS 系统上打包，跳过...")
            continue

        if target_os == "Linux" and platform.system() not in ["Linux", "Darwin"]:
            print("Linux 应用建议在 Linux 系统上打包，跳过...")
            continue

        if not package_for_platform(target_os):
            success = False

    return success


def create_launcher_scripts():
    """创建启动脚本（用于测试）"""
    print("创建测试启动脚本...")

    # Windows 启动脚本
    if platform.system() == "Windows":
        bat_content = f"""\
@echo off
echo 启动 {Config.APP_NAME}...
dist-desktop\\windows\\desktop.exe
pause
"""
        bat_path = Config.BASE_DIR / "launch.bat"
        with open(bat_path, "w") as f:
            f.write(bat_content)
        print(f"创建 Windows 启动脚本: {bat_path}")

    # Linux/macOS 启动脚本
    else:
        sh_content = f"""\
#!/bin/bash
echo "启动 {Config.APP_NAME}..."
dist-desktop/linux/desktop
"""
        sh_path = Config.BASE_DIR / "launch.sh"
        with open(sh_path, "w") as f:
            f.write(sh_content)
        sh_path.chmod(0o755)  # 添加可执行权限
        print(f"创建 Unix 启动脚本: {sh_path}")


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description="桌面应用打包工具")
    parser.add_argument(
        "--platform",
        choices=["windows", "macos", "linux", "all"],
        default="all",
        help="目标平台 (默认: 所有平台)",
    )
    parser.add_argument("--debug", action="store_true", help="启用调试模式")
    args = parser.parse_args()

    # 设置调试模式
    if args.debug:
        print("调试模式已启用")

    # 验证环境
    if not validate_environment():
        sys.exit(1)

    # 清理输出目录
    cleanup_output()

    # 执行打包
    success = True

    if args.platform == "all":
        success = package_all_platforms()
    else:
        # 映射平台名称
        platform_map = {"windows": "Windows", "macos": "Darwin", "linux": "Linux"}
        target_os = platform_map[args.platform]
        success = package_for_platform(target_os)

    # 创建启动脚本
    if success:
        create_launcher_scripts()
        print("=" * 50)
        print(f"{Config.APP_NAME} {Config.APP_VERSION} 打包完成!")
        print(f"输出目录: {Config.OUTPUT_DIR}")
        print("=" * 50)
    else:
        print("打包过程中出现错误，请检查日志")
        sys.exit(1)


if __name__ == "__main__":
    main()
