import logging
import os
import subprocess
from tkinter import Tk, filedialog
from typing import List

from fastapi import Depends, Response
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import get_db
from ..util import router, wrap_response
from .models import FfmpegCanmand, FfmpegCanmandDto

log = logging.getLogger(__name__)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
consoleHeader = logging.StreamHandler()
consoleHeader.setFormatter(formatter)
log.addHandler(consoleHeader)


@router.get("/select-folder")
async def select_folder():
    """选择文件夹"""
    root = Tk()
    root.withdraw()
    root.lift()  # 提升窗口层级
    root.attributes("-topmost", True)  # 置顶
    folder_path = filedialog.askdirectory(title="选择文件夹")
    root.destroy()
    if not folder_path:
        return wrap_response(message="未选择文件夹", status=2)
    return wrap_response(data={"folder_path": folder_path})


@router.get("/scan-files-for-walk")
async def scan_files(path):
    """扫描文件夹中的文件（递归）"""
    if not os.path.isdir(path):
        return wrap_response(message="路径不存在或不是文件夹", status=2)
    files = []
    for root, _, filenames in os.walk(path):
        for filename in filenames:
            files.append(os.path.join(root, filename))
    return wrap_response(data={"files": files})


@router.get("/scan-files")
async def scan_files(path):
    """扫描当前文件夹中的文件（不递归）"""
    if not os.path.isdir(path):
        return wrap_response(message="路径不存在或不是文件夹", status=2)
    files = []
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            files.append(full_path.replace("\\", "/"))
    return wrap_response(data={"files": files})


class MergeFilesDto(BaseModel):
    files: List[str]
    folderPath: str
    fileName: str


# 根据文件列表生成ffmpeg合并文件filelist.txt，并调用ffmpeg进行合并（需检查ffmpeg是否安装）
@router.post("/create-filelist-merge")
async def create_filelist_merge(
    req: MergeFilesDto,
    session: AsyncSession = Depends(get_db),
):
    print(req)
    """创建ffmpeg合并文件filelist.txt"""
    if not req.files:
        return wrap_response(message="文件列表不能为空", status=2)
    filelist_path = "filelist.txt"
    # with open(filelist_path, "w") as f:
    #     for path in file_paths:
    #         f.write(f"file '{path}'\n")
    # 调用ffmpeg进行合并
    try:
        result = await session.execute(
            select(FfmpegCanmand).where(FfmpegCanmand.name == "UN_TXT")
        )
        cmd = result.scalar_one()
        command = cmd.command.replace("filelist_path", filelist_path).replace(
            "output", req.fileName
        )
        print(command)
        # subprocess.run(
        #     [
        #         "ffmpeg",
        #         "-f",
        #         "concat",
        #         "-safe",
        #         "0",
        #         "-i",
        #         filelist_path,
        #         "-c",
        #         "copy",
        #         "output.mp4",
        #     ],
        #     check=True,
        # )
        return wrap_response(message="合并成功")
    except subprocess.CalledProcessError as e:
        return wrap_response(message=f"合并失败: {str(e)}", status=2)


# 保存ffmpeg命令,整体保存，替换FfmpegCanmand表中数据
@router.post("/save-ffmpeg-commands")
async def save_ffmpeg_commands(
    commands: List[FfmpegCanmandDto], session: AsyncSession = Depends(get_db)
) -> dict:
    """保存ffmpeg命令"""
    try:
        # 清空表
        await session.execute(delete(FfmpegCanmand))
        # 插入新数据
        orm_commands = [FfmpegCanmand(**cmd.model_dump()) for cmd in commands]
        session.add_all(orm_commands)
        await session.commit()
        return wrap_response(message="ffmpeg命令已保存")
    except Exception as e:
        await session.rollback()
        return wrap_response(message=f"ffmpeg命令保存失败: {str(e)}", status=2)


# 获取ffmpeg命令,整体获取，返回FfmpegCanmand表中数据
@router.get("/get-ffmpeg-commands")
async def get_ffmpeg_commands(session: AsyncSession = Depends(get_db)) -> dict:
    """获取ffmpeg命令"""
    try:
        result = await session.execute(select(FfmpegCanmand))
        commands = result.scalars().all()
        command_list = [
            {
                "name": cmd.name,
                "command": cmd.command,
                "description": cmd.description,
            }
            for cmd in commands
        ]
        return wrap_response(data=command_list)
    except Exception as e:
        log.error(f"获取ffmpeg命令失败: {e}")
        return wrap_response(message=f"获取ffmpeg命令失败: {str(e)}", status=2)
