import json
import os
from datetime import datetime
from models.base_model import CrawlResult
from config.config import settings  # 引入全局配置中心

class JSONLStorage:
    def __init__(self, base_dir: str = settings.RESULT_DIR):
        self.base_dir = base_dir
        if not os.path.exists(base_dir):
            os.makedirs(base_dir)

    def save(self, result: CrawlResult):
        """将单条抓取结果追加写入平台对应的 jsonl 文件"""
        # 按平台分类存储，方便后续针对性训练 AI
        file_path = os.path.join(self.base_dir, f"{result.platform}.jsonl")
        
        # 将模型转为字典，并处理 datetime 序列化
        data = result.dict()
        data['timestamp'] = data['timestamp'].isoformat()

        with open(file_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(data, ensure_ascii=False) + "\n")

# 全局实例，方便调用
storage = JSONLStorage()