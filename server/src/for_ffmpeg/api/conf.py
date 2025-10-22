from fastapi import APIRouter, Depends
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from for_ffmpeg.api.models import ConfParam, ConfParamDto
from for_ffmpeg.db import get_db, wrap_response

# 创建 API 路由
router = APIRouter()


async def select_conf_param(key: str, session: AsyncSession = Depends(get_db)):
    """选择配置参数"""
    result = await session.execute(select(ConfParam).where(ConfParam.pkey == key))
    param = result.scalars().first()
    return param.pvalue if param else None


@router.post("/save-conf-param")
async def save_conf_param(
    conf: List[ConfParamDto], session: AsyncSession = Depends(get_db)
) -> dict:
    """
    插入或更新配置参数
    """
    try:
        # 清空表
        await session.execute(delete(ConfParam))
        # 插入新数据
        orm_commands = [ConfParam(**cmd.model_dump()) for cmd in conf]
        session.add_all(orm_commands)
        await session.commit()
        await session.commit()
        return wrap_response(message="配置参数已保存")
    except Exception as e:
        await session.rollback()
        return wrap_response(message=f"配置参数保存失败: {str(e)}", status=2)


@router.get("/get-conf-param")
async def get_conf_param(session: AsyncSession = Depends(get_db)) -> dict:
    try:
        result = await session.execute(select(ConfParam))
        commands = result.scalars().all()
        command_list = [
            {
                "pkey": cmd.pkey,
                "pvalue": cmd.pvalue,
            }
            for cmd in commands
        ]
        return wrap_response(data=command_list)
    except Exception as e:
        print(f"获取配置参数失败: {e}")
        return wrap_response(message=f"获取配置参数失败: {str(e)}", status=2)
