from io import BytesIO

from PIL import Image
from celery import shared_task
from moviepy.video.io.VideoFileClip import VideoFileClip
from django.core.files.storage import default_storage
import os
import logging

logger = logging.getLogger(__name__)





# @shared_task
# def resize_video_task(video_path, output_dir, output_filename, width=640, bitrate="500k", fps=24):
#     input_path = os.path.join(default_storage.location, video_path)
#     output_path = os.path.join(default_storage.location, output_dir, output_filename)
#
#     # Ensure the input video exists
#     if not os.path.exists(input_path):
#         logger.error(f"Input video file does not exist: {input_path}")
#         raise FileNotFoundError(f"Video file not found at {input_path}")
#
#     try:
#         # Resize video using MoviePy
#         with VideoFileClip(input_path) as video:
#             # Resize video to the specified width while maintaining aspect ratio
#             resized_video = video.resized(width=width)
#             resized_video.write_videofile(
#                 output_path,
#                 codec='libx264',  # Video codec (h.264)
#                 bitrate=bitrate,  # Adjust bitrate to compress the video
#                 fps=fps,  # Set fps (frames per second)
#                 threads=4  # Use multiple threads to speed up the processing
#             )
#
#         # Return the resized video path
#         return output_path
#
#     except Exception as e:
#         # Log and raise exception for error handling
#         logger.error(f"Error resizing video: {e}")
#         raise


import os
import subprocess
import logging
import uuid
from django.core.files.storage import default_storage
from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def resize_video_task(video_path, output_dir, output_filename,
                      width=640,
                      max_bitrate="500k",
                      max_fps=24,
                      max_duration_seconds=60):  # Durasi maksimal 60 detik
    """
    Optimasi video dengan pembatasan durasi
    """
    input_path = os.path.join(default_storage.location, video_path)
    output_path = os.path.join(default_storage.location, output_dir, output_filename)

    # Cek eksistensi file
    if not os.path.exists(input_path):
        logger.error(f"Video tidak ditemukan: {input_path}")
        raise FileNotFoundError(f"File video tidak tersedia di {input_path}")

    try:
        # Dapatkan informasi video asli
        probe_cmd = [
            'ffprobe',
            '-v', 'error',
            '-show_entries', 'format=duration',
            '-of', 'default=noprint_wrappers=1:nokey=1',
            input_path
        ]

        # Ambil durasi video
        duration = float(subprocess.check_output(probe_cmd, universal_newlines=True).strip())

        # Tentukan parameter pemotongan
        start_time = 0
        if duration > max_duration_seconds:
            # Jika video lebih panjang, mulai dari akhir
            start_time = duration - max_duration_seconds
            duration = max_duration_seconds

        # Dapatkan informasi resolusi asli
        probe_resolution_cmd = [
            'ffprobe',
            '-v', 'error',
            '-select_streams', 'v:0',
            '-count_packets',
            '-show_entries', 'stream=width,height,r_frame_rate',
            '-of', 'csv=p=0',
            input_path
        ]

        probe_result = subprocess.check_output(probe_resolution_cmd, universal_newlines=True).strip().split(',')

        # Parse informasi video
        original_width = int(probe_result[0])
        original_height = int(probe_result[1])
        original_fps = eval(probe_result[2])

        # Hitung aspek rasio
        aspect_ratio = original_width / original_height
        new_height = int(width / aspect_ratio)

        # Batasi fps
        target_fps = min(original_fps, max_fps)

        # Optimasi kompleks dengan FFmpeg
        ffmpeg_cmd = [
            'ffmpeg',
            '-ss', str(start_time),  # Waktu mulai
            '-i', input_path,  # Input file
            '-t', str(max_duration_seconds),  # Durasi maksimal
            '-vf', f'scale={width}:{new_height}',  # Resize dengan mempertahankan aspek rasio
            '-c:v', 'libx264',  # Video codec
            '-preset', 'medium',  # Preset kompresi
            '-crf', '23',  # Kualitas kompresi (0-51, lower = better quality)
            '-maxrate', max_bitrate,  # Batasi bitrate maksimum
            '-bufsize', '1M',  # Buffer untuk bitrate
            '-r', str(target_fps),  # Batasi frame rate
            '-c:a', 'aac',  # Audio codec
            '-b:a', '128k',  # Bitrate audio
            output_path
        ]

        # Jalankan kompresi
        subprocess.run(ffmpeg_cmd, check=True)

        # Hapus file input asli
        os.unlink(input_path)

        return output_path

    except subprocess.CalledProcessError as e:
        logger.error(f"Kesalahan kompresi video: {e}")
        raise
    except Exception as e:
        logger.error(f"Error umum pada kompresi video: {e}")
        raise
#
# @shared_task
# def compress_image_task(image_path, output_dir, output_filename, target_width=800, quality=85):
#     input_path = os.path.join(default_storage.location, image_path)
#     output_path = os.path.join(default_storage.location, output_dir, output_filename)
#
#     try:
#         with Image.open(input_path) as img:
#             aspect_ratio = img.height / img.width
#             target_height = int(target_width * aspect_ratio)
#             img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)  # Use LANCZOS instead of ANTIALIAS
#
#             output_io = BytesIO()
#             img.save(output_io, format='JPEG', quality=quality, optimize=True)
#             output_io.seek(0)
#
#             with open(output_path, 'wb') as f:
#                 f.write(output_io.read())
#
#         return output_path
#     except Exception as e:
#         print(f"Error compressing image: {e}")
#         raise
# @shared_task
# def compress_image_task(image_path, output_dir, output_filename, target_width=800, quality=85):
#     input_path = os.path.join(default_storage.location, image_path)
#     output_path = os.path.join(default_storage.location, output_dir, output_filename)
#
#     try:
#         with Image.open(input_path) as img:
#             # Check if the image has an alpha channel (RGBA), and convert it to RGB if it does
#             if img.mode == 'RGBA':
#                 img = img.convert('RGB')
#
#             # Resize the image to the target width while maintaining aspect ratio
#             aspect_ratio = img.height / img.width
#             target_height = int(target_width * aspect_ratio)
#             img = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
#
#             # Save the image in JPEG format
#             output_io = BytesIO()
#             img.save(output_io, format='JPEG', quality=quality, optimize=True)
#             output_io.seek(0)
#
#             with open(output_path, 'wb') as f:
#                 f.write(output_io.read())
#
#         return output_path
#     except Exception as e:
#         print(f"Error compressing image: {e}")
#         raise




@shared_task
def compress_image_task(image_path, output_dir, output_filename, target_width=800, quality=85):
    input_path = os.path.join(default_storage.location, image_path)
    output_path = os.path.join(default_storage.location, output_dir, output_filename)
    try:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with Image.open(input_path) as img:
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            # Hitung ulang tinggi dengan mempertahankan rasio aspek
            aspect_ratio = img.height / img.width
            target_height = int(target_width * aspect_ratio)
            # Resize gambar
            resized_img = img.resize(
                (target_width, target_height),
                resample=Image.Resampling.BICUBIC  # Alternatif untuk Lanczos
            )
            output_io = BytesIO()
            resized_img.save(
                output_io,
                format='JPEG',
                quality=quality,
                optimize=True
            )
            output_io.seek(0)
            # Tulis ke file
            with open(output_path, 'wb') as f:
                f.write(output_io.read())

        return output_path
    except Exception as e:
        print(f"Error compressing image: {e}")
        raise
