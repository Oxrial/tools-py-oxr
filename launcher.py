# launcher.py
import sys
import os
from pathlib import Path

# 添加模块路径
current_dir = Path(__file__).parent
server_src_dir = current_dir / "server" / "src"
if server_src_dir.exists():
    sys.path.insert(0, str(server_src_dir))

# 设置环境变量标识打包环境
os.environ["FROZEN"] = "True"

from tool_oxr.main import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())
