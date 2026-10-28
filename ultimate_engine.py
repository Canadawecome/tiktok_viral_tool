import sys
import os
import subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import av

# Configuration
INPUT_VIDEO = "kennedy_raw.mp4"
AUDIO_FILE = "kennedy_ultimate_audio.m4a"
OUTPUT_VIDEO = "kennedy_ultimate_viral_showcase.mp4"

START_TIME = 563.0
DURATION = 68.0  # 68s (TikTok Beta US Compliant)

CANVAS_W, CANVAS_H = 1080, 1920
VID_W, VID_H = 1080, 720
VID_Y = 480
FPS = 24000 / 1001

# Fonts
font_impact = '/System/Library/Fonts/Supplemental/Impact.ttf'
font_helv = '/System/Library/Fonts/Helvetica.ttc'

f_badge = ImageFont.truetype(font_impact, 36)
f_curiosity = ImageFont.truetype(font_impact, 26)
f_title = ImageFont.truetype(font_impact, 54)
f_sub = ImageFont.truetype(font_helv, 28)
f_cap = ImageFont.truetype(font_impact, 70)
f_cap_pop = ImageFont.truetype(font_impact, 84) # 120% pop!
f_card_tag = ImageFont.truetype(font_impact, 20)
f_card_title = ImageFont.truetype(font_impact, 28)
f_card_sub = ImageFont.truetype(font_helv, 22)

SPACE_W = f_cap.getbbox(' ')[2] - f_cap.getbbox(' ')[0]

# Subtitle words & timing from Whisper transcription
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "tiktok_viral_tool"))
from core.transcriber import transcribe_with_words, auto_chunk_lines

print("[Ultimate Showcase] Extracting word timestamps from audio...")
words = transcribe_with_words(AUDIO_FILE, model_name="base", language="en")

for w in words:
    if "CONLAW" in w["word"] or "CON LAW" in w["word"]:
        w["word"] = "CON-LAW"
    if "FEVEL" in w["word"] or "BUSTERS" in w["word"]:
        w["word"] = "FILIBUSTER"

lines = auto_chunk_lines(words, max_words=4, min_words=2)

# Red Accent Trigger Words (Emotionally charged legal/political blows)
TRIGGER_WORDS = {
    "VIOLATED", "VIOLATES", "DISCLOSE", "UNBIASED", "FEELINGS",
    "THROW", "MOUTH", "FILIBUSTER", "INFAMOUS", "FRISBEE", "CATALOG", "BAMBI"
}

# Floating Evidence Cards: (start_t, end_t, tag, title, subtitle)
EVIDENCE_CARDS = [
    (4.5, 11.5, "CITATION", "HARVARD LAW SCHOOL", "\"Playing Frisbee in the quad?\""),
    (31.0, 39.0, "EVIDENCE", "J.CREW CATALOG", "\"Violates Speech & Debate Clause\""),
    (58.5, 64.5, "KNOCKOUT", "FINAL VERDICT", "\"You make me want to throw up\"")
]

# Dynamic Zoom Schedule: (start_t, end_t, zoom_scale)
ZOOM_SCHEDULE = [
    (4.0, 12.0, 1.10),   # Frisbee at Harvard
    (31.0, 40.0, 1.10),  # J.Crew catalog
    (58.0, 64.5, 1.15)   # Throw up in my mouth
]

def get_zoom_factor(rel_t):
    for z_start, z_end, z_scale in ZOOM_SCHEDULE:
        if z_start <= rel_t <= z_end:
            return z_scale
    return 1.0

