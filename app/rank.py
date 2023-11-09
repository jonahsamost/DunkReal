
from openai import OpenAI
import datetime
import os
import math
import json

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)


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
        transcript = {
            'start': transcript['start'], 'end': transcript['end'], 'text': transcript['text']}

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

# rank segment
# @param: transcript (str) - the full transcript of the game
# @param: top_n (int) - number of top highlight segments to return
#
# @return: top_segments ([{start, end, text}]) - top segments
def rank_segment(transcript, top_n: int):
    transcript_str = json.dumps(transcript)
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[
            {
                "role": "system",
                "content": "You are a video editor editing highlight reels for a basketball game. Your task is to rank the commentary snippets given to you based on how likely the snippet would contain a highlight play.\n\nA highlight play can be:\n- basket\n- score\n- dunk\n- steal\n- block\n\nthe more positive the commentary snippet seems like, the more likely the snippet contains a highlight play\n\nEach snippets are expressed as an object with the following format:\n{\n   start: the timestamp of the start of the snippet\n   end: the timestamp of the end of the snippet\n   text: the commentary snippet\n}\n\nWhen outputting, only output in a json array that contains the highlight snippets with the key `highlights`"
            },
            {
                "role": "user",
                "content": f'Here are the snippets\n\n```\n{transcript_str}\n```\n\nFind the top {top_n} snippets'
            },
        ],
        response_format={ "type": "json_object" }
    )
    return response.choices[0].message.content
