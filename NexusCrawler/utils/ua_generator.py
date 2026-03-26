# utils/ua_generator.py
import random
from config.config import settings
class UAGenerator:

         # 可直接复制到你的爬虫代码中
    _ua_list = [
    # === PC端 - Chrome ===
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # === PC端 - Firefox ===
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
    # === PC端 - Safari ===
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    # === 移动端 - 安卓 Chrome ===
    "Mozilla/5.0 (Linux; Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; Redmi K50) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Mobile Safari/537.36",
    # === 移动端 - 安卓 Firefox ===
    "Mozilla/5.0 (Android 13; Mobile; rv:121.0) Gecko/121.0 Firefox/121.0",
    # === 移动端 - iOS Safari ===
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (iPad; CPU OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    # === 移动端 - 微信内置浏览器 ===
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 MicroMessenger/8.0.45 NetType/WIFI MiniProgramEnv/Windows WindowsWechat",
    "Mozilla/5.0 (Android 13; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/103.0.5060.129 Mobile Safari/537.36 MicroMessenger/8.0.45.2401(0x28002D39) NetType/WIFI Language/zh_CN",
    # === 小众浏览器/系统 ===
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Vivaldi/6.4.3160.47",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0.1 Safari/605.1.15"
]
    
    @classmethod
    def get_random(cls, platform_type: str =settings.PLATFORM_TYPE) -> str:
        """
        基于你的列表进行语义过滤，而不是手动写死。
        """
        if platform_type == "pc":
            pc_uas = [ua for ua in cls._ua_list if any(x in ua for x in ["Windows", "Macintosh", "X11"])]
            return random.choice(pc_uas)
        
        if platform_type == "mobile":
            mobile_uas = [ua for ua in cls._ua_list if any(x in ua for x in ["iPhone", "Android", "Mobile"])]
            return random.choice(mobile_uas)
            
        if platform_type == "mixed":
            return random.choice(cls._ua_list)

        return random.choice(cls._ua_list)