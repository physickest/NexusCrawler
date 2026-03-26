import browser_cookie3
import yt_dlp

def get_yt_cookies():
    # Extracts cookies directly from Chrome's decrypted storage
    cj = browser_cookie3.chrome(domain_name='.youtube.com')
    return cj

ydl_opts = {
    'cookiefile': 'youtube_session.txt', # yt-dlp will save them here if provided
    'quiet': False
}

with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    # Pass the cookie jar directly if not using a file
    ydl.cookiejar = get_yt_cookies()
    ydl.download(['https://www.youtube.com/watch?v=4gYm0Rp7VHc'])