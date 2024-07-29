import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

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
            # Extract audio streams
            audio_command_template = [
                'ffmpeg', '-y', '-i', file_path, '-map', '0:a:{stream_index}', 
                '-c:a', 'aac', '-b:a', '192k', '-vn', '{output_file}'
            ]
            audio_streams = []
            for i in range(10):  # Handle up to 10 audio streams
                output_file = f"{base_name}_audio_{i}.m4a"
                audio_command = [x.format(stream_index=i, output_file=output_file) for x in audio_command_template]
                try:
                    run_ffmpeg_command(audio_command, dash_output_path)
                    if os.path.exists(os.path.join(dash_output_path, output_file)):
                        audio_streams.append(output_file)
                except RuntimeError as e:
                    if "Stream map '0:a:" in str(e):
                        break  # No more audio streams available
                    else:
                        raise

            # Define video commands for different resolutions
            video_commands = [
                [
                    'ffmpeg', '-y', '-i', file_path, '-preset', 'medium', '-tune', 'film', '-vsync', 'passthrough',
                    '-an', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '22',
                    '-maxrate', '5000k', '-bufsize', '10000k', '-pix_fmt', 'yuv420p', '-f', 'mp4', f"{base_name}_original.mp4"
                ],
                [
                    'ffmpeg', '-y', '-i', file_path, '-preset', 'medium', '-tune', 'film', '-vsync', 'passthrough',
                    '-an', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '23',
                    '-maxrate', '3000k', '-bufsize', '6000k', '-pix_fmt', 'yuv420p', '-vf', 'scale=-2:720', '-f', 'mp4', f"{base_name}_720p.mp4"
                ],
                [
                    'ffmpeg', '-y', '-i', file_path, '-preset', 'medium', '-tune', 'film', '-vsync', 'passthrough',
                    '-an', '-c:v', 'libx264', '-x264opts', 'keyint=48:min-keyint=48:no-scenecut', '-crf', '23',
                    '-maxrate', '1500k', '-bufsize', '3000k', '-pix_fmt', 'yuv420p', '-vf', 'scale=-2:480', '-f', 'mp4', f"{base_name}_480p.mp4"
                ]
            ]

            with ThreadPoolExecutor() as executor:
                executor.map(lambda cmd: run_ffmpeg_command(cmd, dash_output_path), video_commands)

            # Generate DASH manifest
            dash_command = [
                'MP4Box', '-dash', '4000', '-rap', '-frag-rap', '-bs-switching', 'no', '-profile', 'dashavc264:live',
                f"{base_name}_original.mp4", f"{base_name}_720p.mp4", f"{base_name}_480p.mp4"
            ] + audio_streams + ['-out', f"{base_name}.mpd"]
            run_ffmpeg_command(dash_command, dash_output_path)

            # Clean up individual segments
            for file in [f"{base_name}_original.mp4", f"{base_name}_720p.mp4", f"{base_name}_480p.mp4"] + audio_streams:
                os.remove(os.path.join(dash_output_path, file))

            # Create a jpg for poster
            poster_command = [
                'ffmpeg', '-i', file_path, '-ss', '00:00:00', '-vframes', '1', '-qscale:v', '10', '-n', '-f', 'image2', f"{base_name}.jpg"
            ]
            run_ffmpeg_command(poster_command, dash_output_path)

        except Exception as e:
            print(f"An error occurred while processing the video: {e}")
