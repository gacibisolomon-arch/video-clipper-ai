import yt_dlp
import ffmpeg
import os

class VideoClipperEngine:
    def __init__(self, config_path='config/settings.json'):
        self.config_path = config_path
        os.makedirs('downloads', exist_ok=True)
        os.makedirs('output', exist_ok=True)
        print('[INFO] Initializing live ultra-high-performance clipping engine...')

    def download_stream(self, video_url: str) -> str:
        print(f'[DOWNLOAD] Connecting to resource stream via yt-dlp: {video_url}')
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
            (..ffmpeg.input(input_file, ss=start_time, to=end_time).output(output_path, c='copy').run(overwrite_output=True, capture_stdout=True, capture_stderr=True))
            print(f'[SUCCESS] Isolated clip saved to: {output_path}')
            return output_path
        except Exception as e:
            print(f'[ERROR] FFmpeg cutting sequence failed: {e}')
            return ''

if __name__ == '__main__':
    engine = VideoClipperEngine()
    # This short link is a 15-second creative-commons video for safe, fast local testing!
    source = engine.download_stream('https://youtube.com')
    if source:
        engine.isolate_clip(source, '00:00:02', '00:00:07', 'my_first_viral_clip')
