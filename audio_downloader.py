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