def render_dynamic_subtitle(draw, line_info, current_t, y_center=1460):
    words_data = line_info["words"]
    
    # Active word index
    active_idx = -1
    for i, w in enumerate(words_data):
        if w["start"] <= current_t <= w["end"]:
            active_idx = i
            break
    if active_idx == -1:
        for i in range(len(words_data) - 1):
            if words_data[i]["end"] <= current_t <= words_data[i+1]["start"]:
                active_idx = i
                break
                
    # Calculate widths
    rendered_items = []
    total_w = 0
    for i, w_data in enumerate(words_data):
        w_text = w_data["word"]
        is_active = (i == active_idx)
        font = f_cap_pop if is_active else f_cap
        
        box = font.getbbox(w_text)
        w_len = box[2] - box[0]
        
        rendered_items.append({
            "word": w_text,
            "font": font,
            "is_active": is_active,
            "w_len": w_len
        })
        total_w += w_len
        
    total_w += SPACE_W * (len(rendered_items) - 1)
    cur_x = (CANVAS_W - total_w) / 2
    
    for item in rendered_items:
        clean_key = item["word"].strip(".,!?:;\"'")
        is_trigger = clean_key in TRIGGER_WORDS
        
        if item["is_active"]:
            color = (255, 51, 68) if is_trigger else (255, 230, 0)
            stroke = 9
            y_pos = y_center - 4  # subtle pop elevation
        else:
            color = (255, 255, 255)
            stroke = 6
            y_pos = y_center
            
        draw.text(
            (cur_x, y_pos), item["word"],
            fill=color, font=item["font"], anchor="lm",
            stroke_width=stroke, stroke_fill=(0, 0, 0)
        )
        cur_x += item["w_len"] + SPACE_W

# Precompute Base Background
container = av.open(INPUT_VIDEO)
v_stream = container.streams.video[0]
v_stream.thread_type = "AUTO"

pts_start = int(START_TIME / v_stream.time_base)
container.seek(pts_start, stream=v_stream)

first_frame = None
for f in container.decode(v_stream):
    first_frame = f.to_image()
    break

bg_ref = first_frame.resize((CANVAS_W, CANVAS_H)).filter(ImageFilter.GaussianBlur(radius=45))
dark_overlay = Image.new('RGB', (CANVAS_W, CANVAS_H), (8, 10, 15))
base_bg = Image.blend(bg_ref, dark_overlay, 0.78)

draw_base = ImageDraw.Draw(base_bg)

# 1. Top Live Indicator (drawn with geometric red circle + clean text)
dot_x, dot_y = 230, 95
draw_base.ellipse((dot_x - 12, dot_y - 12, dot_x + 12, dot_y + 12), fill=(239, 68, 68))
draw_base.text((dot_x + 25, dot_y), 'SENATE JUDICIARY COMMITTEE', fill=(239, 68, 68), font=f_badge, anchor='lm')

# 2. Curiosity Pill with golden neon glow
pill_box = (180, 140, 900, 185)
draw_base.rounded_rectangle(pill_box, radius=16, fill=(28, 33, 46), outline=(255, 230, 0), width=2)
draw_base.text((540, 162), 'WATCH JACK SMITH\'S REACTION AT THE END', fill=(255, 230, 0), font=f_curiosity, anchor='mm')

# 3. Main Headlines
draw_base.text((540, 245), 'SEN. KENNEDY ROASTS', fill=(255, 255, 255), font=f_title, anchor='mm')
draw_base.text((540, 315), 'SPECIAL COUNSEL JACK SMITH', fill=(255, 230, 0), font=f_title, anchor='mm')
draw_base.text((540, 385), '\"WERE YOU PLAYING FRISBEE AT HARVARD LAW?\"', fill=(200, 215, 235), font=f_sub, anchor='mm')

# 4. Video Divider lines
draw_base.line([(0, VID_Y), (CANVAS_W, VID_Y)], fill=(239, 68, 68), width=3)

# 5. Footer
draw_base.text((540, 1820), 'CONGRESSIONAL OVERSIGHT HEARING • U.S. SENATE', fill=(140, 150, 170), font=f_sub, anchor='mm')

# Re-seek to start
container.seek(pts_start, stream=v_stream)

