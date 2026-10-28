import sys
import os

# Add root of tool
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.audio import extract_and_normalize
from core.transcriber import transcribe_with_words, auto_chunk_lines
from core.renderer import build_viral_video

INPUT_FILE = "schmitt_clashes_raw.mp4"
OUTPUT_FILE = "schmitt_dirtbag_66s_beta.mp4"

# Check parent directory for source video if not in current folder
if not os.path.exists(INPUT_FILE):
    parent_path = os.path.join(os.path.dirname(__file__), "..", INPUT_FILE)
    if os.path.exists(parent_path):
        INPUT_FILE = parent_path

START_TIME = 148.5
DURATION = 66.5  # 66.5s -> Fully eligible for TikTok Beta US (>= 60s)

TEMP_AUDIO = "schmitt_66s_audio.m4a"

# Smart camera crop function:
# During Schmitt questioning: crop Schmitt (x=100 to 640)
# During Smith answering (approx 8.5s to 30.5s from start) and final reaction (65.2s to end): crop Smith (x=35 to 575)
def schmitt_smith_crop(raw_img, rel_t):
    # From 8.5s to 30.2s: Jack Smith answers about subpoenas & Congressman Perry's phone
    # From 65.2s to end: Jack Smith silent reaction
    if (8.5 <= rel_t <= 30.2) or (rel_t >= 65.2):
        return raw_img.crop((35, 0, 575, 360))
    else:
        return raw_img.crop((100, 0, 640, 360))

def main():
    print("=" * 65)
    print("🎬 PRODUCING 66.5S VIRAL TIKTOK BETA US VIDEO (SCHMITT VS SMITH)")
    print("=" * 65)
    
    # 1. Normalize audio
    extract_and_normalize(INPUT_FILE, START_TIME, DURATION, TEMP_AUDIO)
    
    # 2. Transcribe word-level timestamps
    words = transcribe_with_words(TEMP_AUDIO, model_name="base", language="en")
    
    # 3. Auto chunk into 2-4 punchy words per line
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
        headline_text="SEN. SCHMITT DESTROYS",
        subheadline_text="SPECIAL COUNSEL JACK SMITH",
        quote_text="\"YOU WILL GO DOWN AS A TOTAL DIRTBAG!\"",
        footer_text="CONGRESSIONAL OVERSIGHT HEARING • U.S. SENATE",
        crop_fn=schmitt_smith_crop
    )
    
    if os.path.exists(TEMP_AUDIO):
        os.remove(TEMP_AUDIO)
        
    print("\n✅ Done! File saved at:", os.path.abspath(OUTPUT_FILE))

if __name__ == "__main__":
    main()
