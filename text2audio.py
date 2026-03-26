"""

1. Random Voice with High Volume (Best for simulation):
# Filename contains spaces; quoting is NOT required thanks to updated parser.
python text2audio.py Early Hominid Diets and the Function of Stone Tools.txt -R -vol "+100%"

# or with quotes (still works):
# python text2audio.py "From Invisibility to Record_Women in American History.txt" -R -vol "+100%"

2. Speed Training (Random Voice + Fast):
python text2audio.py article.txt -R -r "+20%" 

3. Specific Voice Override:  
python text2audio.py article.txt -v "en-GB-RyanNeural"

"""

# TOEFL-Relevant Voice Distribution
# Mix of Academic (Formal) and Conversational (Student) tones across accents.
VOICE_POOL = [
    "en-US-ChristopherNeural", # US Male (Standard/Formal)
    "en-US-AriaNeural",        # US Female (Standard/Formal)
    "en-US-GuyNeural",         # US Male (Casual/Student)
    "en-US-JennyNeural",       # US Female (Casual/Student)
    "en-GB-RyanNeural",        # UK Male (Academic)
    "en-GB-SoniaNeural",       # UK Female (Academic)
    "en-AU-WilliamNeural",     # AU Male (Occasional TOEFL accent)
]

DEFAULT_RATE = "+0%"
DEFAULT_VOL = "10%" # Slight boost by default


import asyncio
import edge_tts
import argparse
import random
import sys
from pathlib import Path

async def text_to_speech(input_path: Path, output_path: Path, voice: str, rate: str, volume: str):
    try:
        # 1. Validation & Read
        if not input_path.exists():
            raise FileNotFoundError(f"Input file not found: {input_path}")
        
        with open(input_path, "r", encoding="utf-8") as f:
            text_content = f.read().strip()
            
        if not text_content:
            raise ValueError("Input file is empty.")

        # 2. Synthesis
        print(f"--- Configuration ---")
        print(f"Input:  {input_path.name}")
        print(f"Voice:  {voice}")
        print(f"Rate:   {rate}")
        print(f"Volume: {volume}")
        print(f"---------------------")
        
        communicate = edge_tts.Communicate(text_content, voice, rate=rate, volume=volume)
        await communicate.save(str(output_path))
        print(f"Success: Saved to {output_path}")

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="TOEFL TTS Generator: Random Voices & Volume Boost")
    
    # Path Arguments
    # accept one or more path components so users don't need to quote filenames with spaces
    parser.add_argument("input_file", type=Path, nargs="+", help="Path to source .txt file (can include spaces without quoting)")
    parser.add_argument("-o", "--output", type=Path, help="Output path (default: input_name.mp3)")
    
    # Audio Parameters
    group = parser.add_mutually_exclusive_group()
    group.add_argument("-v", "--voice", type=str, default=VOICE_POOL[0], help="Specific Edge-TTS voice ID")
    group.add_argument("-R", "--random", action="store_true", help="Select a random voice from the TOEFL pool")
    
    parser.add_argument("-r", "--rate", type=str, default=DEFAULT_RATE, help="Speech rate (e.g., '+10%', '-5%')")
    parser.add_argument("-vol", "--volume", type=str, default=DEFAULT_VOL, help="Volume adjustment (e.g., '+20%', '-10%')")

    args = parser.parse_args()

    # Fix for paths containing spaces: argparse with nargs="+" returns a list
    if isinstance(args.input_file, list):
        args.input_file = Path(" ".join(str(p) for p in args.input_file))

    # Logic: Handle Random Voice Selection
    selected_voice = args.voice
    if args.random:
        selected_voice = random.choice(VOICE_POOL)

    # Logic: Default Output Path
    if not args.output:
        # Appends voice name to filename for easy identification during batch review
        clean_voice_name = selected_voice.split('-')[2].replace('Neural', '')
        args.output = args.input_file.parent / f"{args.input_file.stem}_{clean_voice_name}.mp3"

    asyncio.run(text_to_speech(args.input_file, args.output, selected_voice, args.rate, args.volume))
