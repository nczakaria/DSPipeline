import csv
import subprocess
import os
from pydub import AudioSegment 

number = 11


def download_and_process_video(video_id, start_time, end_time, video_type, save_path, ffmpeg_location=None):
    global number
    # Construct the output file name and path
    output_name = f"{video_type}_{number}.mp3"
    output_path = os.path.join(save_path, output_name)
    temp_mp3_path = os.path.join(save_path, f"{video_id}.mp3")

    # Create the save directory if it doesn't exist
    os.makedirs(save_path, exist_ok=True)

    # Download the audio from the YouTube video
    ffmpeg_option = f"--ffmpeg-location \"{ffmpeg_location}\"" if ffmpeg_location else ""
    download_command = f'yt-dlp -x --audio-format mp3 {ffmpeg_option} -o \"{temp_mp3_path}\" https://www.youtube.com/watch?v={video_id}'
    subprocess.run(download_command, shell=True)

    # Crop the audio
    if os.path.exists(temp_mp3_path):
        print(f"Processing {video_id} from {start_time} to {end_time}")
        start_time_ms = start_time * 1000  # convert to milliseconds
        end_time_ms = end_time * 1000  # convert to milliseconds

        # Load audio file using pydub
        audio = AudioSegment.from_file(temp_mp3_path)
        cropped_audio = audio[start_time_ms:end_time_ms]
        
        # Export the cropped audio to the output path
        cropped_audio.export(output_path, format="ogg")
        
        number += 1

        
        # Remove the original downloaded audio if it exists
        if os.path.exists(temp_mp3_path):
            os.remove(temp_mp3_path)


def process_csv(csv_file_path, ffmpeg_location=None):
    save_path = r'Audio_data'
    video_type = 'Traffic'
    with open(csv_file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        for row in reader:
            video_id = row[0]
            start_time = float(row[1])
            end_time = float(row[2])
            download_and_process_video(video_id, start_time, end_time, video_type, save_path, ffmpeg_location)

# Replace 'your_file.csv' with the path to your CSV file
csv_file_path = r'Audio_data_collection\traffic_data.csv'
ffmpeg_location = r'C:\ffmpeg'
process_csv(csv_file_path, ffmpeg_location=ffmpeg_location)