ffmpeg_cmd = [
    'ffmpeg', '-y',
    '-f', 'rawvideo',
    '-vcodec', 'rawvideo',
    '-s', f'{CANVAS_W}x{CANVAS_H}',
    '-pix_fmt', 'rgb24',
    '-r', str(FPS),
    '-i', '-',
    '-i', AUDIO_FILE,
    '-c:v', 'h264_videotoolbox',
    '-b:v', '6500k',
    '-c:a', 'copy',
    '-shortest',
    OUTPUT_VIDEO
]

print(f"[Ultimate Showcase] Launching FFmpeg encoder at {FPS:.3f} fps...")
proc = subprocess.Popen(ffmpeg_cmd, stdin=subprocess.PIPE)

frame_count = 0
total_frames = int(DURATION * FPS)

for frame in container.decode(v_stream):
    pts_sec = float(frame.pts * v_stream.time_base)
    rel_t = pts_sec - START_TIME
    
    if rel_t < 0:
        continue
    if rel_t > DURATION:
        break
        
    raw_img = frame.to_image()
    
    # Speaker Cut Detection
    arr = np.array(raw_img)
    mean_b = arr.mean()
    center_x = 450 if mean_b > 68.0 else 350
    
    # Dynamic Zoom
    zoom = get_zoom_factor(rel_t)
    crop_w = int(540 / zoom)
    crop_h = int(360 / zoom)
    
    x1 = max(0, min(640 - crop_w, center_x - crop_w // 2))
    y1 = max(0, min(360 - crop_h, 180 - crop_h // 2))
    
    cropped = raw_img.crop((x1, y1, x1 + crop_w, y1 + crop_h))
    vid_resized = cropped.resize((VID_W, VID_H), Image.Resampling.BILINEAR)
    
    # Composite frame
    cur_frame = base_bg.copy()
    cur_frame.paste(vid_resized, (0, VID_Y))
    draw_f = ImageDraw.Draw(cur_frame)
    
    # Floating Evidence Card (Zero tofu, high broadcast quality)
    for c_start, c_end, tag, title, subtitle in EVIDENCE_CARDS:
        if c_start <= rel_t <= c_end:
            card_box = (670, 505, 1050, 615)
            draw_f.rounded_rectangle(card_box, radius=14, fill=(16, 20, 30), outline=(239, 68, 68), width=3)
            # Red accent pill tag
            draw_f.rounded_rectangle((700, 520, 810, 544), radius=6, fill=(239, 68, 68))
            draw_f.text((755, 532), tag, fill=(255, 255, 255), font=f_card_tag, anchor='mm')
            
            draw_f.text((865, 560), title, fill=(255, 255, 255), font=f_card_title, anchor='mm')
            draw_f.text((865, 592), subtitle, fill=(255, 230, 0), font=f_card_sub, anchor='mm')
            break
            
    # Real-Time Neon Progress Bar at Y=1200
    prog_ratio = min(1.0, max(0.0, rel_t / DURATION))
    prog_w = int(CANVAS_W * prog_ratio)
    draw_f.line([(0, 1200), (CANVAS_W, 1200)], fill=(35, 40, 55), width=5)
    if prog_w > 0:
        draw_f.line([(0, 1200), (prog_w, 1200)], fill=(255, 230, 0), width=5)
        # Leading glow dot
        draw_f.ellipse((prog_w - 6, 1200 - 6, prog_w + 6, 1200 + 6), fill=(255, 255, 255))
        
    # Dynamic Alex Hormozi Subtitles with Pop Bounce
    for line in lines:
        if line["start"] <= rel_t <= line["end"]:
            render_dynamic_subtitle(draw_f, line, rel_t, y_center=1460)
            break
            
    proc.stdin.write(cur_frame.tobytes())
    frame_count += 1
    
    if frame_count % 150 == 0:
        print(f"[Ultimate Showcase] Rendered {frame_count}/{total_frames} frames ({frame_count/total_frames*100:.1f}%)")

proc.stdin.close()
proc.wait()
print(f"\n🎉 Ultimate Showcase Video Completed (Zero Tofu): {OUTPUT_VIDEO}")
