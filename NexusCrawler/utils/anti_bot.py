# utils/anti_bot.py
import random
from utils.ua_generator import UAGenerator # 使用你之前安装的逻辑
from config.config import settings
import asyncio

class AntiBotMiddleware:
    @classmethod
    def get_headers(cls, platform: str) -> dict:
        # 强制沿用你的 ua_generator.py，并锁定 PC 端以防被 B 站 Web 版拦截
        ua = UAGenerator.get_random(platform_type=settings.PLATFORM_TYPE)
        headers = {
            "User-Agent": ua,
            "Accept": "*/*", # 对于图片下载，*/* 足够鲁棒
            "Accept-Language": settings.ACCEPT_LANGUAGE,
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        
        # 针对平台的特定伪装
        if platform == "bilibili":
            headers["Referer"] = "https://www.bilibili.com/"
            headers["Origin"] = "https://www.bilibili.com"
        elif platform == "youtube":
            headers["Referer"] = "https://www.youtube.com/"
            
        return headers

    @staticmethod
    async def random_delay():
        """指数级随机退避的基础"""
        delay = random.uniform(settings.MIN_DELAY, settings.MAX_DELAY)
        await asyncio.sleep(delay)