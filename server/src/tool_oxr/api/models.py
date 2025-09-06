from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from ..db import Base


class ConfParam(Base):
    __tablename__ = "conf_param"
    pkey = Column(Integer, primary_key=True, index=True)
    pvalue = Column(String)


class ConfParamDto(BaseModel):
    pkey: int
    pvalue: str


class FfmpegCanmand(Base):
    __tablename__ = "ffmpeg_command"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    command = Column(String, nullable=False)
    description = Column(String, nullable=True)


class FfmpegCanmandDto(BaseModel):
    id: str
    name: str
    command: str
    description: str
