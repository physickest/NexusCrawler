from pydantic import BaseModel, Field
from typing import List, Optional, Union
from datetime import datetime

class MediaItem(BaseModel):
    type: str  # "image", "video", "audio"
    url: str
    metadata: Optional[dict] = None  # 分辨率、时长等

class CrawlResult(BaseModel):
    platform: str
    task_id: str
    author: str
    text_content: str
    media_list: List[MediaItem] = []
    raw_response: Optional[dict] = None  # 保留原始数据以备逆向分析
    timestamp: datetime = Field(default_factory=datetime.now)