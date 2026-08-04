import streamlit as st
import yt_dlp
import ffmpeg
import os
import glob
import cv2
import numpy as np

# Ensure local FFmpeg folder is registered globally in Python's environment path
ffmpeg_path = r"C:\Users\ADMIN\AppData\Local\ffmpegio\ffmpeg-downloader\ffmpeg\bin"
if ffmpeg_path not in os.environ["PATH"]:
    os.environ["PATH"] += ";" + ffmpeg_path

class UltimateVideoEngine:
    def sanitize_timestamp(self, ts: str) -> str:
        """Fixes common user typo symbols (;, ., -) and converts to accurate HH:MM:SS format."""
        ts = ts.strip().replace(';', ':').replace('.', ':').replace('-', ':')
        parts = ts.split(':')
        padded_parts = [f"{int(p):02d}" if p.isdigit() else "00" for p in parts]
        while len(padded_parts) < 3:
            padded_parts.insert(0, "00")
        return ":".join(padded_parts[:3])

    def get_auto_highlight_timestamps(self, video_info: dict, duration_seconds: int = 15) -> tuple:
        """Parses YouTube's internal crowd engagement analytics to extract the absolute best highlight window."""
        try:
            heatmap = video_info.get('heatmap')
            if not heatmap:
                return None, None
            peak_moment = max(heatmap, key=lambda x: x.get('value', 0))
            peak_seconds = peak_moment.get('start_time', 0)

            start_sec = max(0, int(peak_seconds - 2))
            end_sec = start_sec + duration_seconds

            format_time = lambda s: f"{s//3600:02d}:{(s%3600)//60:02d}:{s%60:02d}"
            return format_time(start_sec), format_time(end_sec)
        except:
            return None, None

    def calculate_face_center(self, temp_source: str) -> float:
        """Applies algorithmic face clustering across frames to pinpoint where the speaker is standing."""
        try:
            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            cap = cv2.VideoCapture(temp_source)
            x_positions = []
            frame_count = 0

            while cap.isOpened() and frame_count < 150:
                ret, frame = cap.read()
                if not ret:
                    break
                if frame_count % 5 == 0:
                    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
                    for (x, y, w, h) in faces:
                        x_positions.append(x + w / 2)
                frame_count += 1
            cap.release()

            if x_positions:
                return float(np.median(x_positions))
            return None
        except:
            return None

    def fast_clip_stream(self, url_input, start_time, end_time, file_name, format_choice, auto_mode, auto_duration, visual_style, brand_overlay_text, viral_caption):
        """Downloads specific streaming windows, applies crops, and wraps formatting outputs."""
        temp_raw = f"downloads/raw_{file_name}.mp4"
        output_path = f"output/{file_name}.mp4"

        # Updated format settings to prevent silent download failures
        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'quiet': True,
            'no_warnings': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url_input, download=False)
                stream_url = info['url']

                if auto_mode:
                    auto_start, auto_end = self.get_auto_highlight_timestamps(info, auto_duration)
                    if auto_start and auto_end:
                        start_time, end_time = auto_start, auto_end
                    else:
                        start_time, end_time = "00:00:00", f"00:00:{auto_duration:02d}"
            except Exception as e:
                return f"ERROR: Network stream resolution failed. {str(e)}", "", ""

        start_time = self.sanitize_timestamp(start_time)
        end_time = self.sanitize_timestamp(end_time)

        try:
            st.text(f"📥 Slicing remote source buffer stream ({start_time} -> {end_time})...")
            (
                ffmpeg
                .input(stream_url, ss=start_time, to=end_time)
                .output(temp_raw, vcodec='libx264', acodec='aac', loglevel="error")
                .run(overwrite_output=True)
            )

            video_meta = ffmpeg.probe(temp_raw)
            video_stream = next((s for s in video_meta['streams'] if s['codec_type'] == 'video'), None)
            orig_w, orig_h = int(video_stream['width']), int(video_stream['height'])
            target_w = int(orig_h * (9 / 16))

            video_input = ffmpeg.input(temp_raw).video
            audio_input = ffmpeg.input(temp_raw).audio

            if format_choice == "AI Smart-Center Face Crop (9:16)":
                st.text("🔍 Running Computer Vision Face-Detection matrix tracker...")
                face_x = self.calculate_face_center(temp_raw)
                crop_x = int(face_x - (target_w / 2)) if face_x is not None else (orig_w - target_w) // 2
                crop_x = max(0, min(crop_x, orig_w - target_w))
                video_input = video_input.filter('crop', target_w, orig_h, crop_x, 0)
            elif format_choice == "Standard Vertical Center Crop (9:16)":
                video_input = video_input.filter('crop', target_w, orig_h, '(iw-ow)/2', 0)

            if visual_style == "Cinematic Color Grade":
                video_input = video_input.filter('eq', contrast=1.15, saturation=1.1, brightness=0.03)
            elif visual_style == "Sharp Contrast Boost":
                video_input = video_input.filter('eq', contrast=1.3, saturation=1.05, brightness=0.02)
            elif visual_style == "Viral Glow Pop":
                video_input = video_input.filter('eq', contrast=1.2, saturation=1.2, brightness=0.04)

            if brand_overlay_text:
                video_input = video_input.filter(
                    'drawtext',
                    text=brand_overlay_text,
                    font='Arial',
                    fontsize=28,
                    fontcolor='white',
                    box=1,
                    boxcolor='black@0.5',
                    x='(w-text_w)-20',
                    y='h-60'
                )

            st.text("⚙️ Compiling final HD video wrapper fields...")
            (
                ffmpeg
                .output(video_input, audio_input, output_path, vcodec='libx264', crf=18, acodec='aac', audio_bitrate='320k', loglevel="error")
                .run(overwrite_output=True)
            )

            if os.path.exists(temp_raw):
                os.remove(temp_raw)
            return output_path, start_time, end_time

        except Exception as e:
            if os.path.exists(temp_raw):
                os.remove(temp_raw)
            return f"ERROR: {str(e)}", "", ""

    def clear_cache_folders(self):
        """Cleans temporary download files automatically."""
        for pattern in ['*.part', '*.ytdl', '*.tmp', 'downloads/raw_*.mp4']:
            for file in glob.glob(pattern):
                try:
                    os.remove(file)
                except:
                    pass

