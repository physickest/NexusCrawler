#python c:/Users/EtherEditor/Desktop/TOEFL/scripts/audio/Automatic_Speech_Recognition.py
import whisper
from whisper.utils import get_writer
import os

def generate_srt(video_path: str, output_directory: str = "text", model_tier: str = "base"):
    """
    Transcribes a video file and generates an SRT subtitle file.
    
    Args:
        video_path: Path to the input video file (e.g., .mp4, .mkv, .avi).
        output_directory: Where to save the resulting .srt file.
        model_tier: The Whisper model to use ('tiny', 'base', 'small', 'medium', 'large').
                    Larger models are more accurate but slower.
    """
    if not os.path.exists(video_path):
        print(f"Error: File not found at {video_path}")
        return

    print(f"Loading Whisper model '{model_tier}'...")
    # Loads the model into memory (downloads automatically on first run)
    model = whisper.load_model(model_tier)

    print(f"Processing and transcribing '{video_path}'...")
    # Whisper automatically handles stripping the audio from the video container
    result = model.transcribe(video_path)
    os.makedirs(output_directory, exist_ok=True)

    # Initialize the SRT writer
    srt_writer = get_writer("srt", output_directory)
    
    # Generate and save the file
    srt_writer(result, video_path)
    
    filename = os.path.splitext(os.path.basename(video_path))[0]
    print(f"\nSuccess! Subtitles saved to: {os.path.join(output_directory, filename + '.srt')}")

if __name__ == "__main__":
    # Define the path to your target video file here
    input_video = r"C:\Users\EtherEditor\Desktop\scrape_subtitle\data\downloads\Bandit\【前沿研究课程】第一讲：Introduction to Multi-Armed Bandits.mp4"
    # Execute the function
    generate_srt(input_video, model_tier="base")
