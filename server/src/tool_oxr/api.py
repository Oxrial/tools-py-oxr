import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter
from sqlalchemy import select
from .db import AsyncSessionLocal
from .models import ConfParam

# 应用版本
APP_VERSION = "1.0.0"

# 创建 API 路由
router = APIRouter()
executor = ThreadPoolExecutor(max_workers=1)


# 包装接口返回
def wrap_response(data=None, message="success", status=1):
    return {"status": status, "message": message, "data": data}


# 示例API端点
@router.get("/select-folder")
async def select_folder():
    """选择文件夹"""
    from tkinter import filedialog, Tk

    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="选择文件夹")
    root.destroy()
    if not folder_path:
        return wrap_response(message="未选择文件夹", status=2)
    return wrap_response(data={"folder_path": folder_path})


@router.get("/scan-files")
async def scan_files(path):
    """扫描文件夹中的文件"""
    import os

    if not os.path.isdir(path):
        return wrap_response(message="路径不存在或不是文件夹", status=2)
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return wrap_response(data={"files": files})


def select_conf_param(key: str, session: AsyncSession = Depends(get_db)):
    """选择配置参数"""

    async def _select():
        async with AsyncSessionLocal() as session:
            result = await session.execute(
                select(ConfParam).where(ConfParam.pkey == key)
            )
            param = result.scalars().first()
            return param.pvalue if param else None

    return asyncio.run(_select())


def insert_conf_param(key: str, value: str):
    """插入或更新配置参数"""

    async def _insert():
        async with AsyncSessionLocal() as session:
            param = await session.execute(
                select(ConfParam).where(ConfParam.pkey == key)
            )
            param = param.scalars().first()
            if param:
                param.pvalue = value
            else:
                new_param = ConfParam(pkey=key, pvalue=value)
                session.add(new_param)
            await session.commit()

    asyncio.run(_insert())
    return wrap_response(message="配置参数已保存")


# 根据文件列表生成ffmpeg合并文件filelist.txt，并调用ffmpeg进行合并（需检查ffmpeg是否安装）
@router.post("/create-filelist-merge")
def create_filelist_merge(file_paths: list):
    """创建ffmpeg合并文件filelist.txt"""
    import os

    if not file_paths:
        return wrap_response(message="文件列表不能为空", status=2)

    filelist_path = "filelist.txt"
    with open(filelist_path, "w") as f:
        for path in file_paths:
            f.write(f"file '{path}'\n")

    # 调用ffmpeg进行合并
    import subprocess

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                filelist_path,
                "-c",
                "copy",
                "output.mp4",
            ],
            check=True,
        )
        return wrap_response(message="合并成功")
    except subprocess.CalledProcessError as e:
        return wrap_response(message=f"合并失败: {str(e)}", status=2)
