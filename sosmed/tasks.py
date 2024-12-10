from celery import shared_task
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.core.files.storage import default_storage
import os
from PIL import Image
from io import BytesIO
from django.core.files.base import ContentFile
import logging

# Setup logging for better error tracking
logger = logging.getLogger(__name__)


@shared_task
def resize_video_task(video_path, output_dir, output_filename, width=640, bitrate="500k", fps=24):
    input_path = os.path.join(default_storage.location, video_path)
    output_path = os.path.join(default_storage.location, output_dir, output_filename)

    # Ensure the input video exists
    if not os.path.exists(input_path):
        logger.error(f"Input video file does not exist: {input_path}")
        raise FileNotFoundError(f"Video file not found at {input_path}")

    try:
        # Resize video using MoviePy
        with VideoFileClip(input_path) as video:
            # Resize video to the specified width while maintaining aspect ratio
            resized_video = video.resize(width=width)
            resized_video.write_videofile(
                output_path,
                codec='libx264',  # Video codec (h.264)
                bitrate=bitrate,  # Adjust bitrate to compress the video
                fps=fps,  # Set fps (frames per second)
                threads=4  # Use multiple threads to speed up the processing
            )

        # Return the resized video path
        return output_path

    except Exception as e:
        # Log and raise exception for error handling
        logger.error(f"Error resizing video: {e}")
        raise



@shared_task
def compress_image_task(image_path, output_dir, output_filename, target_width=800, quality=85):
    input_path = os.path.join(default_storage.location, image_path)
    output_path = os.path.join(default_storage.location, output_dir, output_filename)

    try:
        with Image.open(input_path) as img:
            aspect_ratio = img.height / img.width
            target_height = int(target_width * aspect_ratio)
            img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)  # Use LANCZOS instead of ANTIALIAS

            output_io = BytesIO()
            img.save(output_io, format='JPEG', quality=quality, optimize=True)
            output_io.seek(0)

            with open(output_path, 'wb') as f:
                f.write(output_io.read())

        return output_path
    except Exception as e:
        print(f"Error compressing image: {e}")
        raise