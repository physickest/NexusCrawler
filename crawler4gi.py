#针对GI，其他网页需要调整str等参数
import requests
import json
import time
import re
import pandas as pd

def master_weapon_crawler():
    # 核心 API 地址
    # 1. 将变动频繁的 AppID 抽离成变量
    # 你的截图显示的是 16471662a82d418a，请以此为准
    app_id_segment = "16471662a82d418a" 
    api_url = f"https://act-api-takumi-static.mihoyo.com/content_v2_user/app/{app_id_segment}/getContentList"

    all_results = []
    page = 1
    page_size = 50 # 工业级标准：单次获取 20-50 条，平衡效率与风险

            # 这里的 Header 是解决 "app not found" 的核心
    headers = {
            "Accept": "application/json, text/plain, */*", #加上 application/json 是为了强制握手，确保返回的是我们 Pipeline 能处理的结构化数据
            "Origin": "https://ys.mihoyo.com",
            "Referer": "https://ys.mihoyo.com/", # 必须告诉服务器你从哪来
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"   #标识这是一个 Ajax（异步）请求.这是许多 Web 框架（如 Django, Spring）区分“直接页面访问”和“API 数据调用”的标准，否则会认为是僵尸程序
            #Cookie: 当你需要抓取个人信息、背包数据或需要登录权限的内容时（涉及身份鉴权）
            #Content-Type: 当你使用 POST 方法发送数据（如模拟登录、提交表单）时，必须指定发送数据的格式。
            #DS (Dynamic Secret): 这是米哈游特有的安全签名。如果你去爬米游社 App 接口，不带动态生成的 DS，请求会直接被 403 封杀。
        }

    print("[*] 开始全量数据同步...")

    while True:
            #params在network- Payload中
            params = {
                "iAppId": "43",
                "iChanId": "720",
                "iPageSize": page_size,
                "iPage": page,
                "sLangKey": "zh-cn"
            }

            try:
                #这些str参数在Network-Preview中
                res = requests.get(api_url, params=params, headers=headers, timeout=10)
                data = res.json()
                items = data.get('data', {}).get('list', [])

                if not items:
                    break # 扫描完毕

                for item in items:
                    title = item.get('sTitle', '')
                    if "神铸赋形" in title:
                        info_id = item.get('iInfoId')
                        # 补充：记录发布时间，这对 PhD 分析概率周期非常有价值
                        start_time = item.get('dtStartTime', 'Unknown')
                        all_results.append({
                            "title": title,
                            "date": start_time,
                            "url": f"https://ys.mihoyo.com/main/news/detail/{info_id}",
                            "sContent": item.get('sContent', '')
                        })
                
                print(f"[>] 已完成第 {page} 页扫描，累计命中 {len(all_results)} 个武器池")
                
                # 停止条件：如果 items 数量少于 page_size，说明是最后一页
                if len(items) < page_size:
                    break
                    
                page += 1
                time.sleep(0.3) # 保持频率在人类极限范围内

            except Exception as e:
                print(f"[!] 异常中断: {e}")
                break

        # 数据持久化：存储为 JSON
    with open("weapon_wishes_withsContent.json", "w", encoding="utf-8") as f:
            json.dump(all_results, f, ensure_ascii=False, indent=2)
        
    print(f"\n[Done] 数据同步完成！共发现 {len(all_results)} 次武器池更新。文件已保存。")

def sota_weapon_cleaner(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        items = json.load(f)

    # 1. 建立归一化映射（数据预处理的核心）
    def preprocess_html(text):
        if not text: return ""
        # 替换常见的 HTML 实体，将异质数据对齐
        text = text.replace("&middot;", "·").replace("&nbsp;", " ")
        text = text.replace("&ldquo;", "「").replace("&rdquo;", "」")
        # 移除所有 HTML 标签，只保留纯文本，极大提升信噪比 (SNR)
        clean_text = re.sub(r'<[^>]+>', '', text)
        return clean_text

    results = []
    seen_banners = set() # 用于去重：即将开启 vs 现已开启

    # 预编译正则，注意旧版有时用“五星”，有时用“5星”
    weapon_pattern = re.compile(r"「(.*?)」")
    star_5_pattern = re.compile(r"[5五]星武器(.*?)[。！]")
    star_4_pattern = re.compile(r"4星武器(.*?)[。！]")

    for item in items:
        title = item.get('title') or ""
        # 去重逻辑：基于标题中的武器名进行 Hash
        banner_id = "".join(weapon_pattern.findall(title))
        if not banner_id or banner_id in seen_banners:
            continue
        seen_banners.add(banner_id)

        content = preprocess_html(item.get('sContent', ''))
        
        # 提取逻辑
        f5_match = star_5_pattern.search(content)
        f5_list = weapon_pattern.findall(f5_match.group(1)) if f5_match else []
        
        f4_match = star_4_pattern.search(content)
        f4_list = []
        if f4_match:
            # 提取所有武器，并过滤掉已经出现在 5 星里的（针对旧版混合描述的鲁棒性）
            f4_list = [w for w in weapon_pattern.findall(f4_match.group(1)) if w not in f5_list]

        # 归一化武器名（去掉前缀）
        def norm(w): return w.split('·')[-1]

        results.append({
            "date": item.get('date'),
            "5_star": " & ".join([norm(w) for w in f5_list]),
            "4_star": " | ".join([norm(w) for w in f4_list]),
            "title": title
        })

    df = pd.DataFrame(results)
    return df

if __name__ == "__main__":
    df = sota_weapon_cleaner("weapon_wishes.json")
    df.to_csv("all_history_cleaned.csv", index=False, encoding="utf-8-sig")
    print(f"[*] 战果：成功提取 {len(df)} 期唯一武器池。")
    print(df.tail(10)) # 查看最老的数据是否成功
    """
    import json

with open("weapon_wishes.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    print(f"Type: {type(data)}")
    if isinstance(data, list):
        print(f"Length: {len(data)}")
        print(f"First element keys: {data[0].keys() if len(data)>0 else 'Empty'}")
    elif isinstance(data, dict):
        print(f"Top level keys: {data.keys()}")
        """