import os
import httpx
import asyncio
import sys
from typing import Dict, List
from config.config import settings
from models.base_model import CrawlResult 
from utils.media_downloader import MediaDownloader
from utils.ocr_engine import DropOCR
from utils.persistence_manager import storage
from utils.anti_bot import AntiBotMiddleware
import cv2
import numpy as np
import re

import traceback
from functools import partial

class NexusEngine:
    def __init__(self, worker_count=settings.WORKER_COUNT):
        self.task_queue = asyncio.Queue()
        self.worker_count = worker_count
        self.spiders = {}
        self.media_semaphore = asyncio.Semaphore(settings.MEDIA_CONCURRENCY_LIMIT)
        self.ocr = DropOCR() # 确保在 init 中
        self.downloader = MediaDownloader()

    def register_spider(self, platform: str, spider_instance):
            """显式注册，方便后续扩展为动态发现"""
            self.spiders[platform] = spider_instance

    def _parse_game_drops(self, ocr_results: list) -> dict:
        """
        将 EasyOCR 返回的 list: [(bbox, text, prob), ...] 转换为结构化字典
        目标：识别类似 'x3', '数量: 5', '10个' 的掉落信息
        """
        extracted_data = {}
        
        # 定义常见掉落物关键字（根据 26fall 申请相关的 RNG 研究需求定制）
        #
        targets = ["大镀剂", "中镀剂", "丁尼", "复写额度", "以太", "火花", "爻光"] 
        
        for i, (bbox, text, prob) in enumerate(ocr_results):
            if prob < 0.4: continue # 过滤低置信度噪声
            
            # 逻辑 1：直接正则匹配数字（如 x10, 数量:5）
            count_match = re.search(r'[xX*：:]\s*(\d+)', text)
            if count_match:
                count = int(count_match.group(1))
                # 尝试寻找该数字前后的关键字
                context_text = ""
                if i > 0: context_text += ocr_results[i-1][1] # 前一个框的内容
                context_text += text
                
                for item in targets:
                    if item in context_text:
                        extracted_data[item] = extracted_data.get(item, 0) + count

        return extracted_data
      
    async def process_media(self, media_item):
            """
            在内存中处理媒体流，同样遵循代理分流与指纹一致性原则
            """
            if media_item.type == "image":
                # 1. 继承解析逻辑，确定该媒体是否需要走 VPN
                # 我们可以直接复用 downloader 的探测逻辑，或者通过 media_item 携带的 platform
                platform = self.downloader._detect_platform(media_item.url)
                proxy = settings.PROXY_URL if platform in settings.PROXY_REQUIRED_PLATFORMS else None
                headers = AntiBotMiddleware.get_headers(platform)

                # 2. 并发控制：使用 Semaphore 防止瞬间压垮 VPN 或 CPU
                async with self.media_semaphore:
                    async with httpx.AsyncClient(
                        proxy=proxy, 
                        headers=headers, 
                        verify=settings.SSL_CONTEXT
                    ) as client:
                        try:
                            resp = await client.get(media_item.url, headers=headers, timeout=settings.REQUEST_TIMEOUT)
                            if resp.status_code == 200:
                                # 3. 内存级 OpenCV 转换与 OCR 识别
                                image_array = np.frombuffer(resp.content, dtype=np.uint8)
                                img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                                ocr_results = self.ocr.reader.readtext(img)
                                return self._parse_game_drops(ocr_results) 
                        except Exception as e:
                            print(f"[!] 内存解析失败 ({platform}): {e}")
            return None
    
    async def worker(self):
        while True:
            task = await self.task_queue.get()
            platform, keyword, params = task # 解构出 params 字典

            try:
                print(f"[*] 处理任务: 平台={platform}, 关键词={keyword}, 参数={params}")

                # 调试：列出已注册 spiders 并打印 platform 的 repr，便于定位匹配问题
                print(f"[*] 已注册 spiders: {list(self.spiders.keys())}")
                print(f"[*] 平台 repr: {repr(platform)}")

                # 更健壮的匹配：尝试大小写容错
                spider = self.spiders.get(platform) or self.spiders.get(str(platform).lower())
                if not spider:
                    print(f"[!] 未找到 spider: {platform}，可用: {list(self.spiders.keys())}")
                    continue

                # 3. 动态指纹与指纹注入
                headers = AntiBotMiddleware.get_headers(platform)
                proxy = settings.PROXY_URL if platform in ["youtube", "reddit", "X"] else None
                
                # 4. 执行抓取：兼容同步/异步 spider.run，并捕获任何异常
                results = []
                try:
                    run_fn = getattr(spider, "run", None)
                    if asyncio.iscoroutinefunction(run_fn):
                        results = await run_fn(
                            keyword=keyword,
                            override_params=params,
                            headers=headers,
                            proxy=proxy
                        )
                    else:
                        loop = asyncio.get_running_loop()
                        func = partial(
                            run_fn,
                            keyword=keyword,
                            override_params=params,
                            headers=headers,
                            proxy=proxy
                        )
                        results = await loop.run_in_executor(None, func)
                except Exception as e:
                    print(f"[!] spider.run 异常 ({platform}): {e}")
                    traceback.print_exc()
                    results = []

                if results is None:
                    results = []

                print(f"[*] {platform} 抓取到 {len(results)} 条结果，开始媒体处理与落地...")
                # NexusEngine.py 的 worker 循环内
                for res in results:
                    # 并发执行内存 OCR
                    process_media_tasks = [self.process_media(media) for media in res.media_list]
                    ocr_outputs = await asyncio.gather(*process_media_tasks, return_exceptions=True)
                    
                    # 过滤掉 None 和 异常，汇总结果
                    valid_drops = [d for d in ocr_outputs if isinstance(d, dict)]
                    if valid_drops:
                        # 汇总该视频所有图片的掉落总数
                        combined_drops = {}
                        for d in valid_drops:
                            for k, v in d.items():
                                combined_drops[k] = combined_drops.get(k, 0) + v
                        
                        # 回填至结果模型，确保持久化到 JSONL
                        res.raw_response = {"extracted_drops": combined_drops} 
                    
                    storage.save(res)
                
                print(f"[✔] {platform} 任务处理完成并落地：{len(results)} 条")


            except httpx.HTTPStatusError as e:
                if e.response.status_code in [403, 412, 429]:
                    print(f"[!!!] 警报：检测到状态码 {e.response.status_code}，疑似 IP 被封禁！")
                    print("[!] 正在紧急停止所有 Worker 以保护 IP...")
                    # 强制终止整个进程
                    os._exit(1)
            finally:
                self.task_queue.task_done()

    async def submit_task(self, platform: str, keyword: str, custom_params: dict = None):
        """
        生产者：将任务塞进队列。
        使用更直观的 page_size 替代模糊的 limit。
        """
        # 1. 参数合并：全局默认 -> 平台默认 -> 用户自定义
        final_params = settings.GLOBAL_DEFAULT_PARAMS.copy()
        final_params.update(settings.PLATFORM_PARAMS_MAP.get(platform, {}))
        if custom_params:
            final_params.update(custom_params)
        
        # 2. 安全红线截断：针对 page_size 的物理保护
        max_allowed = settings.PLATFORM_PARAMS_MAP[platform]['page_size'] if platform in settings.PLATFORM_PARAMS_MAP else 20
        current_size = final_params.get("page_size", 20)
        
        if current_size > max_allowed:
            print(f"[!] 警告: {platform} 的 page_size ({current_size}) 超过安全红线，已强制降级为 {max_allowed}")
            final_params["page_size"] = max_allowed
            
        await self.task_queue.put((platform, keyword, final_params))

    async def start(self):
        """启动引擎：初始化 Workers 并等待任务完成"""
        workers = [asyncio.create_task(self.worker()) for _ in range(self.worker_count)]
        
        # 等待队列中的所有任务被处理
        await self.task_queue.join()
        
        # 任务全部完成后，取消 Worker
        for w in workers:
            w.cancel()

