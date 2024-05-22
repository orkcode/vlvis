from PIL import Image
import os
from moviepy.editor import VideoFileClip


def compress_image(image_path, output_path, quality=85):
    with Image.open(image_path) as img:
        img.save(output_path, 'JPEG', quality=quality)

def compress_video(video_path, output_path, target_size_mb=5):
    try:
        clip = VideoFileClip(video_path)
        bitrate = target_size_mb * 1000 * 1000 / clip.duration  # битрейт в битах
        clip.write_videofile(output_path, bitrate=bitrate)
        print(f"Video compressed to: {output_path}")
    except Exception as e:
        print(f"Error compressing video: {e}")