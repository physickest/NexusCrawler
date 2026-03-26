import yt_dlp
#from config.config import settings
import ffmpeg
import os
import shutil  # <-- Required for path verification

import subprocess

def fix_and_verify_js_runtime():
    """
    Forces the subprocess to use global JS runtimes, bypassing broken Conda binaries.
    Validates execution rather than just file existence.
    """
    # 1. Isolate known good paths (Winget Node.js and PowerShell Deno)
    global_node = r"C:\Program Files\nodejs"
    global_deno = os.path.expanduser(r"~\.deno\bin")
    
    # 2. Forcefully inject them at the very front of the subprocess PATH
    valid_paths = [p for p in [global_node, global_deno] if os.path.exists(p)]
    if valid_paths:
        os.environ["PATH"] = os.pathsep.join(valid_paths) + os.pathsep + os.environ.get("PATH", "")

    # 3. Perform an actual execution test to ensure it does not crash
    try:
        # Prefer node, fallback to deno
        engine = "node" if shutil.which("node") else "deno"
        if not engine:
            raise FileNotFoundError("Neither Node nor Deno could be found in the global paths.")
            
        result = subprocess.run([engine, "-v"], capture_output=True, text=True, check=True)
        print(f"[*] JS Engine Active & Verified: {engine} {result.stdout.strip()}")
    except Exception as e:
        raise EnvironmentError(
            f"[Fatal] A JS engine was found, but it crashes upon execution. "
            f"This is usually caused by broken Conda DLLs. \nError details: {e}\n"
        )

def sota_download_youtube(url: str, save_path: str = "data/downloads"):
    """
    Executes yt-dlp via an isolated subprocess to bypass Conda IPC bridging issues.
    This guarantees native JS engine detection and prevents 'n' cipher drops.
    """
    # 1. Path Resolutions
    cookie_path = os.path.abspath("www.youtube.com_cookies.txt")
    out_tmpl = os.path.join(save_path, '%(title)s.%(ext)s')
    
    # 2. Verify CLI availability
    ytdlp_exe = shutil.which("yt-dlp")
    if not ytdlp_exe:
        raise FileNotFoundError("[Fatal] yt-dlp CLI binary not found in PATH.")

    # 3. Construct the state-of-the-art argument matrix
    # 3. Construct the state-of-the-art argument matrix
    command = [
        ytdlp_exe,
        "--cookies", cookie_path,
        "--proxy", "http://127.0.0.1:7897",
        
        # ---------------------------------------------------------
        # THE CRITICAL FIX: EJS Hot-Loading & Explicit Engine Bind
        # ---------------------------------------------------------
        "--remote-components", "ejs:github", # Dynamically fetches the missing n-cipher solver
        "--js-runtimes", "node",             # Forces CLI to bind strictly to Node
        
        # Extractor bypasses for SABR and PO Tokens
        "--extractor-args", "youtube:player_client=tv,web",
        
        # Multiplexing and Formatting
        "-f", "bestvideo+bestaudio/best",
        "--merge-output-format", "mp4",
        "-o", out_tmpl,
        
        # Cache clearing
        "--rm-cache-dir", 
        
        # Target
        url
    ]
    print(f"[*] Booting Isolated CLI Pipeline for: {url}")
    
    try:
        # 4. Execute with real-time stdout streaming
        process = subprocess.Popen(
            command, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.STDOUT, 
            text=True,
            encoding='utf-8', # Force UTF-8 to prevent Node.js CP936 crashes
            errors='replace'
        )

        for line in process.stdout:
            # Filter out the noise, print only critical status updates
            if any(keyword in line for keyword in ["[download]", "[youtube]", "ERROR", "WARNING"]):
                print(line.strip())

        process.wait()
        
        if process.returncode == 0:
            print("\n[+] Download and multiplexing seamlessly completed.")
        else:
            print(f"\n[-] CLI Pipeline exited with code {process.returncode}")

    except Exception as e:
        print(f"\n[-] Subprocess Error: {e}")

def verify_js_runtime():
    """Pre-flight check to ensure the JS runtime is bound to the subprocess PATH."""
    if not (shutil.which("node") or shutil.which("deno")):
        raise EnvironmentError(
            "[Fatal] JS Runtime not found in PATH. "
            "YouTube's 'n' cipher cannot be decrypted. "
            "Install Node.js globally (winget install OpenJS.NodeJS) and restart your IDE."
        )



def sota_download_bilibili(url: str, save_path: str = "data/videos"):
    ydl_opts = {
        # 1. 格式选择：优先选择 1080p+ 且合并为 mp4 方便后续 AI 抽帧
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        
        # 2. 外部依赖路径：对齐你的本地 FFmpeg
        'ffmpeg_location': settings.FFMPEG_PATH, 
        
        # 3. 反爬与指纹：B 站必须有 Referer
        'http_headers': {
            'Referer': 'https://www.bilibili.com',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36...'
        },
        
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
    
if __name__ == "__main__":
    #sota_download_bilibili("https://www.bilibili.com/video/BV1PmvsBcEAd/?spm_id_from=333.1387.favlist.content.click&vd_source=41ac0cb6007ceac3544bdbb195b7cd45",save_path="data/downloads")
    os.makedirs("data/downloads", exist_ok=True)
    target_url = "https://www.youtube.com/watch?v=f2_841yROHc"
    sota_download_youtube(target_url, save_path="data/downloads")
    """
    powershell_command_for_download:
    & "D:\ffmpeg-2026-01-29-git-c898ddb8fe-full_build\ffmpeg-2026-01-29-git-c898ddb8fe-full_build\bin\ffmpeg.exe" -http_proxy "http://127.0.0.1:7897" -i "https://vv.jisuzyv.com/play/0dNX3Z6a/index.m3u8" -c copy "Avengers_Endgame.mp4"
    """
