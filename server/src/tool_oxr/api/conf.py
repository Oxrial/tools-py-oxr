from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tool_oxr.db import get_db
from tool_oxr.util import wrap_response
from tool_oxr.api.models import ConfParam, ConfParamDto

from fastapi import APIRouter

# 创建 API 路由
router = APIRouter()


async def select_conf_param(key: str, session: AsyncSession = Depends(get_db)):
    """选择配置参数"""
    result = await session.execute(select(ConfParam).where(ConfParam.pkey == key))
    param = result.scalars().first()
    return param.pvalue if param else None


@router.post("/insert-conf-param")
async def insert_conf_param(
    conf: ConfParamDto, session: AsyncSession = Depends(get_db)
) -> dict:
    """
    插入或更新配置参数
    """
    try:
        result = await session.execute(
            select(ConfParam).where(ConfParam.pkey == conf.pkey)
        )
        param = result.scalars().first()
        if param:
            param.pvalue = conf.pvalue
        else:
            param = ConfParam(pkey=conf.pkey, pvalue=conf.pvalue)
            session.add(param)
        await session.commit()
        if not param:
            await session.refresh(param)
        return wrap_response(message="配置参数已保存")
    except Exception as e:
        await session.rollback()
        return wrap_response(message=f"配置参数保存失败: {str(e)}", status=2)