async def main():
    """
    重构后的入口函数：声明式任务调度
    """
    # 1. 初始化引擎：从 config 自动读取 worker_count
    engine = NexusEngine() 
    
    # 2. 动态注册插件 (未来可改为自动扫描 plugins 目录)
    from plugins.bilibili_spider import Spider as BiliSpider
    # from plugins.reddit_spider import Spider as RedditSpider 
    
    engine.register_spider("bilibili", BiliSpider())
    # engine.register_spider("reddit", RedditSpider())

    # 3. 声明式任务清单
    # 结构：(平台, 关键词, 自定义参数字典)
    # 如果自定义参数为 None，submit_task 将自动应用 config 中的默认值
    tasks = [
        # 任务 A：使用默认配置抓取 20 条（由 settings.BILIBILI_DEFAULT_PARAMS 驱动）
        ("bilibili", "全英", {"page_size": 9999,"order": "stow"}),    #最多收藏
        
        # 任务 B：临时覆盖配置，改为抓取 50 条，并按发布时间排序
        #("bilibili", "我一点也不爱人工智能", {"page_size": 50, "order": "pubdate"}),
        
        # 任务 C：Reddit 抓取 (需 VPN 流量)
        #("reddit", "ZZZ RNG", {"page_size": 30}),
        
        # 任务 D：如果你想测试安全红线，传入 9999
        #("bilibili", "海灯节奔霄颂月轮", {"page_size": 9999}) 
    ]
    
    # 4. 批量分发任务
    print(f"[*] {settings.PROJECT_NAME} 正在启动，准备分发 {len(tasks)} 个初始任务...")
    for platform, kw, params in tasks:
        await engine.submit_task(platform, kw, params)
    
    # 5. 启动引擎并阻塞等待完成
    try:
        await engine.start()
    except KeyboardInterrupt:
        print("\n[!] 用户中断，正在优雅关闭 Worker...")
    finally:
        print("[*] 任务处理链条已关闭，数据已持久化至:", settings.RESULT_DIR)

if __name__ == "__main__":
    # 针对 Windows 环境下常见的 ProactorEventLoop 问题进行防御性处理
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())