# --- STREAMLIT WEB APP MASTER INTERFACE ---
st.set_page_config(page_title="Ultimate AI Video Clipper Studio PRO", layout="centered")
st.title("🎬 Ultimate AI Video Clipper Studio PRO")
st.markdown("Automated high-definition viral clip generation, smart tracking crops, and live browser previews.")

if not os.path.exists("output"):
    os.makedirs("output")
if not os.path.exists("downloads"):
    os.makedirs("downloads")

engine = UltimateVideoEngine()
engine.clear_cache_folders()

url_input = st.text_input("YouTube Link / Live Stream URL", placeholder="https://youtube.com...")

st.markdown("### 🤖 Extraction Configuration")
auto_mode = st.toggle("✨ Auto-Detect Best Viral Peak (Crowd-Engagement Heatmap Mode)", value=False)

start_time, end_time, auto_duration = "00:00:02", "00:00:17", 15
if auto_mode:
    auto_duration = st.slider("Target Output Clip Duration (Seconds)", min_value=5, max_value=60, value=15, step=5)
else:
    col1, col2 = st.columns(2)
    with col1:
        start_time = st.text_input("Start Timestamp", value="00:01:00")
    with col2:
        end_time = st.text_input("End Timestamp", value="00:01:15")

st.markdown("### �️ AI Editing & Visuals")
visual_col1, visual_col2 = st.columns(2)
with visual_col1:
    visual_style = st.selectbox(
        "Visual Style Preset",
        ["None", "Cinematic Color Grade", "Sharp Contrast Boost", "Viral Glow Pop"]
    )
    brand_overlay_text = st.text_input("Brand Overlay Text", value="My Channel")
with visual_col2:
    viral_caption = st.text_input("Viral Caption / Hook", value="#ViralClip #AIEdit")
    brand_tagline = st.text_input("Brand Tagline", value="Built for shareable short-form stories")

st.markdown("### �📐 Layout & File Management")
col3, col4 = st.columns(2)
with col3:
    file_name = st.text_input("Output File Name", value="viral_clip")
with col4:
    format_choice = st.selectbox(
        "Aspect Ratio Layout Format",
        ["AI Smart-Center Face Crop (9:16)", "Standard Vertical Center Crop (9:16)", "Original Aspect Ratio (Landscape)"]
    )

if st.button("🚀 Generate Viral Video Clip", type="primary"):
    if not url_input:
        st.error("Please enter a valid YouTube video URL first.")
    else:
        with st.spinner("Processing stream pipeline... Please wait."):
            engine.clear_cache_folders()
            out_file, final_start, final_end = engine.fast_clip_stream(
                url_input, start_time, end_time, file_name, format_choice, auto_mode, auto_duration
            )

            if "ERROR" in out_file:
                st.error(out_file)
            else:
                st.success(f"🎉 Success! Clip extracted between {final_start} and {final_end}")
                if os.path.exists(out_file):
                    with open(out_file, 'rb') as vf:
                        st.video(vf.read())
                    with open(out_file, "rb") as file:
                        st.download_button(
                            label="💾 Download Processed Video Clip",
                            data=file,
                            file_name=f"{file_name}.mp4",
                            mime="video/mp4"
                        )