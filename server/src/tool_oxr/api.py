from fastapi import APIRouter, Request

# 应用版本
APP_VERSION = "1.0.0"

# 创建 API 路由
router = APIRouter()


# 示例API端点
@router.get("/health")
async def health_check():
    """服务健康检查"""
    return {"status": "healthy", "version": APP_VERSION}


@router.get("/system-info")
async def get_system_info():
    """获取系统信息"""
    import platform
    import psutil

    return {
        "os": platform.system(),
        "os_version": platform.release(),
        "architecture": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "memory_total": psutil.virtual_memory().total,
        "memory_available": psutil.virtual_memory().available,
        "cpu_count": psutil.cpu_count(logical=False),
        "cpu_logical_count": psutil.cpu_count(logical=True),
    }


@router.post("/data")
async def save_data(request: Request):
    """保存数据到内存（实际应用中应使用数据库）"""
    data = await request.json()
    print(f"保存数据: {data}")
    return {"status": "success", "data": data}
