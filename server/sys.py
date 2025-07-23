import sys
from flask import Blueprint

sys_bp = Blueprint("sys", __name__)


# ============= 示例API端点 =============
@sys_bp.route("/api/hello")
def hello_api():
    """示例API端点"""
    return {"message": f"Hello from {APP_NAME}!", "status": "success"}


@sys_bp.route("/api/system-info")
def system_info():
    """系统信息API"""
    return {
        "platform": sys.platform,
        "python_version": sys.version,
        "app_version": "1.0.0",
    }
