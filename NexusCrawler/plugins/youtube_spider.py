import yt_dlp
from models import CrawlResult, MediaItem #
from config.config import settings  # 引入全局配置中心
class Spider:
    def __init__(self):
        self.name = "youtube"
        # 核心：使用 yt-dlp 的接口而非硬抓 HTML
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'proxy': 'http://127.0.0.1:YOUR_PORT', # 处理 SSL EOF 的关键
        }

    async def run(self, keyword: str, override_params=None, headers=None, proxy=None) -> list:
        print(f"[*] YouTube 正在深度解析: {keyword}")
        results = []
        
        # 使用多线程运行阻塞的 yt-dlp 逻辑
        with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
            try:
                # 抓取搜索结果元数据
                info = ydl.extract_info(f"ytsearch{settings.YOUTUBE_SEARCH_LIMIT}:{keyword}", download=False)
                for entry in info['entries']:
                    res = CrawlResult(
                        platform=self.name,
                        task_id=entry['id'],
                        author=entry['uploader'],
                        text_content=f"{entry['title']}\n{entry['description'][:200]}",
                        media_list=[
                            MediaItem(type="image", url=entry['thumbnail']),
                            MediaItem(type="video", url=entry['webpage_url'])
                        ]
                    )
                    results.append(res)
            except Exception as e:
                print(f"[!] YouTube 提取失败: {e}")
        return results
    
#“流式抽帧”:如果你心疼流量，在处理视频（YouTube、B 站视频）时，不要下载整个 .mp4。我们可以利用 yt-dlp 获取流地址，然后用 OpenCV 直接在内存里抓图。
"""
import cv2
import yt_dlp

def stream_capture(url):
    ydl_opts = {'format': 'best[height<=480]', 'quiet': True} # 强制低分辨率省流量
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        stream_url = info['url']
        
    cap = cv2.VideoCapture(stream_url)
    success, frame = cap.read()
    if success:
        # 这里直接把 frame 扔给 EasyOCR，不需要保存图片文件
        return frame

"""