import asyncpraw
from models import CrawlResult, MediaItem
from config.config import settings  # 引入全局配置中心
class Spider:
    def __init__(self):
        self.name = "reddit"
        # 实际申请 PhD 时，这些凭证应从环境变量或配置中心读取
        self.reddit = asyncpraw.Reddit(
            client_id="YOUR_ID",
            client_secret="YOUR_SECRET",
            user_agent="NexusCrawler 1.0 by /u/yourname"
        )

    async def run(self, keyword: str, override_params=None, headers=None, proxy=None) -> list:
        results = []
        try:
            # 在全站搜索关于“绝区零”的内容
            subreddit = await self.reddit.subreddit("all")
            async for submission in subreddit.search(keyword, limit=limit):
                item = CrawlResult(
                    platform=self.name,
                    task_id=submission.id,
                    author=str(submission.author),
                    text_content=submission.title + " " + (submission.selftext[:500]),
                    media_list=self._extract_media(submission)
                )
                results.append(item)
        except Exception as e:
            print(f"[!] {self.name} Error: {e}")
        return results

    def _extract_media(self, post):
        # 简单处理：如果是图片贴
        if hasattr(post, 'url') and any(ext in post.url for ext in ['.jpg', '.png', '.gif']):
            return [MediaItem(type="image", url=post.url)]
        return []