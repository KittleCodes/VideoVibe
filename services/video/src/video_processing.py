import os
import subprocess

def run_ffmpeg_command(command, output_path):
    """Run an FFmpeg command and return the output."""
    process = subprocess.Popen(command, cwd=output_path, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise RuntimeError(f"FFmpeg command failed with error: {stderr.decode('utf-8')}")
    return stdout, stderr

def process_video(file_path, filename):
    """Convert video to multi-bitrate in MPEG-DASH format."""
    file_path = os.path.abspath(file_path)  # Fullname of the file
    base_name = os.path.splitext(filename)[0]  # Name without extension
    
    dash_output_path = os.path.join('dash/', base_name)
    os.makedirs(dash_output_path, exist_ok=True)

    if os.path.exists(dash_output_path):
        print(f"Converting \"{base_name}\" to multi-bitrate video in MPEG-DASH")

        try:
            # FFmpeg command to extract multiple outputs (video at different resolutions + audio)
            ffmpeg_command = [
                'ffmpeg', '-y', '-i', file_path, '-preset', 'medium', '-tune', 'film', '-vsync', 'passthrough',
                # Audio stream extraction
                '-map', '0:a', '-c:a', 'aac', '-b:a', '192k', '-vn', '-f', 'mp4', f"{base_name}_audio.m4a",
                # Original resolution video stream
                '-map', '0:v', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '22',
                '-maxrate', '5000k', '-bufsize', '10000k', '-pix_fmt', 'yuv420p', '-f', 'mp4', f"{base_name}_original.mp4",
                # 720p video stream
                '-map', '0:v', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '23',
                '-maxrate', '3000k', '-bufsize', '6000k', '-vf', 'scale=-2:720', '-pix_fmt', 'yuv420p', '-f', 'mp4', f"{base_name}_720p.mp4",
                # 480p video stream
                '-map', '0:v', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '23',
                '-maxrate', '1500k', '-bufsize', '3000k', '-vf', 'scale=-2:480', '-pix_fmt', 'yuv420p', '-f', 'mp4', f"{base_name}_480p.mp4"
            ]

            # Run FFmpeg command to process both video and audio in parallel
            run_ffmpeg_command(ffmpeg_command, dash_output_path)

            # Generate DASH manifest
            dash_command = [
                'MP4Box', '-dash', '4000', '-rap', '-frag-rap', '-bs-switching', 'no', '-profile', 'dashavc264:live',
                f"{base_name}_original.mp4", f"{base_name}_720p.mp4", f"{base_name}_480p.mp4", f"{base_name}_audio.m4a",
                '-out', f"{base_name}.mpd"
            ]
            run_ffmpeg_command(dash_command, dash_output_path)

            # Clean up individual segments
            for file in [f"{base_name}_original.mp4", f"{base_name}_720p.mp4", f"{base_name}_480p.mp4", f"{base_name}_audio.m4a"]:
                os.remove(os.path.join(dash_output_path, file))

            # Create a jpg for poster
            poster_command = [
                'ffmpeg', '-i', file_path, '-ss', '00:00:00', '-vframes', '1', '-qscale:v', '10', '-n', '-f', 'image2', f"{base_name}.jpg"
            ]
            run_ffmpeg_command(poster_command, dash_output_path)

        except Exception as e:
            print(f"An error occurred while processing the video: {e}")
