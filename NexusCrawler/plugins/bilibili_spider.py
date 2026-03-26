import httpx
from models.base_model import CrawlResult, MediaItem
from config.config import settings  # 引入全局配置中心

class Spider:
    def __init__(self):
        self.name = "bilibili"
        self.api_url = "https://api.bilibili.com/x/web-interface/search/all/v2"

    async def run(
        self, 
        keyword: str, 
        override_params: dict = None, 
        headers: dict = None, 
        proxy: str = settings.PROXY_URL
    ) -> list:
        # 1. 以 config 中的默认值为基础
        params = override_params or settings.PLATFORM_PARAMS_MAP.get(self.name, {}).copy() 
        
        # B站原始 API 叫 'pagesize'，我们在 Spider 内部做一次映射
        api_params = {
            "keyword": keyword,
            "page": params.get("page_num", 1),
            "pagesize": params.get("page_size", 20), # 语义映射
            "search_type": params.get("search_type", "video"),
            "order": params.get("order", "totalrank")
        }
        params.update(api_params)
        
        # 使用 settings 中定义的超时时间
        async with httpx.AsyncClient(
            http2=True, 
            timeout=settings.REQUEST_TIMEOUT, 
            proxy=proxy
        ) as client:
            try:
                # 注意：在这里统一注入由 AntiBotMiddleware 生成的 headers
                response = await client.get (
                    self.api_url, 
                    params=params, 
                    headers=headers,    
                )
                
                if response.status_code != 200:
                    print(f"[!] {self.name} 异常状态码: {response.status_code}")
                    return []
                # save(response.json(), "debug_bilibili.json")  # 调试用：保存原始响应
                return self.parse(response.json())
            except Exception as e:
                print(f"[!] Bilibili 采集失败: {e}")
                return []

    def parse(self, data: dict) -> list:
        results = []
        all_results = data.get("data", {}).get("result", [])
        
        # 这种用 next() 找结果的方法在 API 结构变动时很鲁棒
        video_data = next(
            (item.get("data") for item in all_results if item.get("result_type") == "video"), 
            []
        )

        for v in video_data:
            # 自动处理 URL 前缀补全
            img_url = v.get("pic")
            if img_url and not img_url.startswith("http"):
                img_url = "https:" + img_url

            res = CrawlResult(
                platform=self.name,
                task_id=str(v.get("aid")),
                author=v.get("author"),
                text_content=f"{v.get('title')} | 简介: {v.get('description')}",
                media_list=[
                    MediaItem(type="image", url=img_url, metadata={"play": v.get("play")}),
                    MediaItem(type="video", url=f"https://www.bilibili.com/video/{v.get('bvid')}")
                ]
            )
            results.append(res)
        return results