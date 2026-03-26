from typing import Dict, Any, List
import os
from pydantic_settings import BaseSettings
import ssl
class Settings(BaseSettings):
    # 系统基础配置
    PROJECT_NAME: str = "NexusCrawler"
    WORKER_COUNT: int = 5
    LOG_LEVEL: str = "INFO"
    FFMPEG_PATH:str=r"D:\ffmpeg-2026-01-29-git-c898ddb8fe-full_build\ffmpeg-2026-01-29-git-c898ddb8fe-full_build\bin\ffmpeg.exe"
    YOUTUBE_COOKIE_PATH:str=r"C:\Users\27124\Desktop\crawler\NexusCrawler\www.youtube.com_cookies.txt"

    # 网络与代理
    # 如果为空则直连，否则使用代理。防止在没开VPN时崩溃
    PROXY_URL: str = "http://127.0.0.1:7897" 
    REQUEST_TIMEOUT: int = 15
    STRICT_SSL: bool = False  # 如果遇到 SSL EOF 报错，改为 False
    UA_STRATEGY: str = "pc_only" # 可选: pc_only, mobile_only, mixed
    # 强制分流：哪些平台必须走代理
    PROXY_REQUIRED_PLATFORMS: List[str] = ["youtube", "reddit", "twitter", "telegram", "tiktok", "x"]

    # 爬虫策略：防封号核心
    MIN_DELAY: float = 2.0  # 最小延迟（秒）
    MAX_DELAY: float = 5.0  # 最大延迟
    RANDOM_UA: bool = True
    PLATFORM_TYPE: str = "pc"  # 可选: pc, mobile, mixed

    @property
    def SSL_CONTEXT(self):
        # 产生一个严谨的 SSL 上下文
        context = ssl.create_default_context()
        # 如果你确实遇到 EOF 问题，这里可以增加容错配置
        # context.minimum_version = ssl.TLSVersion.TLSv1_2 
        return context

    # 路径配置
    BASE_DATA_DIR: str = "data"
    DOWNLOAD_DIR: str = os.path.join(BASE_DATA_DIR, "downloads")
    RESULT_DIR: str = os.path.join(BASE_DATA_DIR, "results")

    # OCR 与图片处理开关
    ENABLE_OCR: bool = True
    MEDIA_CONCURRENCY_LIMIT: int = 10 # 限制并发媒体处理任务

    ACCEPT_LANGUAGE: str = "zh-CN,zh;q=0.9,en;q=0.8"

    # 建立域名关键字到平台标识的映射，用于自动推导 Referer 和代理策略
    DOMAIN_PLATFORM_MAP: Dict[str, str] = {
        "hdslb.com": "bilibili",
        "googlevideo.com": "youtube",
        "ytimg.com": "youtube",
        "redd.it": "reddit",
        "twimg.com": "twitter"
    }

    # 定义全局默认参数，作为所有平台的底色
        # 采集规模控制
    GLOBAL_DEFAULT_PARAMS: Dict[str, Any] = {
        "page_size": 20,
        "page_num": 1,
    }
    # 平台特有参数配置（优先级高于全局默认）
    PLATFORM_PARAMS_MAP: Dict[str, Dict[str, Any]] = {
        "bilibili": {
            "page_num": 2,
            "page_size": 20,
            "search_type": "video",
            "order": "totalrank", # 综合排序
            "tids": 0,            # 全分区
        },
        "youtube": {
            "page_num": 1,
            "page_size": 10,
            "relevance_language": "en",
            "safe_search": "moderate",
        },
        "reddit": {
            "page_num": 1,
            "page_size": 50,
            "sort": "new",
            "time": "all",
        }
    }

    # --- 安全红线 (Safety Waterline) ---
    # 无论用户在 submit_task 传入多少，都不能超过这个物理上限，保护流量和 IP
    # 默认全局抓取上限
    DEFAULT_LIMIT: int = 20
    PLATFORM_MAX_LIMITS: Dict[str, int] = {
        "bilibili": 100,
        "youtube": 30,
        "reddit": 100,
        "x": 20
    }
    class Config:
            # 支持从 .env 文件自动加载变量，方便不同环境下切换
            env_file = ".env"
            case_sensitive = True

# 全局配置实例
settings = Settings()