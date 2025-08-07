import os
import subprocess
from tkinter import Tk, filedialog

from ..util import router, wrap_response


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


# 根据文件列表生成ffmpeg合并文件filelist.txt，并调用ffmpeg进行合并（需检查ffmpeg是否安装）
@router.post("/create-filelist-merge")
def create_filelist_merge(file_paths: list):
    """创建ffmpeg合并文件filelist.txt"""
    if not file_paths:
        return wrap_response(message="文件列表不能为空", status=2)
    filelist_path = "filelist.txt"
    with open(filelist_path, "w") as f:
        for path in file_paths:
            f.write(f"file '{path}'\n")
    # 调用ffmpeg进行合并
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
