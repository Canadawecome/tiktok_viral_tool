import whisper
import json
import re

def transcribe_with_words(audio_path, model_name='base', language='en'):
    """
    Transcribes audio using Whisper with word-level timestamps.
    """
    print(f"[Transcriber] Loading Whisper model '{model_name}'...")
    model = whisper.load_model(model_name)
    print(f"[Transcriber] Transcribing {audio_path} (language={language})...")
    res = model.transcribe(audio_path, language=language, word_timestamps=True)
    
    words = []
    for seg in res.get('segments', []):
        for w in seg.get('words', []):
            clean_word = w['word'].strip()
            if clean_word:
                words.append({
                    'word': clean_word.upper(),
                    'start': round(w['start'], 3),
                    'end': round(w['end'], 3)
                })
    print(f"[Transcriber] Transcribed {len(words)} words.")
    return words

def auto_chunk_lines(words, max_words=4, min_words=2, max_pause=0.6):
    """
    Groups words into punchy subtitle lines (2-4 words per line)
    designed for high-retention fast reading on TikTok.
    Splits early on sentence-ending punctuation or audible pauses.
    """
    lines = []
    current_line = []
    
    for i, w in enumerate(words):
        current_line.append(w)
        
        # Check reasons to break current line:
        # 1. Punctuation (. ! ?)
        has_punctuation = any(w['word'].endswith(p) for p in ['.', '!', '?', ';', ':'])
        # 2. Reached max words
        reached_max = (len(current_line) >= max_words)
        # 3. Audible pause before next word
        long_pause = False
        if i < len(words) - 1:
            pause_duration = words[i+1]['start'] - w['end']
            if pause_duration >= max_pause and len(current_line) >= min_words:
                long_pause = True
                
        if (has_punctuation and len(current_line) >= min_words) or reached_max or long_pause:
            lines.append({
                'start': current_line[0]['start'],
                'end': current_line[-1]['end'],
                'words': current_line
            })
            current_line = []
            
    if current_line:
        lines.append({
            'start': current_line[0]['start'],
            'end': current_line[-1]['end'],
            'words': current_line
        })
        
    print(f"[Transcriber] Auto-chunked into {len(lines)} subtitle lines.")
    return lines
