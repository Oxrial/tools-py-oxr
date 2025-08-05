from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from ..db import get_db
from ..models import ConfParam
from .index import router, wrap_response


async def select_conf_param(key: str, session: AsyncSession = Depends(get_db)):
    """选择配置参数"""
    result = await session.execute(select(ConfParam).where(ConfParam.pkey == key))
    param = result.scalars().first()
    return param.pvalue if param else None


async def insert_conf_param(
    key: str, value: str, session: AsyncSession = Depends(get_db)
):
    """插入或更新配置参数"""
    param = await session.execute(select(ConfParam).where(ConfParam.pkey == key))
    param = param.scalars().first()
    if param:
        param.pvalue = value
    else:
        new_param = ConfParam(pkey=key, pvalue=value)
        session.add(new_param)
    await session.commit()

    return wrap_response(message="配置参数已保存")
