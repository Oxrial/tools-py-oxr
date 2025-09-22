from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from tool_oxr.db import Base


class ConfParam(Base):
    __tablename__ = "conf_param"
    pkey = Column(Integer, primary_key=True, index=True)
    pvalue = Column(String)


class ConfParamDto(BaseModel):
    pkey: int
    pvalue: str


class FfmpegCanmand(Base):
    __tablename__ = "ffmpeg_command"
    name = Column(String, primary_key=True, nullable=True)
    command = Column(String, nullable=True)
    description = Column(String, nullable=False)


class FfmpegCanmandDto(BaseModel):
    name: str
    command: str
    # 可选
    description: str | None = None
