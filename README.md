# TIKTOK BETA US VIRAL VIDEO GENERATOR 🚀
> Công cụ tự động sản xuất video ngắn 9:16 chuẩn thị trường Mỹ (US Audience) để kiếm tiền TikTok Beta / Creator Rewards Program (CRP), YouTube Shorts và Reels.

---

## 🌟 TÍNH NĂNG CHÍNH
1. **Chuẩn kiếm tiền TikTok Beta (Duration $\ge 60$s)**:
   - Tự động cảnh báo nếu video dưới 60s. Khung chuẩn khuyến nghị: 65s - 80s để tối đa hóa RPM (\$1 - \$4+).
2. **Dynamic Alex Hormozi / TikTok Subtitles**:
   - Sử dụng OpenAI Whisper trích xuất mốc thời gian chính xác từng từ (`word_timestamps=True`).
   - Tự động cắt nhịp 2-4 từ/dòng.
   - Hiệu ứng **Word-by-Word Highlight**: Từ đang phát âm sáng màu vàng neon (`#FFE500`) viền đen dày, các từ còn lại màu trắng tuyết.
   - Đặt ở vùng an toàn (Safe Zone) không bị che bởi giao diện TikTok.
3. **Bố cục Single-Camera Card**:
   - Không ép chia đôi màn hình. Khung hình chính 3:2 sắc nét (1080x720) trên nền mờ nghệ thuật.
   - Tự động chuyển góc máy theo người đang nói.
4. **Chuẩn hóa âm lượng EBU R128 (-14 LUFS)**:
   - Tối ưu hóa âm lượng loa điện thoại, chống vỡ tiếng.
5. **Render siêu tốc (Hardware Acceleration)**:
   - Sử dụng `PyAV` kết hợp tăng tốc phần cứng Apple Silicon `h264_videotoolbox` đạt tốc độ 150-180 fps (chỉ mất vài giây cho một video hoàn chỉnh).

---

## 📁 CẤU TRÚC THƯ MỤC
```text
tiktok_viral_tool/
├── main.py              # CLI chính chạy mọi video từ URL hoặc file thô
├── run_schmitt_65s.py   # Script mẫu chạy video 66.5s đạt chuẩn TikTok Beta
├── config.py            # Cấu hình màu sắc, phông chữ, tọa độ canvas
├── requirements.txt     # Danh sách thư viện Python cần thiết
├── README.md            # Tài liệu hướng dẫn sử dụng
└── core/
    ├── audio.py         # Trích xuất và chuẩn hóa âm thanh -14 LUFS
    ├── transcriber.py   # Whisper AI bóc tách từ & auto-chunk phụ đề
    ├── renderer.py      # Engine render video 9:16 siêu tốc
    └── downloader.py    # Tải video chất lượng cao từ YouTube (yt-dlp)
```

---

## 🚀 CÁCH SỬ DỤNG

### 1. Cài đặt thư viện (nếu môi trường mới)
```bash
pip install -r requirements.txt
```

### 2. Chạy nhanh qua CLI (`main.py`)
```bash
python3 tiktok_viral_tool/main.py \
  --input "schmitt_clashes_raw.mp4" \
  --start "02:28.5" \
  --duration 66.5 \
  --badge "🔴 SENATE JUDICIARY COMMITTEE" \
  --headline "SEN. SCHMITT DESTROYS" \
  --subheadline "SPECIAL COUNSEL JACK SMITH" \
  --quote "\"YOU WILL GO DOWN AS A TOTAL DIRTBAG!\"" \
  --output "schmitt_dirtbag_66s.mp4"
```

**Các tham số quan trọng:**
* `--input`: Đường dẫn file video (`.mp4`) hoặc URL YouTube.
* `--start`: Mốc thời gian bắt đầu (giây hoặc `MM:SS`, ví dụ: `148.5` hoặc `02:28.5`).
* `--duration`: Thời lượng video (khuyến nghị $\ge 60$s để đủ điều kiện TikTok Beta).
* `--headline`: Tiêu đề chính trên banner (chữ trắng in hoa).
* `--subheadline`: Tiêu đề phụ (màu vàng neon nổi bật).
* `--quote`: Câu quote giật tít kịch tính.
* `--output`: Tên file video xuất ra.

### 3. Chạy thử nghiệm kịch bản 66.5s mẫu
```bash
python3 tiktok_viral_tool/run_schmitt_65s.py
```
Video xuất ra sẽ có độ dài 66.5s, cắt trọn vẹn màn chất vấn 197 trát hầu tòa cho đến cú chốt hạ *"total dirtbag"* và cận cảnh phản ứng sững sờ của Jack Smith.
