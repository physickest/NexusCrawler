"""
When Will These Cookies Change?
Cookies are dynamic and will expire or change under specific circumstances:

Expiration: SESSDATA typically has a lifespan (often 1 to 6 months depending on your account activity). Once it expires, you will receive 403 Forbidden or "No subtitles found" errors in your crawler.

Logging Out: Manually clicking "Log Out" in your browser immediately invalidates the current SESSDATA and bili_jct on Bilibili's servers.

Password Change: Changing your Bilibili account password will force a refresh of all active sessions and invalidate old cookies.

Security Refresh: Bilibili occasionally forces a session refresh if it detects "unusual" activity (like high-frequency scraping) coming from an IP that doesn't match your usual login location.
"""
# Your target BVIDs
BVID_LIST = ["BV1wZF7zqEth", "BV1jyzCBSEBD"]


import requests
import json
import urllib3
import re
def get_subtitle_url(bvid):
    """Fetches any available subtitle URL (Standard or AI) using BVID."""
    try:
        # 1. Get CID and Initial Subtitle List
        view_api = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        view_data = requests.get(view_api, headers=headers).json().get('data', {})
        
        aid, cid = view_data.get('aid'), view_data.get('cid')
        title = view_data.get('title', 'Unknown')
        #print(view_data,"view_data_above")

        list_api = f"https://api.bilibili.com/x/player/wbi/v2?aid={aid}&cid={cid}"
        list_data = requests.get(list_api, headers=headers).json().get('data', {})
        #print(list_data['subtitle']['subtitles'])
        subtitle_url = list_data ['subtitle']['subtitles'][0]['subtitle_url']
        #print(subtitle_url)
        # Check standard list first
        """
        sub_list = view_data.get('subtitle', {}).get('list', [])
        #print(sub_list)
        # 2. Fallback to Player V2 (Where AI subtitles often hide)
        if not sub_list:
            player_api = f"https://api.bilibili.com/x/player/v2?aid={aid}&cid={cid}"
            player_data = requests.get(player_api, headers=headers).json().get('data', {})
            sub_list = player_data.get('subtitle', {}).get('subtitles', [])

        if not sub_list: return None, title

        # 3. Select Track: Prioritize AI if standard is missing
        track = next((s for s in sub_list if "AI" in s.get('lan_doc', '')), sub_list[0])
        #print(track,"above is track")
        url = track['subtitle_url']
        """
        return "https:" + subtitle_url  if subtitle_url .startswith("//") else subtitle_url , title

    except Exception as e:
        print(f"Error resolving {bvid}: {e}")
        return None, None

def process_bvid(bvid):
    """Main execution logic for a single BVID."""
    sub_url, title = get_subtitle_url(bvid)
    #print(sub_url,"fenge",title)
    if not sub_url:
        print(f"[-] {bvid}: No subtitles found.")
        return

    try:
        content = requests.get(sub_url, headers=headers).json().get('body', [])
        
        # Identifiable JSON structure
        output = {
            "metadata": {
                "title": title,
                "bvid": bvid,
                "url": f"https://www.bilibili.com/video/{bvid}",
                "count": len(content)
            },
            "subtitles": [{"from": s["from"], "to": s["to"], "text": s["content"]} for s in content]
        }

        filename = f"{re.sub(r'[\\/*?:\u0022<>|]', '', title)}_{bvid}.json"
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print(f"[+] {bvid}: Saved as {filename}")

    except Exception as e:
        print(f"[!] {bvid} processing error: {e}")

SESSDATA="4c2b36f2%2C1785929168%2Ce7202%2A22CjCxjB-CZO_Npe20EmNTtmTall59wLySpPcsaSUzwNsg9Sfg9qYRMTB8O-hvrvh9tXASVkIzZExsM0htRTBRUlVrazNsNlRCVV9LSmUxU2MzaVBxTS1oUFhkMnc4ZUk4YV9kako3dkpEdDd2VnZRc3ZkcWNJekFrdWJnbmwxMW5SUkc2ZzNKSlJRIIEC"
bili_jct="cabc3d99688c5e3d92aebae910428b6d"
buvid3="21D8213F-8092-723F-502B-3CD1BF2F02FF29300infoc"
MY_COOKIES = {
    "SESSDATA": SESSDATA,
    "bili_jct": bili_jct,
    "buvid3": buvid3
}
cookie_str = "; ".join([f"{k}={v}" for k, v in MY_COOKIES.items()])

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Referer": "https://www.bilibili.com/",
    "Cookie": cookie_str # Optional: Add if videos are login-only 如bilibili不登录只能单个下载
}

if __name__ == "__main__":
    for bv in BVID_LIST:
        process_bvid(bv)
