from .db import Base
from sqlalchemy import Column, Integer, String


class ConfParam(Base):
    __tablename__ = "conf_param"
    pkey = Column(Integer, primary_key=True, index=True)
    pvalue = Column(String)


class FfmpegCanmand(Base):
    __tablename__ = "ffmpeg_command"
    id = Column(String, primary_key=True, index=True)
    command = Column(String, nullable=False)
    description = Column(String, nullable=True)
