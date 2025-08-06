from concurrent.futures import ThreadPoolExecutor

from fastapi import APIRouter

PORTS = {"SERVER": 9000, "APP": 9001, "DESKTOP": 9002, "API": 9003, "RELOAD": 9004}
# 创建 API 路由
router = APIRouter()
executor = ThreadPoolExecutor(max_workers=1)


# 包装接口返回
def wrap_response(data=None, message="success", status=1):
    return {"status": status, "message": message, "data": data}
