# Title                 : Create 4x4 thumbnail image grid from video file using python and FFmpeg.
# Created by            : Chalongchaii@gmail.com
# Generate code from    : ChatGPT
# License               : Free
# Modify date           : 23-07-2024
# **************************************

import os
import subprocess
import glob

# Paths
ffmpeg_path = "ffmpeg.exe"
ffprobe_path = "ffprobe.exe"  # Use ffprobe instead of ffmpeg for duration
video_dir = "Input-Video"
output_dir = "Output-Image"
font_path = "NotoSansThai.ttf"  # Update this path if needed

# Create the output directory if it doesn't exist
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Get all .mp4 files in the directory
video_files = glob.glob(os.path.join(video_dir, "*.mp4"))

# Process each video file
for video_file in video_files:
    video_name = os.path.splitext(os.path.basename(video_file))[0]
    output_thumb_dir = os.path.join(output_dir, video_name)

    # Create a directory to store thumbnail images for each video
    if not os.path.exists(output_thumb_dir):
        os.makedirs(output_thumb_dir)

    # Use FFprobe to get the duration of the video
    ffprobe_cmd = [
        ffprobe_path, "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", video_file
    ]

    try:
        result = subprocess.run(ffprobe_cmd, capture_output=True, text=True, check=True)
        duration_str = result.stdout.strip()
        
        if not duration_str:
            raise ValueError(f"Could not retrieve duration for video: {video_file}")

        duration = float(duration_str)
        interval = duration / 16

        # Extract 16 thumbnails from the video
        for i in range(16):
            time = i * interval
            output_thumb = os.path.join(output_thumb_dir, f"thumb_{i+1}.jpg")
            cmd = [
                ffmpeg_path, "-ss", str(time), "-i", video_file,
                "-vframes", "1", "-q:v", "2", "-y", output_thumb
            ]
            subprocess.run(cmd, check=True)

        # Ensure the video name is correctly handled for Thai characters
        utf8_video_name = video_name.encode('utf-8').decode('utf-8')

        # Combine thumbnails into a 4x4 grid and overlay the video name
        output_image = os.path.join(output_dir, f"{video_name}_grid.jpg")
        drawtext_cmd = [
            ffmpeg_path, "-i", os.path.join(output_thumb_dir, "thumb_%d.jpg"),
            "-filter_complex",
            f"tile=4x4,drawtext=text='{utf8_video_name}':x=(w-text_w)/2:y=h-th-50:fontsize=200:fontcolor=white:box=1:boxcolor=black@0.5:fontfile='{font_path}'", "-y", 
            output_image
        ]

        subprocess.run(drawtext_cmd, check=True)

        print(f"Created thumbnail grid image for {video_name}: {output_image}")

    except subprocess.CalledProcessError as e:
        print(f"An error occurred while running FFmpeg on {video_file}: {e}")
    except (ValueError, KeyError) as ve:
        print(f"Error processing {video_file}: {ve}")
