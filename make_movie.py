import argparse
from moviepy.editor import AudioFileClip, concatenate_videoclips, TextClip, CompositeVideoClip, ImageClip
import numpy as np
import srt
import re

def filter_subtitles(subtitles, start_time, end_time):
    filtered_subtitles = []
    for subtitle in subtitles:
        if subtitle.start.total_seconds() >= start_time and subtitle.end.total_seconds() <= end_time:
            filtered_subtitles.append(subtitle)
    return filtered_subtitles


def create_video_with_captions(audio_file_path, subtitles_file_path, output_file_path):
    # Load audio
    audio_clip = AudioFileClip(audio_file_path)

    # Parse subtitles
    with open(subtitles_file_path) as f:
        subtitle_generator = srt.parse(f)
        subtitles = list(subtitle_generator)

    # Create a black background image
    # black_background = np.zeros((1080, 1920, 3))  # 1080p resolution
    # smaller res for debug
    black_background = np.zeros((480, 640, 3))  # 480p resolution

    # Create video clips with subtitles
    clips = []
    # doctor_name = None
    # doctor_speaker_id = None
    # patient_speaker_id = None
    for subtitle in subtitles:
    #     # Hilarious hack
    #     # Check if the Doctor is speaking by searching for "Doctor" in the subtitle
    #     # If so, we map their diarization speaker ID (e.g. [SPEAKER_01]) to the Doctor's name, and
    #     # the other speaker's ID to "Patient"
    #     if not doctor_speaker_id:
    #         if "doctor" in subtitle.content.lower():
    #             doctor_name = re.search(r"doctor ([a-z]+)", subtitle.content.lower()).group(1)
    #         elif "dr." in subtitle.content.lower():
    #             doctor_name = "Dr. " + re.search(r"dr. ([a-z]+)", subtitle.content.lower()).group(1).capitalize()
    #         print(f"Doctor name: {doctor_name}")
    #         if doctor_name:
    #             doctor_speaker_id = re.search(r"\[([A-Z_0-9]+)\]", subtitle.content).group(1)
    #             print(f"Doctor speaker ID: {doctor_speaker_id}")
    #     elif not patient_speaker_id and doctor_speaker_id not in subtitle.content:
    #         patient_speaker_id = re.search(r"\[([A-Z_0-9]+)\]", subtitle.content).group(1)
    #         print(f"Patient speaker ID: {patient_speaker_id}")

    #     if doctor_speaker_id and doctor_speaker_id in subtitle.content:
    #         subtitle.content = subtitle.content.replace(doctor_speaker_id, doctor_name)
    #     if patient_speaker_id and patient_speaker_id in subtitle.content:
    #         subtitle.content = subtitle.content.replace(patient_speaker_id, "Patient")


        # Create a TextClip for each subtitle
        background_clip = ImageClip(black_background, duration=(subtitle.end - subtitle.start).total_seconds())
        txt_clip = TextClip(subtitle.content, fontsize=35, color='white', font="Arial", size=background_clip.size, method="caption", align="center", interline=0.5)
        txt_clip = txt_clip.set_pos('center').set_duration((subtitle.end - subtitle.start).total_seconds())
        txt_clip = txt_clip.on_color(
                  color=(0,0,0), pos=(6,'center'), col_opacity=0.6)

        # Set the start time for the text clip
        # txt_clip = txt_clip.set_start(subtitle.start.total_seconds())

        # Set the audio of the text clip
        start_time = subtitle.start.total_seconds()
        end_time = min(subtitle.end.total_seconds(), audio_clip.duration)  # Ensure the end time doesn't exceed the audio clip's duration
        txt_clip = txt_clip.set_audio(audio_clip.subclip(start_time, end_time))

        composite = CompositeVideoClip([background_clip, txt_clip])
        # for debug purposes
        # if len(clips) < 5:
        #     composite.write_videofile(f"subtitle_{subtitle.start.total_seconds()}.mp4", codec="libx264", audio_codec="aac", fps=24)  # Set a fixed fps

        clips.append(composite)

    # Concatenate all clips
    final_clip = concatenate_videoclips(clips)

    # Write the final video file
    final_clip.write_videofile(output_file_path, codec="libx264", audio_codec="aac", fps=24)

def main():
    parser = argparse.ArgumentParser(description="Create a video with captions from an audio file and subtitle file.")
    parser.add_argument("audio_file", help="Path to the audio file (.wav)")
    parser.add_argument("subtitles_file", help="Path to the subtitles file (.srt, .vtt, etc.)")
    parser.add_argument("output_file", help="Path to the output video file (.mp4)")

    args = parser.parse_args()
    create_video_with_captions(args.audio_file, args.subtitles_file, args.output_file)

if __name__ == "__main__":
    main()
