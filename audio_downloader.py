#command way: just replace the last BVid
# yt-dlp -x --audio-format mp3 --audio-quality 0 "https://www.bilibili.com/video/BV1K5mnBHEpv"

"""
Utility to download only the audio track from a Bilibili (or any yt-dlp supported)
video.  The input can be a full URL or a BV id, and the output will be a single
audio file in the specified format (default m4a).

Usage:
    python audio_downloader.py <url_or_bv> [output_dir] [format]

Example:
    python audio_downloader.py BV1nHVmzDEKF data/audio mp3

Dependencies:
    pip install yt-dlp
    ffmpeg must be installed and available on PATH (or specify FFMPEG_PATH in
    a `config.config` module if you already use one elsewhere).
"""

import os
import sys

import yt_dlp


# helper to optionally read ffmpeg location from existing config
_ffmpeg_location = None
try:
    # this import is used by other scripts in this workspace; if it isn't
    # available we simply fall back to whatever is on the PATH.
    from config.config import settings

    _ffmpeg_location = getattr(settings, "FFMPEG_PATH", None)
except Exception:  # pragma: no cover - config is optional
    _ffmpeg_location = None



def download_bilibili_audio(url: str, save_path: str = "data/audio", audio_format: str = "m4a") -> bool:
    """Download the audio track from a Bilibili video.

    Args:
        url: Full URL or BV identifier ("BV..." will be prefixed automatically).
        save_path: Directory where the audio file will be written.
        audio_format: The codec/extension for the final file (m4a, mp3, opus, etc.).

    Returns:
        True on success, False on failure.
    """
    if url.lower().startswith("bv"):
        url = f"https://www.bilibili.com/video/{url}"

    os.makedirs(save_path, exist_ok=True)

    ydl_opts = {
        # tell yt-dlp to fetch the best audio stream only
        "format": "bestaudio/best",
        # supply a directory template for output
        "outtmpl": os.path.join(save_path, "%(title)s.%(ext)s"),
        # convert/extract to the requested audio format using ffmpeg
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": "192",
            }
        ],
        # make debugging visible by default
        "quiet": False,
        "noplaylist": True,
        "socket_timeout": 30,
        "retries": 5,
    }

    if _ffmpeg_location:
        ydl_opts["ffmpeg_location"] = _ffmpeg_location

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            print(f"[*] Downloading audio from {url} -> {save_path} ({audio_format})")
            ydl.download([url])
        return True
    except Exception as e:  # pylint: disable=broad-except
        print(f"[!] audio download failed: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(
            "Usage: python audio_downloader.py <url_or_bv> [output_dir] [format]"
        )
        sys.exit(1)

    inp = sys.argv[1].strip()
    outdir = sys.argv[2] if len(sys.argv) > 2 else "data/audio"
    fmt = sys.argv[3] if len(sys.argv) > 3 else "m4a"

    success = download_bilibili_audio(inp, outdir, fmt)
    if not success:
        sys.exit(1)
"""

import os
import yt_dlp

class BiliAudioDownloader:
    def __init__(self, output_dir="music_downloads", audio_format="mp3", audio_quality="192"):
        """
        初始化下载器
        :param output_dir: 保存目录
        :param audio_format: 输出的音频格式 (mp3, flac, wav, m4a)
        :param audio_quality: 比特率 (192, 320)
        """
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        # yt-dlp 配置参数
        self.ydl_opts = {
            'format': 'bestaudio/best',  # 只请求最佳音频流
            'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'), # 输出文件命名模板
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': audio_quality,
            }],
            # 如果需要下载需要大会员或高音质的音频，可以取消下方注释并传入浏览器的 cookie
            # 'cookiesfrombrowser': ('chrome', ),

            'quiet': False,       # 设为 True 可关闭终端进度条输出
            'no_warnings': True,
        }

    def download_audio(self, url: str):
        """
        下载并提取音频
        """
        print(f"正在解析并下载: {url}")
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # 提取视频信息，可选
                info = ydl.extract_info(url, download=False)
                print(f"视频标题: {info.get('title', 'Unknown')}")

                # 执行下载
                ydl.download([url])
                print(f"\n[+] 下载成功，已保存至 {self.output_dir} 目录。")
        except Exception as e:
            print(f"\n[-] 下载失败，错误信息: {e}")

if __name__ == "__main__":
    # 示例：下载《崩坏：星穹铁道》或《原神》的某一期 OST 视频音频
    # 你可以替换为任意 B 站视频 URL 或 BV 号
    target_url = "https://space.bilibili.com/1340190821/lists/3236620?type=series"

    # 实例化并运行
    downloader = BiliAudioDownloader(output_dir="./ost_collection", audio_format="mp3")
    downloader.download_audio(target_url)
    """
