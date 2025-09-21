import os
import sys
from pathlib import Path

PORTS = {"SERVER": 39000, "APP": 39001, "DESKTOP": 39002, "API": 39003, "RELOAD": 39004}


# 包装接口返回
def wrap_response(data=None, message="success", status=1):
    return {"status": status, "message": message, "data": data}


def get_resource_path(relative_path: str) -> Path:
    """获取资源文件的绝对路径，适用于打包后的环境"""
    path = Path(__file__).parent

    files = []
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        files.append(full_path.replace("\\", "/"))
    print(str(files))
    print(str(sys.path))
    print(str(os.path.abspath(".")))
    if getattr(sys, "frozen", False):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
