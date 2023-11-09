import asyncio
import base64
import datetime
import glob
import json
import multiprocessing
import os
import random
import re
import subprocess
import tempfile
from dataclasses import dataclass
from typing import List

import requests

nba_prompt = """
Give a play-by-play description of what is happening in this snippet.
Your output will be used as commentary to describe what is happening so be enthusiastic like a broadcaster.
Only talk about the specific play. Do not talk about the overall context.
Do not hallucinate anything. Be very concise. Limit to 70 words. Do not give any introduction.
"""

good_data = [
    {
        "start": 5228,
        "end": 5239,
        "text": "Green back to Curry.  Curry sets leans in.  He's got a shot clock at seven.  He's got a shot clock at seven.  He's got a shot clock at seven.  Knocked away get it back from",
    },
    {
        "start": 5238,
        "end": 5249,
        "text": "Curry shot clock at seven.  Baseball on the drive kicks it  out.  Pull for three.  James the rebound with thirty",
    },
    {
        "start": 5248,
        "end": 5261,
        "text": "two seconds remaining.  There's about a 10 second  different shot clock and game  clock they don't have to foul.  LeBron James I'm putting my head",
    },
    {
        "start": 5260,
        "end": 5273,
        "text": "down and attacking.  I'm going to foul.  I'm not letting him shoot a  three.  They have a timeout left but  won't call it here.  Curse trying to call it.  And finally he gets it.  Steve Kerr came to half court.",
    },
    {
        "start": 5273,
        "end": 5284,
        "text": "The officials couldn't see him  or clearly couldn't hear him.  And he gets the timeout with two  point one remaining.  We'll see if the officials look  to see to perhaps put more time",
    },
    {
        "start": 5283,
        "end": 5295,
        "text": "on the clock.  The Lakers are up three.  James the rebound with thirty  two seconds remaining.  They got a great look the last",
    },
    {
        "start": 5294,
        "end": 5306,
        "text": "time by Jordan Poole in the  corner of a nice pass by  Basemore.  LeBron James with the three  pointer had to throw it up the",
    },
    {
        "start": 5305,
        "end": 5317,
        "text": "shot clock was expiring.  It's a big time shot.  Awful execution.  Realizes that the clock went",
    },
    {
        "start": 5316,
        "end": 5329,
        "text": "down the good chase down by  Curry and.  LeBron.  Elevates.  Knocks down the biggest shot of  the night.  That's a 30 footer.  And you see Curry.  Who's had that look on.",
    },
    {
        "start": 5329,
        "end": 5340,
        "text": "Opponents faces after he knocks  down threes the same look as  LeBron James with a clutch shot.",
    },
]


@dataclass
class Snippet:
    tempdir: tempfile.TemporaryDirectory
    snippet_path: str
    start: int
    whisper_text: str
    gptv_text: str = ""


def generateFakeSamples():
    snips = [x for x in range(10, 3600, 50)]
    snips = random.sample(snips, 10)
    out = []
    for s in snips:
        cur = {"start": s, "end": s + 10, "text": f"the current start time is: {s}"}
        out.append(cur)
    return out


def useRealData():
    return good_data


def sortedDataByStart(data, enforce_no_overlap: bool = True):
    sdata = sorted(data, key=lambda x: x["start"])
    if not enforce_no_overlap:
        return sdata
    new_data = []
    new_data.append(sdata[0])

    for check in sdata[1:]:
        cur = new_data[-1]
        if cur["end"] >= check["start"]:
            cur["end"] = check["end"]
            cur["text"] += ". " + check["text"]
        else:
            new_data.append(check)
    return new_data


def checkData():
    data = sortedDataByStart(good_data)
    for d in data:
        s = d["start"]
        e = d["end"]
        print(f"start: {s}, time: {e - s}")


def getOpenAIKey():
    openai_key = os.getenv("OPENAI_API_KEY")
    if openai_key is not None:
        return openai_key
    else:
        print("THE KEY DOESNT EXIST AS AN ENV VARIABLE!!!!!!!!")
        with open(".OPENAI_KEY.key", "r") as fd:
            return fd.read().strip()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def imagePathsToGPT4(image_paths):
    """Given list of image paths return GPT4Vision output using them."""
    api_key = getOpenAIKey()
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}

    contents = []
    user_prompt = {"type": "text", "text": nba_prompt}
    contents.append(user_prompt)
    for i, img_path in enumerate(image_paths):
        base64_image = encode_image(img_path)
        cur_img = {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/jpeg;base64,{base64_image}",
                "detail": "low",
            },
        }
        contents.append(cur_img)

    payload = {
        "model": "gpt-4-vision-preview",
        "messages": [{"role": "user", "content": contents}],
        "max_tokens": 600,
    }

    response = requests.post(
        "https://api.openai.com/v1/chat/completions", headers=headers, json=payload
    )
    if response.status_code != 200:
        return False, response
    output = json.loads(response.text)
    return True, output["choices"][0]["message"]["content"]


def pathToPics(path):
    """Given a path to png files glob, return all pngs matching regex."""
    pics = glob.glob(path)
    pics_sort = []
    for p in pics:
        number = int(re.findall("\d+", p)[0])
        pics_sort.append((p, number))
    pics_sort = sorted(pics_sort, key=lambda x: x[1])
    return [x[0] for x in pics_sort]


