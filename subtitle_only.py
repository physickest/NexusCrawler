import requests
import json
import urllib3
import re

# Your target BVIDs
BVID_LIST = ["BV1mhNB6PEPr","BV1WeNi6WE3v","BV1GBNq66EYq","BV1FENG67Eu5","BV1SrNA6zEJ2","BV1McN26oE1n","BV18SNT6DEtH","BV1VPNu6FERV","BV1jANp6MEQ1"]

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
    "Cookie": cookie_str
}

def get_subtitle_url(aid, cid):
    """根据 aid 和特定的 cid 获取字幕下载链接（优先选择普通或AI字幕）"""
    try:
        list_api = f"https://api.bilibili.com/x/player/wbi/v2?aid={aid}&cid={cid}"
        list_data = requests.get(list_api, headers=headers).json().get('data', {})

        subtitles = list_data.get('subtitle', {}).get('subtitles', [])
        if not subtitles:
            return None

        # 优先寻找包含 AI 字幕的轨，如果没有则默认选第一个
        track = next((s for s in subtitles if "AI" in s.get('lan_doc', '')), subtitles[0])
        subtitle_url = track.get('subtitle_url', '')

        if subtitle_url:
            return "https:" + subtitle_url if subtitle_url.startswith("//") else subtitle_url
    except Exception as e:
        print(f"[-] 无法获取 cid {cid} 的字幕链接: {e}")
    return None

def download_subtitle(sub_url, bvid, main_title, part_title, page_num):
    """下载并保存单个分 P 的字幕"""
    try:
        content = requests.get(sub_url, headers=headers).json().get('body', [])
        if not content:
            print(f"[-] {bvid} P{page_num}: 字幕内容为空。")
            return

        # 清理文件名中的非法字符
        full_title = f"{main_title}_P{page_num}_{part_title}" if part_title and part_title != main_title else f"{main_title}_P{page_num}"
        clean_title = re.sub(r'[\\/*?:\u0022<>|]', '', full_title)
        filename = f"{clean_title}_{bvid}.json"

        output = {
            "metadata": {
                "title": main_title,
                "part_title": part_title,
                "page": page_num,
                "bvid": bvid,
                "url": f"https://www.bilibili.com/video/{bvid}?p={page_num}",
                "count": len(content)
            },
            "subtitles": [{"from": s["from"], "to": s["to"], "text": s["content"]} for s in content]
        }

        with open(filename, "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=4)
        print(f"[+] {bvid} P{page_num}: 已保存为 {filename}")

    except Exception as e:
        print(f"[!] {bvid} P{page_num} 保存失败: {e}")

def process_bvid(bvid):
    """主执行逻辑：获取视频的所有分 P 并循环下载"""
    if not bvid:
        return

    try:
        # 获取视频的全局信息
        view_api = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        view_data = requests.get(view_api, headers=headers).json().get('data', {})

        aid = view_data.get('aid')
        main_title = view_data.get('title', 'Unknown')
        pages = view_data.get('pages', []) # 这里包含了所有的分 P 信息

        if not pages:
            print(f"[-] {bvid}: 未找到任何视频分 P 数据。")
            return

        print(f"\n[=>] 开始解析视频: {main_title} ({bvid})，共 {len(pages)} 个分 P")

        # 遍历所有分 P
        for p in pages:
            page_num = p.get('page')  # 第几P
            cid = p.get('cid')        # 对应分P的真实cid
            part_title = p.get('part', '') # 分P的名字

            # 获取当前分 P 的字幕链接
            sub_url = get_subtitle_url(aid, cid)

            if sub_url:
                download_subtitle(sub_url, bvid, main_title, part_title, page_num)
            else:
                print(f"[-] {bvid} P{page_num} ({part_title}): 未找到字幕。")

    except Exception as e:
        print(f"[!] 解析 BVID {bvid} 失败: {e}")

if __name__ == "__main__":
    for bv in BVID_LIST:
        process_bvid(bv)