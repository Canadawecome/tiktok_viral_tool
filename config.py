import os

# Canvas & Layout (9:16 vertical standard)
CANVAS_WIDTH = 1080
CANVAS_HEIGHT = 1920

# Main Video Window (3:2 ratio on 9:16 background)
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 720
VIDEO_Y = 480

# TikTok Beta US Monetization Rules
MIN_DURATION_BETA = 60.0  # TikTok Creator Rewards Program minimum
GOLDEN_MIN = 65.0
GOLDEN_MAX = 80.0

# Subtitle Safe Zone (Y: 1250 to 1750, well above TikTok bottom UI)
SUBTITLE_Y = 1460
MAX_WORDS_PER_LINE = 4
MIN_WORDS_PER_LINE = 2

# Colors (RGB)
COLOR_BG_DARK = (12, 14, 20)
COLOR_TEXT_WHITE = (255, 255, 255)
COLOR_ACTIVE_HIGHLIGHT = (255, 230, 0)  # Neon Yellow (Alex Hormozi / TikTok Style)
COLOR_ACTIVE_GREEN = (0, 255, 102)      # Alternative Neon Green
COLOR_STROKE_BLACK = (0, 0, 0)
COLOR_BADGE_RED = (239, 68, 68)
COLOR_SUBTITLE_MUTED = (200, 210, 230)
COLOR_FOOTER_MUTED = (130, 140, 160)

# Stroke Widths
STROKE_WIDTH_NORMAL = 6
STROKE_WIDTH_ACTIVE = 8

# Fonts Priority (macOS paths with cross-platform fallbacks)
def get_font_path(name):
    macos_paths = {
        'impact': '/System/Library/Fonts/Supplemental/Impact.ttf',
        'arial_black': '/System/Library/Fonts/Supplemental/Arial Black.ttf',
        'helvetica': '/System/Library/Fonts/Helvetica.ttc',
        'arial': '/System/Library/Fonts/Supplemental/Arial.ttf'
    }
    path = macos_paths.get(name.lower())
    if path and os.path.exists(path):
        return path
    return None
