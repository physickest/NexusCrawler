import yt_dlp
#from config.config import settings
import ffmpeg
import os

def sota_download_youtube(url, save_path="data/downloads", cookie_file=None, use_cookies=True):
    # Ensure save directory exists
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if cookie_file is None:
        cookie_file = r"C:\Users\EtherEditor\Desktop\scrape_subtitle\www.youtube.com_cookies.txt"

    # warn about old cookies
    if use_cookies and os.path.exists(cookie_file):
        import time
        age = time.time() - os.path.getmtime(cookie_file)
        if age > 7 * 24 * 3600:
            print(f"[!] Cookie file {cookie_file} is more than a week old; consider re-exporting it.")

    if use_cookies and not os.path.exists(cookie_file):
        print(f"[-] Error: {cookie_file} not found. Export it from Chrome (Netscape format) or set use_cookies=False.")
        return

    ydl_opts = {
            # 1. Extractor: Use clients with looser PO Token checks
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'tv', 'default'],
                }
            },

            # 2. Authentication & Network
            'proxy': 'http://127.0.0.1:7897',
            'external_downloader': 'ffmpeg',
            'hls_prefer_native': False,

            # 3. Format Selection
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),

            # 4. Robustness
            'socket_timeout': 30,
            'retries': 10,

            # [NEW] 5. Direct Browser Cookie Extraction
            # Ensure Chrome is completely closed before running the script,
            # as Chromium locks its SQLite database while open.
            'cookiesfrombrowser': ('chrome', ),
        }

    # Delete or comment out the manual file loading logic:
    # if use_cookies:
    #     ydl_opts['cookiefile'] = cookie_file
    if use_cookies:
        ydl_opts['cookiefile'] = cookie_file

    def _download(opts):
        with yt_dlp.YoutubeDL(opts) as ydl:
            print(f"[*] Initiating Handshake via mweb Client: {url}")
            ydl.download([url])

    try:
        _download(ydl_opts)
    except yt_dlp.utils.DownloadError as e:
        msg = str(e)
        print(f"[-] DownloadError: {msg}")
        # common cookie/authentication failures
        if 'cookies' in msg.lower() or 'sign in to confirm' in msg.lower():
            print("[!] Cookie-based authentication failed; retrying without cookies.")
            # remove cookie settings and retry once
            ydl_opts.pop('cookiefile', None)
            ydl_opts['nookies'] = True
            try:
                _download(ydl_opts)
            except Exception as e2:
                print(f"[-] Retry without cookies also failed: {e2}")
        elif 'Requested format is not available' in msg:
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    ydl.list_formats(info)
            except Exception:
                pass
    except Exception as e:
        print(f"[-] Critical Error: {e}")

def sota_download_bilibili(url: str, save_path: str = "data/videos"):
    ydl_opts = {
        # 1. 格式选择：优先选择 1080p+ 且合并为 mp4 方便后续 AI 抽帧
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',

        # 2. 外部依赖路径：对齐你的本地 FFmpeg
        #'ffmpeg_location': settings.FFMPEG_PATH,

        # 3. 反爬与指纹：B 站必须有 Referer
        'http_headers': {
            'Referer': 'https://www.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'
        },
        'extractor_args': {
            'youtube': { ... },   # 如果有需要可以保留
        },
        'sleep_interval': 0,          # 每次请求前至少等待 5 秒
        'max_sleep_interval': 1,     # 最大等待 10 秒
        'sleep_interval_requests': 1, # 如果请求失败，重试前等待 1 秒
        # 4. 网络策略：国内 B 站下载通常不需要走 VPN 代理，建议直连
        # 如果你一定要走，请确保 settings.PROXY_URL 正确
        'proxy': None, # B 站下载直连速度通常更快，除非你在海外

        'outtmpl': f'{save_path}/%(title)s.%(ext)s',
        'socket_timeout': 30,
        'retries': 5,
        'quiet': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"[*] 正在通过 NexusEngine 调度下载: {url}")
            ydl.download([url])
            return True
        except Exception as e:
            print(f"[!] B站视频下载失败: {e}")
            return False


def batch_download_bilibili_up(up_space_url: str, save_path: str = "data/videos"):
    """
    批量下载 B 站 UP 主的所有视频
    示例 URL: https://space.bilibili.com/12345678
    """
    ydl_opts = {
        # 1. 格式选择
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',

        # 2. 动态保存路径：按 UP 主名称自动建文件夹
        'outtmpl': f'{save_path}/%(uploader)s/%(title)s.%(ext)s',

        # 3. 身份验证 (核心)：B站批量抓取列表必须要有 Cookie
        # 确保运行脚本时 Chrome 是关闭的，或者使用导出的 cookies.txt
        #'cookiesfrombrowser': ('chrome', ),

        # 4. 反爬与指纹
        'http_headers': {
            'Referer': 'https://www.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        },

        # 5. 批量下载防封策略 (核心)：绝不能太快！
        'sleep_interval': 0,         # 每次下载前至少等待 10 秒
        'max_sleep_interval': 2,     # 最大随机等待 25 秒
        'sleep_requests': 2,          # 获取网页信息时的请求延时

        # 6. 容错：如果列表中某个视频被删了或有版权限制，跳过并继续下载下一个，不要让整个程序崩溃
        'ignoreerrors': True,

        'socket_timeout': 30,
        'retries': 5,
        'quiet': False,
        'cookiefile': "C:\\Users\\EtherEditor\\Desktop\\scrape_subtitle\\www.bilibili.com_cookies.txt",
        'noplaylist': False,  # 确保允许下载列表/分P
        'extract_flat': False, # 确保不仅提取信息，还要实际下载
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            print(f"[*] 正在提取 UP 主主页视频列表并开始批量下载: {up_space_url}")
            ydl.download([up_space_url])
            print("[+] 批量下载任务结束！")
            return True
        except Exception as e:
            print(f"[!] B站批量下载中断: {e}")
            return False

if __name__ == "__main__":
    sota_download_bilibili("https://www.bilibili.com/video/BV1MVcTzDEy3?t=1001.5",save_path="data/downloads")
    # sota_download_youtube("https://www.youtube.com/watch?v=woMULmmr3u0", save_path="data/downloads")
        # 替换为你想要下载的 UP 主空间链接
    #batch_download_bilibili_up("https://space.bilibili.com/3494379350133362/upload/video", save_path="data/downloads")
    """
    powershell_command_for_download:
    & "D:\ffmpeg-2026-01-29-git-c898ddb8fe-full_build\ffmpeg-2026-01-29-git-c898ddb8fe-full_build\bin\ffmpeg.exe" -http_proxy "http://127.0.0.1:7897" -i "https://vv.jisuzyv.com/play/0dNX3Z6a/index.m3u8" -c copy "Avengers_Endgame.mp4"
    """