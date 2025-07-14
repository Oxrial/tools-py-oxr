import os
import sys

# 使用 sys.argv[0] 获取当前脚本路径
spec_path = os.path.abspath(sys.argv[0])
project_root = os.path.dirname(os.path.dirname(spec_path))

# 定义数据文件
datas = [
    (os.path.join(project_root, 'dist'), 'dist'),
    (os.path.join(project_root, 'server', 'api.py'), '.')
]

# 添加隐藏导入（解决 Flask 等动态导入问题）
hiddenimports = [
    'flask',
    'flask.cli',
    'werkzeug.wrappers',
    'pywebview'
]

a = Analysis(
    [os.path.join(project_root, 'server/main.py')],
    pathex=[project_root],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Tools-OXR',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,  # 启用 UPX 压缩
    console=False  # 不显示控制台窗口
)