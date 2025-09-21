import codecs
import os
import re
import subprocess
from tkinter import Tk, filedialog
from typing import List

from fastapi import APIRouter, BackgroundTasks, Depends
from pydantic import BaseModel
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from tool_oxr.api.models import FfmpegCanmand, FfmpegCanmandDto
from tool_oxr.db import get_db
from util import wrap_response

# 创建 API 路由
router = APIRouter()


@router.get("/select-files")
async def select_files():
    """选择文件，多选"""
    root = Tk()
    root.withdraw()
    root.lift()  # 提升窗口层级
    root.attributes("-topmost", True)  # 置顶
    file_paths = filedialog.askopenfilenames(title="选择文件")
    root.destroy()
    if not file_paths:
        return wrap_response(message="未选择文件", status=2)
    return wrap_response(data={"file_paths": file_paths})


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
    cmd: str


# 根据文件列表生成ffmpeg合并文件filelist.txt，并调用ffmpeg进行合并（需检查ffmpeg是否安装）
@router.post("/create-filelist-merge")
async def create_filelist_merge(req: MergeFilesDto, background_tasks: BackgroundTasks):
    """创建ffmpeg合并文件filelist.txt，并后台执行合并任务"""
    if not req.files:
        return wrap_response(message="文件列表不能为空", status=2)
    if re.match(r".+\..+", req.fileName) is None:
        return wrap_response(message="文件名称异常", status=2)
    filelist_path = os.path.join(req.folderPath, "filelist.txt").replace("\\", "/")
    output_path = os.path.join(req.folderPath, req.fileName).replace("\\", "/")
    # 添加后台任务执行合并
    background_tasks.add_task(merge_files_task, req, filelist_path, output_path)
    return wrap_response(message="合并任务已提交，待执行完成后通知结果")


def merge_files_task(req: MergeFilesDto, filelist_path: str, output_path: str):
    """后台任务：生成 filelist 文件并执行 ffmpeg 合并命令"""

    try:
        # 生成 filelist 文件，确保路径格式为正斜杠
        with codecs.open(filelist_path, "w", encoding="utf-8") as f:
            for path in req.files:
                adjusted_path = path.replace("\\", "/")
                f.write(f"file '{adjusted_path}'\n")
        # 替换模板中的占位符
        command = req.cmd.replace("FILE_LIST_TEXT", filelist_path).replace(
            "OUT_PUT", output_path
        )
        print(f"准备合并，指令：{command}，输出文件：{output_path}")
        # 包装命令，使其在新的cmd窗口中运行，并在执行完成后关闭
        final_command = f'start cmd /c "{command}"'
        subprocess_result = subprocess.Popen(
            final_command,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
            text=True,
            encoding="utf-8",
        )
        print(f"合并完成: {subprocess_result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"合并失败: {e}, stderr: {e.stderr}")


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
        print(f"获取ffmpeg命令失败: {e}")
        return wrap_response(message=f"获取ffmpeg命令失败: {str(e)}", status=2)
