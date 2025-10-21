import os
import shutil
import socket
import subprocess
import sys
import threading
from pathlib import Path

# 基础路径
BASE_DIR = Path(__file__).parent

BACKEND_DIR = BASE_DIR / "server"
FRONTEND_DIR = BASE_DIR / "app"


def find_available_port(start_port, max_attempts=10):
    """查找可用的端口"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(("localhost", port))
                return port
        except OSError:
            continue
    return start_port  # 如果找不到可用端口，返回原始端口


APP_PORT = find_available_port(39000)
API_PORT = find_available_port(39001)
RELOAD_PORT = find_available_port(39002)
DESKTOP_PORT = find_available_port(39003)

PORTS = {
    "APP": APP_PORT,
    "API": API_PORT,
    "RELOAD": RELOAD_PORT,
    "DESKTOP": DESKTOP_PORT,
}


def get_resource_path(relative_path: str = None) -> Path:
    return (
        BASE_DIR
        if relative_path is None
        else Path(os.path.join(BASE_DIR, relative_path))
    )


def isProd():
    return not sys.executable.endswith("python.exe")


def get_my_documents():
    return os.path.expanduser("~\\Documents")


def get_db_path():
    # Nuitka打包后，sys.argv[0]为exe路径；开发时为main.py路径
    document_dir = Path(get_my_documents()) / "tool-oxr"
    print(f"Document directory: {document_dir}")
    # exe_dir = Path(sys.argv[0]).parent.resolve()
    # 如果不存在
    if not Path(document_dir / "data.db").exists():
        if not document_dir.exists():
            document_dir.mkdir(parents=True, exist_ok=True)
        if (get_resource_path("data.db")).exists():
            # 复制一份到exe目录
            with (
                open(get_resource_path("data.db"), "rb") as src,
                open(document_dir / "data.db", "wb") as dst,
            ):
                dst.write(src.read())
    return document_dir / "data.db"


# 获取 UV Python 路径
def get_uv_python():
    """获取虚拟环境中的 Python 解释器路径"""
    if sys.platform == "win32":
        return BACKEND_DIR / ".venv" / "Scripts" / "python.exe"
    else:
        return BACKEND_DIR / ".venv" / "bin" / "python"


def get_pnpm_path():
    """获取 pnpm 可执行文件的完整路径"""
    # 尝试在环境变量中查找 pnpm
    pnpm_path = shutil.which("pnpm")
    if pnpm_path:
        return pnpm_path

    # Windows 特定路径
    if sys.platform == "win32":
        # 检查 AppData 路径
        appdata = os.environ.get("APPDATA")
        if appdata:
            pnpm_path = Path(appdata) / "npm" / "pnpm.cmd"
            if pnpm_path.exists():
                return str(pnpm_path)

            # 检查 npm 安装目录
            npm_path = shutil.which("npm")
            if npm_path:
                npm_dir = Path(npm_path).parent
                pnpm_path = npm_dir / "pnpm.cmd"
                if pnpm_path.exists():
                    return str(pnpm_path)

    # 其他平台
    if sys.platform in ["darwin", "linux"]:
        # 检查常见安装路径
        possible_paths = [
            "/usr/local/bin/pnpm",
            "/usr/bin/pnpm",
            Path.home() / ".npm-global" / "bin" / "pnpm",
            Path.home() / ".nvm" / "versions" / "node" / "*" / "bin" / "pnpm",
            Path.home() / ".yarn" / "bin" / "pnpm",
        ]

        for path in possible_paths:
            if isinstance(path, Path) and path.exists():
                return str(path)
            # 处理通配符路径
            if "*" in str(path):
                import glob

                matches = glob.glob(str(path))
                if matches:
                    return matches[0]

    # 在项目目录中查找
    project_pnpm = FRONTEND_DIR / "node_modules" / ".bin" / "pnpm"
    if project_pnpm.exists():
        return str(project_pnpm)
    return None


class ProcessWrapper:
    def __init__(self, proc, name):
        self.proc = proc
        self.name = name
        self.output_thread = None
        self.exit_code = None


def run_command(cmd, cwd=None, name: str = "Process", realtime_output: bool = True):
    """
    运行命令并返回进程包装器

    :param cmd: 命令列表
    :param cwd: 工作目录
    :param name: 进程名称（用于日志）
    :param realtime_output: 是否实时输出
    :return: ProcessWrapper 对象
    """
    cwd = str(cwd) if cwd is not None and isinstance(cwd, Path) else cwd

    print(f"[{name}] 执行命令: {' '.join(cmd)}")
    if cwd:
        print(f"[{name}] 工作目录: {cwd}")

    try:
        # 创建进程
        stdout = subprocess.PIPE if realtime_output else None
        stderr = subprocess.STDOUT if realtime_output else None
        # 强制使用UTF-8编码
        encoding = "utf-8"
        # 在Windows上使用CREATE_NEW_PROCESS_GROUP
        creationflags = 0
        if sys.platform == "win32":
            creationflags = subprocess.CREATE_NEW_PROCESS_GROUP

        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=stdout,
            stderr=stderr,
            universal_newlines=True,
            text=True,
            bufsize=1,
            creationflags=creationflags,
            encoding=encoding,  # 使用系统编码
        )

        # 创建包装器
        wrapper = ProcessWrapper(proc, name)

        # 如果需要实时输出，启动输出线程
        if realtime_output and stdout is not None:

            def output_reader():
                try:
                    while True:
                        try:
                            line = proc.stdout.readline()
                        except UnicodeDecodeError:
                            # 遇到解码错误时读取原始字节
                            raw_line = proc.stdout.buffer.readline()
                            try:
                                line = raw_line.decode("utf-8", errors="replace")
                            except:
                                line = str(raw_line)  # 最终回退方案

                        if not line and proc.poll() is not None:
                            break
                        if line:
                            line = line.rstrip("\n")
                            try:
                                print(f"[{name}] {line}")
                            except UnicodeEncodeError:
                                # 处理打印时的编码错误
                                safe_line = line.encode(
                                    sys.stdout.encoding, errors="replace"
                                ).decode(sys.stdout.encoding)
                                print(f"[{name}] {safe_line}")
                except Exception as e:
                    # 处理解码错误
                    print(f"[{name}] 读取输出时出错: {e}")
                finally:
                    wrapper.exit_code = proc.poll()

            wrapper.output_thread = threading.Thread(target=output_reader, daemon=True)
            wrapper.output_thread.start()

        return wrapper
    except Exception as e:
        print(f"[{name}] 执行命令出错: {e}")
        raise e.with_traceback(sys.exc_info()[2])  # 重新抛出异常以保留堆栈信息
