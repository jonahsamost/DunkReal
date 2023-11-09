
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
                "content": "You are a video editor editing highlight reels for a basketball game. Your task is to rank the commentary snippets given to you based on how likely the snippet would contain a highlight play.\n\nSome previous highlight play commetary are:1. picks up right where he left off\n2. shut off by\n3. makes the play\n4. waiting for a rebound\n5. extra feed\n6. seal against\n7. good help\n8. draws the foul\n9. step back\n10. knock down the three\n11. push the pace\n12. transition three\n13. catch and shoot\n14. mouse in the house\n15. step back and kiss myself\n16. hustle play\n17. blow by\n18. walk-up three\n19. come fly with me\n20. comfortable coming off the bench\n21. spinning to the rim\n22. stay on the guy\n23. finding the open man\n24. tied the game\n25. takes up slack\n26. scoop to score\n27. put back dunk\n28. contested three\n29. for the win\n30. rolls and kicks\n31. hold for the last shot\n32. overtime\n33. king of the fourth\n34. out of bounds\n35. on the move\n36. off the glass\n37. shot clock at\n38. double team\n39. leading to offense\n40. shooting start\n41. off to an excellent start\n42. spark off the bench\n43. corner three\n44. high up the glass\n45. transition defense\n46. strong finish\n47. charges up\n48. fires a three\n49. down by\n50. back door cut\n\nthe more positive the commentary snippet seems like, the more likely the snippet contains a highlight play\n\nEach snippets are expressed as an object with the following format:\n{\n   start: the timestamp of the start of the snippet\n   end: the timestamp of the end of the snippet\n   text: the commentary snippet\n}\n\nWhen outputting, only output in a json array that contains the highlight snippets with the key `highlights`"
            },
            {
                "role": "user",
                "content": f'Here are the snippets\n\n```\n{transcript_str}\n```\n\nFind the top {top_n} snippets'
            },
        ],
        response_format={ "type": "json_object" }
    )
    return response.choices[0].message.content
