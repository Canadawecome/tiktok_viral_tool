import sys
import os

# Add tool directory to path
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_viral_tool"))

from core.audio import extract_and_normalize
from core.transcriber import transcribe_with_words, auto_chunk_lines
from core.renderer import build_viral_video

INPUT_FILE = "kennedy_raw.mp4"
OUTPUT_FILE = "kennedy_throwup_68s_beta.mp4"
START_TIME = 563.0
DURATION = 68.0  # 68.0s >= 60.0s (TikTok Beta US Compliant)
TEMP_AUDIO = "kennedy_68s_audio.m4a"

def kennedy_crop(raw_img, rel_t):
    # Dynamic crop: Kennedy is on right (x=460), Smith is in center (x=350)
    arr_mean = sum(raw_img.convert('L').getdata()) / (raw_img.width * raw_img.height)
    if arr_mean > 68.0:
        # Kennedy shot
        return raw_img.crop((100, 0, 640, 360))
    else:
        # Smith shot
        return raw_img.crop((60, 0, 600, 360))

def main():
    print("=" * 65)
    print("🎬 RENDERING VIDEO 1: SEN. KENNEDY VS JACK SMITH (68s)")
    print("=" * 65)
    
    # 1. Normalize audio to -14 LUFS
    extract_and_normalize(INPUT_FILE, START_TIME, DURATION, TEMP_AUDIO)
    
    # 2. Transcribe word-level timestamps with Whisper
    words = transcribe_with_words(TEMP_AUDIO, model_name="base", language="en")
    
    # Fix key words if needed
    for w in words:
        if "CONLAW" in w["word"] or "CON LAW" in w["word"]:
            w["word"] = "CON-LAW"
        if "FEVEL" in w["word"] or "BUSTERS" in w["word"]:
            w["word"] = "FILIBUSTER"
            
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
        headline_text="SEN. KENNEDY ROASTS",
        subheadline_text="SPECIAL COUNSEL JACK SMITH",
        quote_text="\"YOU MAKE ME WANT TO THROW UP IN MY MOUTH!\"",
        footer_text="CONGRESSIONAL OVERSIGHT HEARING • U.S. SENATE",
        crop_fn=kennedy_crop
    )
    
    if os.path.exists(TEMP_AUDIO):
        os.remove(TEMP_AUDIO)
        
    print("\n✅ Video 1 Completed:", os.path.abspath(OUTPUT_FILE))

if __name__ == "__main__":
    main()
