
# NexusCrawler: High-Performance Multi-Modal Data Engine

**NexusCrawler** is an advanced, asynchronous data acquisition and processing framework designed for large-scale multi-modal research. Originally conceived to analyze pseudo-random number generation (PRNG) and drop-rate variances in games like *Zenless Zone Zero* and *Genshin Impact*, the system has evolved into a comprehensive pipeline capable of cross-platform scraping, in-memory OCR, automatic speech recognition (ASR), and robust video ingestion.

## 🚀 Core Architectural Advancements

* **Asynchronous Task Orchestration (`NexusEngine`)**: Built on `asyncio` and `httpx` (HTTP/2), the engine dynamically distributes tasks across a configurable worker pool. It features strict "safety waterlines" for `page_size` and concurrent requests to prevent IP blacklisting.
* **In-Memory Multi-Modal Pipeline**: Eliminates unnecessary I/O overhead by stream-capturing media. It integrates **OpenCV** and **EasyOCR** (`ocr_engine.py`) to extract structured text directly from image byte streams in memory, instantly translating pixel data into high-entropy JSON payloads.
* **SOTA Media Ingestion & JS Isolation**: The `video_downloader.py` implements a state-of-the-art subprocess pipeline that forcefully injects global JS runtimes (Node/Deno). This completely bypasses broken Conda IPC bridges, natively solving YouTube's 'n' cipher decryption and preventing silent extraction failures.
* **Industrial-Grade Anti-Bot Mechanics**:
  * **Dynamic Fingerprinting**: `UAGenerator` manages OS-aware (PC/Mobile/Mixed) User-Agent rotation.
  * **Intelligent Routing**: `DOMAIN_PLATFORM_MAP` automatically routes requests through proxy networks (e.g., YouTube, Reddit) while allowing direct connections for domestic endpoints (Bilibili).
  * **SSL Integrity**: Enforces rigorous `ssl.create_default_context()` validation.

## 🧠 AI & NLP Toolchain

Beyond scraping, NexusCrawler provides a suite of offline and API-based AI utilities for dataset generation:
* **`video2text.py`**: Utilizes OpenAI's **Whisper** model to automatically strip audio from video containers and generate highly accurate `.srt` subtitles locally.
* **`text2audio.py`**: Integrates **Edge-TTS** for high-quality, programmatic text-to-speech generation. Features randomized voice pooling and speed/volume mutation, ideal for generating synthetic audio datasets.
* **`subtitle_only.py`**: Directly hooks into Bilibili's internal API (V1 and V2 players) to cleanly extract both standard and AI-generated subtitle tracks into structured JSON.

## 📂 Project Structure

```text
NexusCrawler/
├── config/
│   └── config.py             # Centralized settings & platform-specific parameters
├── models/
│   └── base_model.py         # Pydantic data schemas for structured outputs
├── plugins/
│   ├── bilibili_spider.py    # Bilibili WBI/API extractor
│   ├── youtube_spider.py     # YouTube metadata integration
│   └── reddit_spider.py      # Async PRAW implementation
├── utils/
│   ├── anti_bot.py           # Header injection & backoff algorithms
│   ├── media_downloader.py   # Robust, proxy-aware media fetcher
│   ├── ocr_engine.py         # EasyOCR bounding box and probability logic
│   └── persistence_manager.py# JSONL automated storage
├── core/
│   ├── NexusEngine.py        # The asynchronous worker queue & task dispatcher
│   └── BaseSpider.py         # Abstract base classes for plugin architecture
├── tools/
│   ├── video_downloader.py   # SOTA yt-dlp wrapper with JS-engine verification
│   ├── audio_downloader.py   # FFmpeg-backed audio stream extraction
│   ├── video2text.py         # Local Whisper ASR transcriptions
│   ├── text2audio.py         # Edge-TTS synthetic audio generation
│   └── crawler4gi.py         # Targeted scraper for Genshin Impact historical data
└── README.md
```

## 🛠 Prerequisites & Installation

1. **Python 3.10+**
2. **System Dependencies**:
   * **FFmpeg**: Must be installed and accessible in your system `PATH` (or defined in `config.py`).
   * **Node.js or Deno**: Required for YouTube cipher decryption.
3. **Python Packages**:
   ```bash
   pip install httpx easyocr opencv-python yt-dlp openai-whisper edge-tts pydantic-settings
   ```

## 📋 Usage Examples

### 1. Running the Nexus Engine (Data Scraping)
Configure your `.env` file or `config.py` with your `PROXY_URL` and `FFMPEG_PATH`, then define your declarative tasks in `NexusEngine.py`:

```python
from NexusEngine import NexusEngine
import asyncio

async def main():
    engine = NexusEngine() 
    
    # Registering Spiders
    from plugins.bilibili_spider import Spider as BiliSpider
    engine.register_spider("bilibili", BiliSpider())

    # Declarative task submission (Platform, Keyword, Params)
    await engine.submit_task("bilibili", "AI4Science", {"page_size": 50, "order": "pubdate"})
    
    await engine.start()

if __name__ == "__main__":
    asyncio.run(main())
```

### 2. SOTA Video Downloading
Guarantees extraction by bypassing broken Python-Conda environments and linking directly to native JS engines:
```python
from video_downloader import sota_download_youtube
sota_download_youtube("https://www.youtube.com/watch?v=...", save_path="data/downloads")
```

### 3. Local Whisper ASR Transcription
```python
from video2text import generate_srt
# Automatically converts video audio to a timestamped .srt file
generate_srt("data/downloads/lecture.mp4", model_tier="base")
```