def secondsToTimestamp(seconds):
    """Converts seconds to hour:minute:seconds."""
    return str(datetime.timedelta(seconds=seconds))


def runSubprocessCmd(cmd: str):
    return subprocess.Popen([cmd], shell=True).wait()


def createVideoSnippet(
    start: int, end: int, input_path: str, output_dir: str, ext: str = None
):
    if ext is None:
        ext = get_ext_from_path(input_path)
    """Given start, end and input file, return success, created snippet path tuple."""
    fstart = secondsToTimestamp(start)
    fend = secondsToTimestamp(end)
    filename = f"snippet_{start}_{end}.{ext}"
    output_path = os.path.join(output_dir, filename)
    ffmpeg_cmd = f"ffmpeg -ss {fstart} -to {fend} -i {input_path} -c copy {output_path}"
    output = runSubprocessCmd(ffmpeg_cmd)
    if output != 0:
        print(f"Error for cmd: {ffmpeg_cmd}")
        return False, None
    return True, output_path


def createImagesFromSnippet(input_path: str, tempdir: str, ext: str = "png"):
    """Convert video to png with ffmpeg."""
    out_png = f"out_%d.{ext}"
    out_png = os.path.join(tempdir, out_png)
    ffmpeg_cmd = f"ffmpeg -i {input_path} -vf fps=1 -s 512x512 {out_png}"
    output = runSubprocessCmd(ffmpeg_cmd)
    if output != 0:
        print(f"Error for cmd: {ffmpeg_cmd}")
        return False
    return True


async def imagesToGPT(tempdir: str):
    img_path = os.path.join(tempdir, "*.png")
    image_paths = pathToPics(img_path)
    success, output = imagePathsToGPT4(image_paths)
    if success:
        return True, output
    print("GPT4 Error: ", output)
    return False, None


def snippetsToPngsFn(snip: Snippet):
    """parallel convert video to pictures."""
    tempdir = snip.tempdir
    snippet_path = snip.snippet_path
    return createImagesFromSnippet(snippet_path, tempdir.name)


async def snippetsToGPTFn(snips: List[Snippet]):
    tasks = [imagesToGPT(s.tempdir.name) for s in snips]
    return await asyncio.gather(*tasks)


def mergeSnippetsToVideo(snips: List[Snippet], tempdir: str, ext: str = "webm"):
    snip_vids = [f"file '{s.snippet_path}'" for s in snips]
    snip_file = os.path.join(tempdir, "snip_file.txt")
    with open(snip_file, "w") as fd:
        fd.write("\n".join(snip_vids))
    merged_path = os.path.join(tempdir, f"merged.{ext}")
    ffmpeg_cmd = f"ffmpeg -f concat -safe 0 -i {snip_file} -c copy {merged_path}"
    output = runSubprocessCmd(ffmpeg_cmd)
    if output != 0:
        print(f"Error for cmd: {ffmpeg_cmd}")
        return False, None
    return True, merged_path


def copyFinalVideoAndText(
    video_path: str,
    snips: List[Snippet],
    output_dir: str,
    output_video_name: str,
    output_text_name: str,
    ext: str = "webm",
):
    outfile_video = os.path.join(output_dir, f"{output_video_name}.{ext}")
    outfile_text = os.path.join(output_dir, output_text_name)
    cmd = f"mv {video_path} {outfile_video}"
    output = runSubprocessCmd(cmd)
    if output != 0:
        print(f"Error for cmd: {cmd}")
        return False, None
    text = [s.gptv_text for s in snips if s.gptv_text]
    text = "\n".join(text)
    with open(outfile_text, "w") as fd:
        fd.write(text)
    return True, (outfile_video, outfile_text)


def runVision(input_data, input_path, output_dir):
    video_ext = get_ext_from_path(input_path)
    snippet_data = sortedDataByStart(input_data)
    snippets = []
    for f in snippet_data:
        tempdir = tempfile.TemporaryDirectory()
        success, snippet_path = createVideoSnippet(
            f["start"], f["end"], input_path, tempdir.name, ext=video_ext
        )
        if not success:
            print("createVideoSnippet returned False!!!! FUCKKKKKK")
            raise ValueError("FUCKKKK")
        snip = Snippet(
            tempdir=tempdir,
            snippet_path=snippet_path,
            start=f["start"],
            whisper_text=f["text"],
        )
        snippets.append(snip)

    with multiprocessing.Pool() as pool:
        results = pool.map(snippetsToPngsFn, snippets)

    results = asyncio.run(snippetsToGPTFn(snippets))
    for (sucess, text), snip in zip(results, snippets):
        if success:
            snip.gptv_text = text

    tempdir = tempfile.TemporaryDirectory()
    success, merged_path = mergeSnippetsToVideo(snippets, tempdir.name, ext=video_ext)

    for s in snippets:
        s.tempdir.cleanup()

    output_video_name = "reel"
    output_text_name = "summary"
    success, (vid_name, txt_name) = copyFinalVideoAndText(
        merged_path, snippets, output_dir, output_video_name, output_text_name
    )
    if success:
        return (vid_name, txt_name)
    return ("", "")


def get_ext_from_path(path: str):
    return os.path.splitext(path)[1][1:]


# input_path = '/home/lodi/mindsdb/warriors_game/warriors_game.webm'
# output_dir = '/home/lodi/mindsdb/output'
# runVision(good_data, input_path, output_dir)
