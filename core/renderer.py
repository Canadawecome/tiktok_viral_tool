import os
import sys
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import av

from config import (
    CANVAS_WIDTH, CANVAS_HEIGHT,
    VIDEO_WIDTH, VIDEO_HEIGHT, VIDEO_Y,
    COLOR_BG_DARK, COLOR_TEXT_WHITE, COLOR_ACTIVE_HIGHLIGHT,
    COLOR_STROKE_BLACK, COLOR_BADGE_RED, COLOR_SUBTITLE_MUTED, COLOR_FOOTER_MUTED,
    STROKE_WIDTH_NORMAL, STROKE_WIDTH_ACTIVE, SUBTITLE_Y,
    get_font_path
)

def render_dynamic_subtitle(draw, line_info, current_t, font, space_w, y_center=SUBTITLE_Y):
    words_data = line_info["words"]
    words = [w["word"] for w in words_data]
    
    # Calculate word widths
    word_widths = [font.getbbox(w)[2] - font.getbbox(w)[0] for w in words]
    total_w = sum(word_widths) + space_w * (len(words) - 1)
    cur_x = (CANVAS_WIDTH - total_w) / 2
    
    # Determine active word index
    active_idx = -1
    for i, w in enumerate(words_data):
        if w["start"] <= current_t <= w["end"]:
            active_idx = i
            break
    # Bridge small gaps between words to prevent flicker
    if active_idx == -1:
        for i in range(len(words_data) - 1):
            if words_data[i]["end"] <= current_t <= words_data[i+1]["start"]:
                active_idx = i
                break
                
    for i, w in enumerate(words_data):
        is_active = (i == active_idx)
        color = COLOR_ACTIVE_HIGHLIGHT if is_active else COLOR_TEXT_WHITE
        stroke = STROKE_WIDTH_ACTIVE if is_active else STROKE_WIDTH_NORMAL
        draw.text(
            (cur_x, y_center), w["word"],
            fill=color, font=font, anchor="lm",
            stroke_width=stroke, stroke_fill=COLOR_STROKE_BLACK
        )
        cur_x += word_widths[i] + space_w

