import subprocess
import os

def extract_and_normalize(input_video, start_time, duration, output_audio_path):
    """
    Extracts audio segment and normalizes to -14 LUFS (EBU R128 international standard
    for US TikTok, YouTube Shorts, and Instagram Reels).
    """
    print(f"[Audio] Extracting and normalizing audio ({duration:.2f}s) to -14 LUFS...")
    cmd = [
        'ffmpeg', '-y',
        '-ss', str(start_time),
        '-t', str(duration),
        '-i', input_video,
        '-vn',
        '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11',
        '-c:a', 'aac',
        '-b:a', '192k',
        output_audio_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    if res.returncode != 0:
        raise RuntimeError(f"FFmpeg audio extraction failed: {res.stderr}")
    print(f"[Audio] Normalized audio saved to {output_audio_path}")
    return output_audio_path
