import os
import sys
from pathlib import Path

PORTS = {"SERVER": 39000, "APP": 39001, "DESKTOP": 39002, "API": 39003, "RELOAD": 39004}


# 包装接口返回
def wrap_response(data=None, message="success", status=1):
    return {"status": status, "message": message, "data": data}


def get_resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)
