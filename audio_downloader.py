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
    target_url = "https://space.bilibili.com/401742377/lists/225754?type=series"

    # 实例化并运行
    downloader = BiliAudioDownloader(output_dir="./ost_collection", audio_format="mp3")
    downloader.download_audio(target_url)