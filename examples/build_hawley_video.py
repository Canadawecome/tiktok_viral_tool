import sys
import os

# Add tool directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_viral_tool"))

from core.audio import extract_and_normalize
from core.transcriber import transcribe_with_words, auto_chunk_lines
from core.renderer import build_viral_video

INPUT_FILE = "hawley_raw.mp4"
OUTPUT_FILE = "hawley_comedic_talent_72s_beta.mp4"
START_TIME = 1.0
DURATION = 72.0  # 72.0s >= 60.0s (TikTok Beta US Compliant)
TEMP_AUDIO = "hawley_72s_audio.m4a"

def hawley_crop(raw_img, rel_t):
    # Hawley is centered in 640x360 around x=330, y=100
    # A 540x360 crop from x=50 to 590 captures Hawley sharply centered
    return raw_img.crop((50, 0, 590, 360))

def main():
    print("=" * 65)
    print("🎬 RENDERING VIDEO 2: SEN. JOSH HAWLEY VS JACK SMITH (72s)")
    print("=" * 65)
    
    # 1. Normalize audio to -14 LUFS
    extract_and_normalize(INPUT_FILE, START_TIME, DURATION, TEMP_AUDIO)
    
    # 2. Transcribe word-level timestamps with Whisper
    words = transcribe_with_words(TEMP_AUDIO, model_name="base", language="en")
    
    # 3. Chunk into 2-4 punchy words per line
    lines = auto_chunk_lines(words, max_words=4, min_words=2)
    
    # 4. Render 9:16 vertical video
    build_viral_video(
        input_video=INPUT_FILE,
        audio_path=TEMP_AUDIO,
        subtitle_lines=lines,
        output_video=OUTPUT_FILE,
        start_time=START_TIME,
        duration=DURATION,
        badge_text="🔴 SENATE JUDICIARY COMMITTEE",
        headline_text="SEN. HAWLEY CONFRONTS",
        subheadline_text="SPECIAL COUNSEL JACK SMITH",
        quote_text="\"I UNDERESTIMATED YOUR COMEDIC TALENT!\"",
        footer_text="CONGRESSIONAL OVERSIGHT HEARING • U.S. SENATE",
        crop_fn=hawley_crop
    )
    
    if os.path.exists(TEMP_AUDIO):
        os.remove(TEMP_AUDIO)
        
    print("\n✅ Video 2 Completed:", os.path.abspath(OUTPUT_FILE))

if __name__ == "__main__":
    main()
