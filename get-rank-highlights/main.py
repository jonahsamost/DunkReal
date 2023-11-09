import subprocess
from openai import OpenAI
import os
from dotenv import load_dotenv
import json
import datetime


load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


def chunk_audio(filePath):
    # take a 10 minute video
    # chunk that to 10 seconds blocks
    # Whisper and return an object with
    # {
    #   start: timestamp (relative to the start of the whole video)
    #   end: timestamp (relative to the start of the whole video)
    #   text: transcript
    # }
    #
    output_file_paths = []

    # Get the duration of the audio file in seconds
    command = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 {filePath}'
    result = subprocess.run(command.split(), stdout=subprocess.PIPE)
    duration = int(float(result.stdout))

    # Calculate the number of chunks based on the duration
    num_chunks = duration // 10
    if duration % 10 != 0:
        num_chunks += 1

    # Chunk the audio file
    for i in range(num_chunks):
        start_time = str(datetime.timedelta(seconds=i*10))
        end_time = str(datetime.timedelta(seconds=(i+1)*10))
        command = f'ffmpeg -ss {start_time} -to {end_time} -i ../files/warriors.mp3 -c copy ../files/chunk_{start_time.replace(":","_")}.mp3'
        subprocess.run(command.split())
        output_file_path = f'../files/chunk_{start_time.replace(":","_")}.mp3'
        output_file_paths.append(output_file_path)

    return output_file_paths

sampleChunks = ['../files/chunk_0_00_00.mp3', '../files/chunk_0_00_10.mp3', '../files/chunk_0_00_20.mp3', '../files/chunk_0_00_30.mp3', '../files/chunk_0_00_40.mp3', '../files/chunk_0_00_50.mp3', '../files/chunk_0_01_00.mp3', '../files/chunk_0_01_10.mp3', '../files/chunk_0_01_20.mp3', '../files/chunk_0_01_30.mp3', '../files/chunk_0_01_40.mp3', '../files/chunk_0_01_50.mp3', '../files/chunk_0_02_00.mp3', '../files/chunk_0_02_10.mp3', '../files/chunk_0_02_20.mp3', '../files/chunk_0_02_30.mp3', '../files/chunk_0_02_40.mp3', '../files/chunk_0_02_50.mp3', '../files/chunk_0_03_00.mp3', '../files/chunk_0_03_10.mp3', '../files/chunk_0_03_20.mp3', '../files/chunk_0_03_30.mp3', '../files/chunk_0_03_40.mp3', '../files/chunk_0_03_50.mp3', '../files/chunk_0_04_00.mp3', '../files/chunk_0_04_10.mp3', '../files/chunk_0_04_20.mp3', '../files/chunk_0_04_30.mp3', '../files/chunk_0_04_40.mp3', '../files/chunk_0_04_50.mp3', '../files/chunk_0_05_00.mp3', '../files/chunk_0_05_10.mp3', '../files/chunk_0_05_20.mp3', '../files/chunk_0_05_30.mp3', '../files/chunk_0_05_40.mp3', '../files/chunk_0_05_50.mp3', '../files/chunk_0_06_00.mp3', '../files/chunk_0_06_10.mp3', '../files/chunk_0_06_20.mp3', '../files/chunk_0_06_30.mp3', '../files/chunk_0_06_40.mp3', '../files/chunk_0_06_50.mp3', '../files/chunk_0_07_00.mp3', '../files/chunk_0_07_10.mp3', '../files/chunk_0_07_20.mp3', '../files/chunk_0_07_30.mp3', '../files/chunk_0_07_40.mp3', '../files/chunk_0_07_50.mp3', '../files/chunk_0_08_00.mp3', '../files/chunk_0_08_10.mp3', '../files/chunk_0_08_20.mp3', '../files/chunk_0_08_30.mp3', '../files/chunk_0_08_40.mp3', '../files/chunk_0_08_50.mp3', '../files/chunk_0_09_00.mp3', '../files/chunk_0_09_10.mp3', '../files/chunk_0_09_20.mp3', '../files/chunk_0_09_30.mp3', '../files/chunk_0_09_40.mp3', '../files/chunk_0_09_50.mp3']

oneChunk = ['../files/500s_output.mp3']

def getTranscription(audioPath):
    return

def main():
    # chunked_audios = chunk_audio('../files/10-mins.mp3')
    transcriptions = []

    # chunk the file paths -- 10 per time
    # chunks = sampleChunks
    # chunked_chunks = [chunks[i:i + 10] for i in range(0, len(chunks), 10)]

    # for smaller_chunk in chunked_chunks:
        
    # # parallel whisper call
    # # put the transcriptions to an object
    
    # # ask GPT to rank it in terms of interestingness

    for audio in oneChunk:
        with open(audio, 'rb') as audio_file:
          transcript = client.audio.transcriptions.create(
              model="whisper-1",
              file=audio_file,
              response_format="verbose_json"
          )
          # start_time = int(audio.split('_')[1].replace('.mp3', ''))
          # end_time = start_time + 10
          transcriptions.append({
              # 'start': start_time,
              # 'end': end_time,
              'text': transcript
          })
    print(transcriptions)


if __name__ == "__main__":
    main()
