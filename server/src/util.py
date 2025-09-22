import os
import sys
from pathlib import Path

PORTS = {"SERVER": 39000, "APP": 39001, "DESKTOP": 39002, "API": 39003, "RELOAD": 39004}


# 包装接口返回
def wrap_response(data=None, message="success", status=1):
    return {"status": status, "message": message, "data": data}


def get_resource_path(relative_path: str = None) -> Path:
    path = (
        os.path.abspath(".")
        if sys.executable.endswith("python.exe")
        else Path(__file__).parent
    )
    return path if relative_path is None else Path(os.path.join(path, relative_path))
