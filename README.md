cat DEPRECATED mouse


subtitle_only-Currently-just-for-bilibili
input:BVID_LIST, output:a .json file with "title","url","subtitles"with "from" "to" and "text"

Error causes that would occur in future:

cookies
bilibili's logic
unkown for now

=========================================================================================================================================================================================

# NexusCrawler
Crawler initially aiming at bilibili, youtube, reddit, Telegram, zhihu , rednote , tiktok ,X , hoyolab ,QQ ,tieba .Deprecated for now for evolving versions and astronomical API costs

To align with your profile as a **Silicon Valley Tech Lead** and a **26fall AI PhD applicant**, this README is designed to showcase engineering rigor, architectural depth, and research potential. It highlights the multi-modal nature of the project and your sophisticated approach to anti-bot challenges.

---

# NexusCrawler: High-Performance Multi-Modal Data Engine

**NexusCrawler** is a robust, asynchronous data acquisition framework designed for large-scale multi-modal research. Originally developed to analyze **RNG (Gacha) mechanics** in titles like *Zenless Zone Zero*, it has evolved into a generalized engine capable of cross-platform scraping, in-memory OCR, and automated video ingestion.

## 🚀 Key Research Features

* **Asynchronous Scalability**: Built on `asyncio` and `httpx`, the engine supports high-concurrency tasks with a configurable worker pool to maximize throughput.
* **Multi-Modal Intelligence**: Integrates **EasyOCR** and **OpenCV** for in-memory image analysis. It extracts structured data from game screenshots without local disk persistence, optimizing I/O for large datasets.
* **Architectural Rigor**: Features a centralized configuration system that enforces "safety waterlines" for `page_size` and request density, preventing IP blacklisting.
* **Industrial-Grade Anti-Bot**:
* **Fingerprint Consistency**: Implements a platform-aware Header/UA distribution system derived from a curated list of PC and mobile browser fingerprints.
* **Dynamic Proxy Routing**: Automatically routes traffic through VPN/Proxies based on domain sensitivity (e.g., YouTube vs. Bilibili).
* **SSL Integrity**: Enforces strict `ssl.create_default_context()` validation for secure, authentic communication.



## 🛠 Tech Stack

* **Language**: Python 3.10+
* **Network**: `httpx` (HTTP/2 support), `websockets`
* **Computer Vision**: `EasyOCR`, `OpenCV`, `NumPy`
* **Video Engine**: `yt-dlp`, `FFmpeg`
* **DevOps**: `Git`, `Pydantic-Settings`

## 📂 Project Structure

```text
NexusCrawler/
├── config/           # Centralized settings & platform-specific params
├── core/             # NexusEngine: The asynchronous task orchestrator
├── plugins/          # Platform-specific spiders (Bilibili, Reddit, etc.)
├── utils/            
│   ├── anti_bot.py   # Header injection & fingerprint management
│   ├── ocr_engine.py # EasyOCR wrapper for structured data extraction
│   └── media_downloader.py # Reliable, proxy-aware media ingestion
└── data/             # Persistent JSONL storage & media downloads

```

## 📋 Usage & Configuration

1. **Clone the Repository**:
```bash
git clone https://github.com/EtherEditor/NexusCrawler.git
cd NexusCrawler

```


2. **Environment Setup**:
Configure your `.env` file with `PROXY_URL` and `FFMPEG_PATH`.
3. **Run the Engine**:
```python
# main.py
from core.engine import NexusEngine

# Declarative task submission
tasks = [("bilibili", "ZZZ Gacha Analysis", {"page_size": 50})]

```



## 📝 Ongoing Research (26fall Prep)

This project serves as the data foundation for a statistical study on **Pseudo-Random Number Generation (PRNG)** and drop rate variances in open-world RPGs. Future milestones include:

* Real-time WebSocket monitoring for social media triggers.
* Automated video frame sampling and labeling.
* Statistical validation of gacha "pity" mechanisms using massive scraped datasets.

---

**Would you like me to add a "License" section or a "Contribution" guide to make it even more professional for your GitHub profile?**