def build_viral_video(
    input_video,
    audio_path,
    subtitle_lines,
    output_video,
    start_time,
    duration,
    badge_text="🔴 BREAKING NEWS",
    headline_text="TITLE OF THE HOOK",
    subheadline_text="",
    quote_text="",
    footer_text="CONGRESSIONAL OVERSIGHT HEARING • U.S. SENATE",
    crop_fn=None
):
    print(f"[Renderer] Initializing render pipeline for {output_video}...")
    
    # Load fonts
    font_impact = get_font_path('impact') or get_font_path('arial_black')
    font_helvetica = get_font_path('helvetica') or get_font_path('arial')
    
    font_badge = ImageFont.truetype(font_impact, 38)
    font_title = ImageFont.truetype(font_impact, 54)
    font_sub = ImageFont.truetype(font_helvetica, 28)
    font_cap = ImageFont.truetype(font_impact, 72)
    space_w = font_cap.getbbox(' ')[2] - font_cap.getbbox(' ')[0]
    
    # Open input stream
    container = av.open(input_video)
    v_stream = container.streams.video[0]
    v_stream.thread_type = "AUTO"
    fps = float(v_stream.average_rate or 24.0)
    
    # Seek to start
    pts_start = int(start_time / v_stream.time_base)
    container.seek(pts_start, stream=v_stream)
    
    # Grab first frame for blurred background
    first_frame = None
    for f in container.decode(v_stream):
        first_frame = f.to_image()
        break
    if not first_frame:
        first_frame = Image.new('RGB', (640, 360), (20, 20, 20))
        
    # Pre-render base background
    bg_ref = first_frame.resize((CANVAS_WIDTH, CANVAS_HEIGHT)).filter(ImageFilter.GaussianBlur(radius=40))
    dark_overlay = Image.new('RGB', (CANVAS_WIDTH, CANVAS_HEIGHT), COLOR_BG_DARK)
    base_bg = Image.blend(bg_ref, dark_overlay, 0.78)
    
    draw_base = ImageDraw.Draw(base_bg)
    # 1. Top Badge
    draw_base.text((CANVAS_WIDTH // 2, 130), badge_text, fill=COLOR_BADGE_RED, font=font_badge, anchor='mm')
    # 2. Headline
    draw_base.text((CANVAS_WIDTH // 2, 230), headline_text, fill=COLOR_TEXT_WHITE, font=font_title, anchor='mm')
    if subheadline_text:
        draw_base.text((CANVAS_WIDTH // 2, 305), subheadline_text, fill=COLOR_ACTIVE_HIGHLIGHT, font=font_title, anchor='mm')
    if quote_text:
        draw_base.text((CANVAS_WIDTH // 2, 380), quote_text, fill=COLOR_SUBTITLE_MUTED, font=font_sub, anchor='mm')
        
    # 3. Video border accent lines
    draw_base.line([(0, VIDEO_Y), (CANVAS_WIDTH, VIDEO_Y)], fill=COLOR_BADGE_RED, width=3)
    draw_base.line([(0, VIDEO_Y + VIDEO_HEIGHT), (CANVAS_WIDTH, VIDEO_Y + VIDEO_HEIGHT)], fill=COLOR_BADGE_RED, width=3)
    
    # 4. Footer
    if footer_text:
        draw_base.text((CANVAS_WIDTH // 2, 1800), footer_text, fill=COLOR_FOOTER_MUTED, font=font_sub, anchor='mm')
        
    # Re-seek to start for decoding
    container.seek(pts_start, stream=v_stream)
    
    # Choose encoder: h264_videotoolbox (Apple Silicon) or libx264
    codec = 'h264_videotoolbox' if sys.platform == 'darwin' else 'libx264'
    
    ffmpeg_cmd = [
        'ffmpeg', '-y',
        '-f', 'rawvideo',
        '-vcodec', 'rawvideo',
        '-s', f'{CANVAS_WIDTH}x{CANVAS_HEIGHT}',
        '-pix_fmt', 'rgb24',
        '-r', str(fps),
        '-i', '-',
        '-i', audio_path,
        '-c:v', codec,
        '-b:v', '6500k',
        '-c:a', 'copy',
        '-shortest',
        output_video
    ]
    
    print(f"[Renderer] Launching FFmpeg encoder ({codec}) at {fps:.2f} fps...")
    proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)
    
    frame_count = 0
    total_frames = int(duration * fps)
    
    for frame in container.decode(v_stream):
        pts_sec = float(frame.pts * v_stream.time_base)
        rel_t = pts_sec - start_time
        
        if rel_t < 0:
            continue
        if rel_t > duration:
            break
            
        raw_img = frame.to_image()
        
        # Crop logic
        if crop_fn:
            cropped = crop_fn(raw_img, rel_t)
        else:
            # Default center crop to 3:2
            src_w, src_h = raw_img.size
            crop_w = int(src_h * (VIDEO_WIDTH / VIDEO_HEIGHT))
            crop_x = max(0, (src_w - crop_w) // 2)
            cropped = raw_img.crop((crop_x, 0, crop_x + crop_w, src_h))
            
        vid_resized = cropped.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.Resampling.BILINEAR)
        
        # Composite frame
        cur_frame = base_bg.copy()
        cur_frame.paste(vid_resized, (0, VIDEO_Y))
        
        # Draw subtitles
        draw_f = ImageDraw.Draw(cur_frame)
        for line in subtitle_lines:
            if line["start"] <= rel_t <= line["end"]:
                render_dynamic_subtitle(draw_f, line, rel_t, font_cap, space_w)
                break
                
        proc.stdin.write(cur_frame.tobytes())
        frame_count += 1
        
        if frame_count % 120 == 0:
            print(f"[Renderer] Rendered {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")
            
    proc.stdin.close()
    proc.wait()
    print(f"[Renderer] Video successfully generated: {output_video}")
    return output_video
