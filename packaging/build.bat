@echo off
setlocal enabledelayedexpansion
chcp 65001 > nul
cls
:: =============================================
:: Nuitka + PyWebView + Vue3 打包脚本
:: 版本: 1.2.0
:: 日期: 2024-07-15
:: =============================================

:: 设置项目根目录
set "PROJECT_ROOT=%~dp0.."
cd /d "%PROJECT_ROOT%"
echo [信息] 项目根目录: %PROJECT_ROOT%

:: 检查必要命令是否存在
where pnpm >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 pnpm 命令，请安装 Node.js
    exit /b 1
)

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 python 命令
    exit /b 1
)

:: 检查 Nuitka 是否安装
python -m nuitka --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] Nuitka 未安装，正在安装...
    pip install nuitka
)

:: 2. 检查 UPX
where upx >nul 2>&1
set UPX_OPT=--upx=no
if %errorlevel% == 0 set UPX_OPT=--upx=yes

:: 构建前端
echo [步骤1] 构建 Vue 前端...
cd app
echo [信息] %CD%
call pnpm i --frozen-lockfile --silent
if %errorlevel% neq 0 (
    echo [错误] pnpm 依赖安装失败
    exit /b 1
)

call pnpm run build
if %errorlevel% neq 0 (
    echo [错误] Vue 构建失败
    exit /b 1
)
cd ..
echo [成功] Vue 前端构建完成

:: 创建构建目录
if exist build (
    del /q build
)
    mkdir build
    echo [信息] 创建构建目录: build

:: 设置图标路径
set "ICON_PATH=packaging\app_icon.ico"
if not exist "%ICON_PATH%" (
    echo [警告] 应用图标不存在: %ICON_PATH%
    set "ICON_OPTION="
) else (
    set "ICON_OPTION=--windows-icon-from-ico=%ICON_PATH%"
)

:: 获取当前日期时间用于版本信息
for /f "tokens=2 delims==" %%a in ('wmic os get localdatetime /value') do set "datetime=%%a"
set "BUILD_DATE=!datetime:~0,4!-!datetime:~4,2!-!datetime:~6,2!"
set "BUILD_TIME=!datetime:~8,2!:!datetime:~10,2!:!datetime:~12,2!"

:: 打包 Python 应用
echo [步骤2] 使用 Nuitka 打包应用...
echo [信息] 开始时间: %time%
set "LOG_FILE=%PROJECT_ROOT%\build\nuitka_build.log"
if exist "%LOG_FILE%" del "%LOG_FILE%"
python -m nuitka  --standalone --windows-console-mode=disable %ICON_OPTION% --windows-product-name="Tools-oxr" --windows-company-name="OXR" --windows-file-version=1.0.0 --windows-product-version=1.0.0 --windows-file-description="PyWebView + Vue3 Desktop App" --include-data-dir=dist=dist   --include-data-dir=logs=logs --include-data-file=server\main.py=main.py --include-data-file=server\utils.py=utils.py --include-package=flask --include-package=flasgger  --include-package=waitress --include-package=ctypes --include-package=logging  --include-package=threading   --include-package=mistune   --include-module=mistune.plugins   --include-module=mistune.plugins.formatting   --include-module=mistune.directives   --include-module=mistune.renderers    --nofollow-import-to=tkinter   --nofollow-import-to=tkinter.*   --nofollow-import-to=ctypes.test   --nofollow-import-to=unittest   --nofollow-import-to=test   --nofollow-import-to=*test* --output-dir=build --remove-output --assume-yes-for-downloads   --plugin-enable=upx %USE_UPX% --lto=yes --jobs=4 --windows-force-stdout-spec=logs\stdout.log --windows-force-stderr-spec=logs\stderr.log server\main.py

if %errorlevel% neq 0 (
    echo [错误] Nuitka 打包失败
    exit /b 1
)

echo [成功] 应用打包完成
echo [信息] 结束时间: %time%

:: 复制额外文件
if exist "packaging\extra_files" (
    echo [信息] 复制额外文件...
    xcopy /E /Y "packaging\extra_files" "build\main.dist"
)

:: 创建版本信息文件
echo Build Date: %BUILD_DATE% %BUILD_TIME% > "build\main.dist\build_info.txt"
echo Nuitka Version: >> "build\main.dist\build_info.txt"
python -m nuitka --version >> "build\main.dist\build_info.txt"

:: 最终输出
echo =============================================
echo [成功] 打包流程完成!
echo 生成的应用位置: %PROJECT_ROOT%\build\main.dist
echo 主执行文件: main.exe
echo 大小信息: 
for %%F in ("build\main.dist\main.exe") do (
    set "size=%%~zF"
    set "size_mb=!size:~0,-6!.!size:~-6,-3! MB"
    echo   main.exe: !size_mb!
)
echo =============================================

endlocal