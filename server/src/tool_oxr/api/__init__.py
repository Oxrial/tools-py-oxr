from .conf import router as conf_router
from .ffmpeg import router as ffmpeg_router

routers = [conf_router, ffmpeg_router]
