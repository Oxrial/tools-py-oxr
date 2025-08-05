from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter

# 应用版本
APP_VERSION = "1.0.0"

# 创建 API 路由
router = APIRouter()
executor = ThreadPoolExecutor(max_workers=1)


# 包装接口返回
def wrap_response(data=None, message="success", status=1):
    return {"status": status, "message": message, "data": data}
