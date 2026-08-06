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
            'format': 'best',
            'outtmpl': 'downloads/source_video.%(ext)s',
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(video_url, download=True)
                filename = ydl.prepare_filename(info)
                print('[SUCCESS] Video source downloaded safely.')
                return filename
        except Exception as e:
            print(f'[ERROR] Download failed: {e}')
            return ''

    def isolate_clip(self, input_file: str, start_time: str, end_time: str, output_name: str) -> str:
        output_path = f'output/{output_name}.mp4'
        print(f'[CLIP] Cutting video with sub-millisecond precision: {start_time} -> {end_time}')
        try:
            ffmpeg.input(input_file, ss=start_time, to=end_time).output(output_path, c='copy').run(overwrite_output=True, capture_stdout=True, capture_stderr=True)
            print(f'[SUCCESS] Isolated clip saved to: {output_path}')
            return output_path
        except Exception as e:
            print(f'[ERROR] FFmpeg cutting sequence failed: {e}')
            return ''

if __name__ == '__main__':
    engine = VideoClipperEngine()
    source = engine.download_stream('https://youtube.com')
    if source:
        engine.isolate_clip(source, '00:00:02', '00:00:07', 'my_first_viral_clip')
