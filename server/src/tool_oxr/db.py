import sys
from pathlib import Path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base


def get_db_path():
    # Nuitka打包后，sys.argv[0]为exe路径；开发时为main.py路径
    exe_dir = Path(sys.argv[0]).parent.resolve()
    return exe_dir / "data.db"


DATABASE_URL = f"sqlite+aiosqlite:///{get_db_path()}"

# 创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=True, future=True)

# 创建异步Session
AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

# 声明模型基类
Base = declarative_base()


async def init_db():
    """初始化数据库"""
    async with engine.begin() as conn:
        # 创建所有表
        await conn.run_sync(Base.metadata.create_all)
    print(f"数据库初始化完成，路径：{get_db_path()}")


# 获取Session的依赖（FastAPI用）
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
