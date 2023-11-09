import asyncio
import logging
import pathlib
import subprocess
import time
import json

import modal
from modal import Image, Stub
from typing import List

from . import config

cache_volume = modal.NetworkFileSystem.persisted(config.NFS_NAME)
logging.basicConfig(level=logging.INFO)
stub = Stub("youtube-url-to-vid-and-transcript")


@stub.local_entrypoint()
def main():
    logging.info("Starting main function")
    vid_url = "https://www.youtube.com/watch?v=LPDnemFoqVk"
    video_pipeline.remote(vid_url)


@stub.function(
    network_file_systems={config.CACHE_DIR: cache_volume},
)
def video_pipeline(vid_url):
    
    (video_id, file_path) = url_fetch.remote(vid_url)
    audio_file_paths = process_video.remote(video_id, file_path)
    start_transcript_time = time.time()
    # get the whole transcript corpus
    transcript = asyncio.run(process_transcription(audio_file_paths))
    # with open(f'{config.CACHE_DIR}/full_transcript.json', 'w') as file:
    #     json.dump(transcript, file)
    # audio_file_to_transcript.remote(audio_file_paths[0])
    logging.info(f"Transcript: {transcript}")
    end_transcript_time = time.time()
    logging.info(
        f"Time taken for turning audio files into transcripts: {end_transcript_time - start_transcript_time} seconds"
    )


ffmpeg_image = (
    Image.debian_slim()
    .apt_install("git")
    .apt_install("ffmpeg")
    # .pip_install("ffmpeg")
    # .pip_install("ffmpeg-python")
)


@stub.function(
    image=ffmpeg_image,
    network_file_systems={config.CACHE_DIR: cache_volume},
    timeout=6000,
)
def process_video(video_id: str, video_path: str):
    logging.info("Starting process_video function")
    if not pathlib.Path(video_path).exists():
        logging.error(f"Video path {video_path} does not exist. Exiting.")
        return

    audio_folder = f"{config.CHUNKED_AUDIO_DIR}/{video_id}"
    ensure_dir(audio_folder)

    logging.info("Processing video into audio chunks")

    start_time = time.time()
    file_paths = asyncio.run(video_to_audio(video_path, audio_folder), debug=True)
    end_time = time.time()
    logging.info(f"Time taken for video_to_audio: {end_time - start_time} seconds")

    logging.info(f"Chunked all the audio files: {file_paths}")
    return file_paths


@stub.function(
    secret=modal.Secret.from_name("openai"),
    image=Image.debian_slim().pip_install("openai"),
    network_file_systems={config.CACHE_DIR: cache_volume},
)
async def audio_file_to_transcript(audio_file_path: str):
    from . import rank
    import os
    # fileName = audio_file_path.replace(".mp3", "-transcipt.json")
    # if (pathlib.Path(fileName)):
    #     with open(f'{audio_file_path.replace(".mp3", "-transcipt.json")}', 'r') as file:
    #         data = json.load(file)
    #     return data
    logging.info(f"Starting audio_file_to_transcript for {audio_file_path}")
    offset = int(os.path.basename(audio_file_path).split('_')[0])
    segments = rank.get_transcription(audio_file_path)
    logging.info(f"Type of segments: {type(segments)}")
    clean_segments = rank.clean_segments(segments, offset)
    logging.info(f"Type of clean_segments: {type(clean_segments)}")
    logging.info(f"Type of clean_segments: {type(clean_segments)}")
    logging.info(f"Transcription process completed: {clean_segments}")
    # try:
    #     with open(fileName, 'w') as file:
    #         file.write(json.dumps(clean_segments))
    # except TypeError as e:
    #     logging.error(f"Error while writing to JSON file: {e}")
    return clean_segments
    
async def process_transcription(audio_file_paths: List[str]):
    logging.info("Starting process_transcription function")
    tasks = []
    for audio_file_path in audio_file_paths:
        task = asyncio.create_task(audio_file_to_transcript.remote(audio_file_path))
        tasks.append(task)
    transcripts = await asyncio.gather(*tasks)
    logging.info("Transcription process completed")
    return transcripts



async def video_to_audio(video_path, audio_folder, chunk_size=600):
    logging.info("Running ffmpeg command to extract audio")
    duration = get_audio_duration(video_path)
    duration = int(float(duration))
    tasks = []
    file_paths = []
    for i in range(0, duration, chunk_size):
        start = i
        end = i + chunk_size
        output_path = f"{audio_folder}/{start}_{end}.mp3"
        file_paths.append(output_path)
        if pathlib.Path(output_path).exists():
            continue
        task = asyncio.create_task(
            run_command(
                "ffmpeg",
                "-i",
                video_path,
                "-ss",
                str(start),
                "-to",
                str(end),
                "-vn",
                "-acodec",
                "libmp3lame",
                output_path,
            )
        )
        tasks.append(task)
    await asyncio.gather(*tasks)
    logging.info("Finished extracting audio with ffmpeg")
    return file_paths


@stub.function(
    image=Image.debian_slim().pip_install("yt-dlp").pip_install("pytube"),
    network_file_systems={config.CACHE_DIR: cache_volume},
)
def url_fetch(url: str):
    import os
    from urllib.parse import parse_qs, urlparse

    logging.info("Starting url_fetch function")

    ensure_dir(config.VIDEO_DIR)

    parsed_url = urlparse(url)
    video_id = parse_qs(parsed_url.query)["v"][0]
    output_file = f"{config.VIDEO_DIR}/{video_id}.mp4"
    if not os.path.exists(output_file):
        # download_with_pytube(url, output_file)
        download_with_ydl(url, output_file)

    return (video_id, output_file)


### Higher level utils


def download_with_pytube(url: str, output_file: str):
    from pytube import YouTube

    yt = YouTube(url)

    yt.streams.filter(progressive=True, file_extension="mp4").order_by(
        "resolution"
    ).desc().first().download(output_path=output_file)


def download_with_ydl(url: str, output_file: str):
    import yt_dlp

    ydl_opts = {
        "outtmpl": output_file,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        import time

        start_time = time.time()
        ydl.download([url])
        end_time = time.time()
        logging.info(f"Downloaded {url} in {end_time - start_time} seconds")


def get_audio_duration(raw_audio_path: str):
    return subprocess.check_output(
        [
            "ffprobe",
            "-i",
            raw_audio_path,
            "-show_entries",
            "format=duration",
            "-v",
            "quiet",
            "-of",
            "csv=p=0",
        ]
    )


### Basic python utils


def ensure_dir(path: str):
    from pathlib import Path

    Path(path).mkdir(parents=True, exist_ok=True)


async def run_command(*args):
    process = await asyncio.create_subprocess_exec(
        *args, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )

    stdout, stderr = await process.communicate()

    if process.returncode != 0:
        raise Exception(
            f"Command exited with status {process.returncode}, stderr: {stderr.decode()}"
        )

    return stdout.decode()
