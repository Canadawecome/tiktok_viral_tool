import argparse
import sys
import os
import shutil

# Add current folder to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import MIN_DURATION_BETA, GOLDEN_MIN, GOLDEN_MAX
from core.downloader import download_video
from core.audio import extract_and_normalize
from core.transcriber import transcribe_with_words, auto_chunk_lines
from core.renderer import build_viral_video

def parse_time(time_str):
    """Parses seconds (e.g. 148.5) or MM:SS (e.g. 02:28.5) to float seconds."""
    if ':' in time_str:
        parts = time_str.split(':')
        if len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        elif len(parts) == 3:
            return float(parts[0]) * 3600 + float(parts[1]) * 60 + float(parts[2])
    return float(time_str)

def main():
    parser = argparse.ArgumentParser(
        description="TikTok Beta US Viral Video Generator (Creator Rewards Program 60s+)"
    )
    parser.add_argument("--input", required=True, help="Input video file path or YouTube URL")
    parser.add_argument("--start", required=True, help="Start time in seconds or MM:SS (e.g. 148.0)")
    parser.add_argument("--duration", required=True, help="Duration in seconds (e.g. 66.0)")
    parser.add_argument("--output", default="output_tiktok_viral_916.mp4", help="Output video path")
    parser.add_argument("--headline", default="VIRAL MOMENT OF THE HEARING", help="Headline title")
    parser.add_argument("--subheadline", default="", help="Sub-headline title (yellow)")
    parser.add_argument("--quote", default="", help="Hook quote text")
    parser.add_argument("--badge", default="🔴 CAPITOL HILL SHOWDOWN", help="Top badge text")
    parser.add_argument("--footer", default="CONGRESSIONAL OVERSIGHT HEARING • U.S. SENATE", help="Bottom footer")
    parser.add_argument("--model", default="base", help="Whisper model (base, small, medium)")
    
    args = parser.parse_args()
    
    start_time = parse_time(args.start)
    duration = float(args.duration)
    
    # Check TikTok Beta minimum duration rule
    if duration < MIN_DURATION_BETA:
        print(f"\n⚠️  [WARNING]: Duration is {duration:.1f}s (< 60.0s).")
        print("    TikTok Beta / Creator Rewards Program requires videos to be >= 60.0s for monetization!")
        print(f"    Golden range recommended: {GOLDEN_MIN}s - {GOLDEN_MAX}s.\n")
    else:
        print(f"\n✅ [TIKTOK BETA COMPLIANT]: Duration is {duration:.1f}s (>= 60s qualified for RPM $1-$4+).\n")
        
    input_file = args.input
    # Check if input is URL
    if input_file.startswith("http://") or input_file.startswith("https://"):
        downloaded = "temp_downloaded_source.mp4"
        download_video(input_file, downloaded)
        input_file = downloaded
        
    if not os.path.exists(input_file):
        print(f"❌ Error: Input video file not found: {input_file}")
        sys.exit(1)
        
    temp_audio = "temp_normalized_audio.m4a"
    
    try:
        # Step 1: Extract and normalize audio (-14 LUFS)
        extract_and_normalize(input_file, start_time, duration, temp_audio)
        
        # Step 2: Transcribe with Whisper word-level timestamps
        words = transcribe_with_words(temp_audio, model_name=args.model, language='en')
        
        # Step 3: Auto-chunk into punchy 2-4 word lines
        lines = auto_chunk_lines(words, max_words=4, min_words=2)
        
        # Step 4: Render 9:16 vertical video
        build_viral_video(
            input_video=input_file,
            audio_path=temp_audio,
            subtitle_lines=lines,
            output_video=args.output,
            start_time=start_time,
            duration=duration,
            badge_text=args.badge,
            headline_text=args.headline,
            subheadline_text=args.subheadline,
            quote_text=args.quote,
            footer_text=args.footer
        )
        
        print(f"\n🎉 Successfully created viral video: {args.output}")
        print(f"   Duration: {duration:.2f}s | Resolution: 1080x1920 (9:16) | Audio: -14 LUFS")
        
    finally:
        # Cleanup temporary audio
        if os.path.exists(temp_audio):
            os.remove(temp_audio)

if __name__ == "__main__":
    main()
