
from openai import OpenAI
import datetime
import os
import math

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


# def chunk_audio(filePath):
#     # take a 10 minute video
#     # chunk that to 10 seconds blocks
#     # Whisper and return an object with
#     # {
#     #   start: timestamp (relative to the start of the whole video)
#     #   end: timestamp (relative to the start of the whole video)
#     #   text: transcript
#     # }
#     #
#     output_file_paths = []

#     # Get the duration of the audio file in seconds
#     command = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filePath}'
#     result = subprocess.run(command.split(), stdout=subprocess.PIPE)
#     duration = int(float(result.stdout))

#     # Calculate the number of chunks based on the duration
#     num_chunks = duration // 10
#     if duration % 10 != 0:
#         num_chunks += 1

#     # Chunk the audio file
#     for i in range(num_chunks):
#         start_time = str(datetime.timedelta(seconds=i*10))
#         end_time = str(datetime.timedelta(seconds=(i+1)*10))
#         command = f'ffmpeg -ss {start_time} -to {end_time} -i ../files/warriors.mp3 -c copy ../files/chunk_{start_time.replace(":","_")}.mp3'
#         subprocess.run(command.split())
#         output_file_path = f'../files/chunk_{start_time.replace(":","_")}.mp3'
#         output_file_paths.append(output_file_path)

#     return output_file_paths

# sampleChunks = ['../files/chunk_0_00_00.mp3', '../files/chunk_0_00_10.mp3', '../files/chunk_0_00_20.mp3', '../files/chunk_0_00_30.mp3', '../files/chunk_0_00_40.mp3', '../files/chunk_0_00_50.mp3', '../files/chunk_0_01_00.mp3', '../files/chunk_0_01_10.mp3', '../files/chunk_0_01_20.mp3', '../files/chunk_0_01_30.mp3', '../files/chunk_0_01_40.mp3', '../files/chunk_0_01_50.mp3', '../files/chunk_0_02_00.mp3', '../files/chunk_0_02_10.mp3', '../files/chunk_0_02_20.mp3', '../files/chunk_0_02_30.mp3', '../files/chunk_0_02_40.mp3', '../files/chunk_0_02_50.mp3', '../files/chunk_0_03_00.mp3', '../files/chunk_0_03_10.mp3', '../files/chunk_0_03_20.mp3', '../files/chunk_0_03_30.mp3', '../files/chunk_0_03_40.mp3', '../files/chunk_0_03_50.mp3', '../files/chunk_0_04_00.mp3', '../files/chunk_0_04_10.mp3', '../files/chunk_0_04_20.mp3', '../files/chunk_0_04_30.mp3', '../files/chunk_0_04_40.mp3', '../files/chunk_0_04_50.mp3', '../files/chunk_0_05_00.mp3', '../files/chunk_0_05_10.mp3', '../files/chunk_0_05_20.mp3', '../files/chunk_0_05_30.mp3', '../files/chunk_0_05_40.mp3', '../files/chunk_0_05_50.mp3', '../files/chunk_0_06_00.mp3', '../files/chunk_0_06_10.mp3', '../files/chunk_0_06_20.mp3', '../files/chunk_0_06_30.mp3', '../files/chunk_0_06_40.mp3', '../files/chunk_0_06_50.mp3', '../files/chunk_0_07_00.mp3', '../files/chunk_0_07_10.mp3', '../files/chunk_0_07_20.mp3', '../files/chunk_0_07_30.mp3', '../files/chunk_0_07_40.mp3', '../files/chunk_0_07_50.mp3', '../files/chunk_0_08_00.mp3', '../files/chunk_0_08_10.mp3', '../files/chunk_0_08_20.mp3', '../files/chunk_0_08_30.mp3', '../files/chunk_0_08_40.mp3', '../files/chunk_0_08_50.mp3', '../files/chunk_0_09_00.mp3', '../files/chunk_0_09_10.mp3', '../files/chunk_0_09_20.mp3', '../files/chunk_0_09_30.mp3', '../files/chunk_0_09_40.mp3', '../files/chunk_0_09_50.mp3']

# oneChunk = 'files/500s_output.mp3'

def get_transcription(audioPath):
    with open(audioPath, 'rb') as audio_file:
        transcript = client.audio.transcriptions.create(
              model="whisper-1",
              file=audio_file,
              response_format="verbose_json"
          )
        return transcript.segments
    
def clean_segments(segments, offset):
    merged = []
    current_transcript = None

    for transcript in segments:
        transcript = {'start': transcript['start'], 'end': transcript['end'], 'text': transcript['text']}

        if current_transcript is None:
            current_transcript = transcript
        else:
            current_transcript['end'] = transcript['end']
            current_transcript['text'] += ' ' + transcript['text']
            # other properties like 'avg_logprob' could be averaged or recalculated in some way if needed

            # If the duration of the current segment is at least 10 seconds, add to merged and reset
            if current_transcript['end'] - current_transcript['start'] >= 10:
                merged.append(current_transcript)
                current_transcript = None

    # If there is a segment at the end that is less than 10 seconds, add it as well
    if current_transcript is not None:
        merged.append(current_transcript)

    for merge in merged:
        merge['start'] = math.floor(merge['start']) + offset
        merge['end'] = math.ceil(merge['end']) + offset

    return merged
