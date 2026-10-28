import subprocess
import os

def download_video(url, output_path="downloaded_source.mp4"):
    """
    Downloads the highest quality 1080p/720p video with audio using yt-dlp.
    """
    print(f"[Downloader] Downloading {url} via yt-dlp...")
    cmd = [
        'yt-dlp',
        '-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '--merge-output-format', 'mp4',
        '-o', output_path,
        url
    ]
    res = subprocess.run(cmd)
    if res.returncode != 0:
        raise RuntimeError("yt-dlp download failed. Ensure valid URL or cookies.")
    print(f"[Downloader] Downloaded to {output_path}")
    return output_path
