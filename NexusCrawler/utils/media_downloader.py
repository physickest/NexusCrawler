# utils/media_downloader.py
import httpx
import os
import hashlib
import ssl
from config.config import settings  # 引入全局配置中心
from utils.anti_bot import AntiBotMiddleware
from urllib.parse import urlparse

class MediaDownloader:
    def __init__(self, base_path: str = settings.DOWNLOAD_DIR):
        self.ssl_context = settings.SSL_CONTEXT
        self.base_path = base_path
        if not os.path.exists(base_path):
            os.makedirs(base_path)
        #self.proxy = settings.PROXY_URL
        #self.proxy_domains = settings.PROXY_REQUIRED_PLATFORMS
    
    def _detect_platform(self, url: str) -> str:
        """从 URL 自动推导出平台标识，用于获取正确的指纹"""
        domain = urlparse(url).netloc
        for key, platform in settings.DOMAIN_PLATFORM_MAP.items():
            if key in domain:
                return platform
        return "general"

    async def download(self, url: str) -> str:
        proxy = settings.PROXY_URL if platform in settings.PROXY_REQUIRED_PLATFORMS else None 
        platform = self._detect_platform(url)
        headers = AntiBotMiddleware.get_headers(platform) # 内部已沿用你的 _ua_list

        """下载媒体文件并返回本地路径，文件名使用 URL 的 MD5 以去重"""
        file_hash = hashlib.md5(url.encode()).hexdigest()
        file_path = os.path.join(self.base_path, f"{file_hash}.jpg")
        
        # 如果文件已存在，直接返回路径（减少重复 IO）
        if os.path.exists(file_path):
            return file_path

        # 在 Spider 或 Downloader 中使用自定义 Client
        async with httpx.AsyncClient(
            verify=settings.SSL_CONTEXT,   #verify=False # 处理某些代理导致的 SSL EOF 问题的暴力方案，但存在中间人攻击风险
            proxy=proxy, # 确保这一行存在
            timeout=settings.REQUEST_TIMEOUT,
            http2=True # 开启 HTTP2 以降低被检测风险
        ) as client:
            # 你的抓取逻辑
         from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

        @retry(
            stop=stop_after_attempt(3), 
            wait=wait_exponential(multiplier=1, min=4, max=10),
            retry=retry_if_exception_type((httpx.ConnectError, httpx.ReadError))
        )
        async def robust_fetch(url):
            # 这里写你的抓取逻辑
            try:
                resp = await client.get(url)
                if resp.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(resp.content)
                    return file_path
            except Exception as e:
                print(f"[!] 下载失败: {url} | 错误: {e}")
        return ""