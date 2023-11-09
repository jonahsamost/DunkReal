from dataclasses import dataclass
from typing import List
import asyncio
import base64
import datetime
import glob
import json
import multiprocessing
import os
import random
import re
import requests
import subprocess
import tempfile


nba_prompt = '''
Give a play-by-play description of what is happening in this snippet.
Your output will be used as commentary to describe what is happening so be enthusiastic like a broadcaster.
Only talk about the specific play. Do not talk about the overall context.
Do not hallucinate anything. Be very concise. Limit to 70 words. Do not give any introduction.
'''


@dataclass
class Snippet:
  tempdir: str
  snippet_path: str
  start: int
  whisper_text: str
  gptv_text: str = ''


def generateFakeSamples():
  snips = [x for x in range(10, 3600, 50)]
  snips = random.sample(snips, 10)
  snips = sorted(snips)
  out = []
  for s in snips:
    cur = {'start': s, 'end': s + 10, 'text': f'the current start time is: {s}'}
    out.append(cur)
  return out

def getOpenAIKey():
  with open('.OPENAI_KEY.key', 'r') as fd:
    return fd.read().strip()

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

def imagePathsToGPT4(image_paths):
  """Given list of image paths return GPT4Vision output using them."""
  api_key = getOpenAIKey()
  headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
  }

  contents = []
  user_prompt = {
    "type": "text",
    "text": nba_prompt
  }
  contents.append(user_prompt)
  for i, img_path in enumerate(image_paths):
    base64_image = encode_image(img_path)
    cur_img = {
      "type": "image_url",
      "image_url": {
        "url": f"data:image/jpeg;base64,{base64_image}",
        "detail": "low"
      } 
    }
    contents.append(cur_img)

  payload = {
    "model": "gpt-4-vision-preview",
    "messages":[
      {
        "role": "user",
        "content": contents
      }
    ],
    "max_tokens": 600
  }

  response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
  if response.status_code != 200:
    return False, response
  output = json.loads(response.text)
  return True, output['choices'][0]['message']['content']


def pathToPics(path):
  """Given a path to png files glob, return all pngs matching regex."""
  pics = glob.glob(path)
  pics_sort = []
  for p in pics:
    number = int(re.findall('\d+', p)[0])
    pics_sort.append((p, number))
  pics_sort = sorted(pics_sort, key=lambda x: x[1]) 
  return [x[0] for x in pics_sort]


def secondsToTimestamp(seconds):
  """Converts seconds to hour:minute:seconds."""
  return str(datetime.timedelta(seconds=seconds))


def runSubprocessCmd(cmd: str):
  return subprocess.Popen([cmd], shell=True).wait()


def createVideoSnippet(start: int, end: int, input_path: str, output_dir: str, ext: str = 'webm'):
  """Given start, end and input file, return success, created snippet path tuple."""
  fstart = secondsToTimestamp(start)
  fend = secondsToTimestamp(end)
  filename = f'snippet_{start}_{end}.{ext}'
  output_path = os.path.join(output_dir, filename)
  ffmpeg_cmd = f'ffmpeg -ss {fstart} -to {fend} -i {input_path} -c copy {output_path}' 
  output = runSubprocessCmd(ffmpeg_cmd)
  if output != 0:
    print(f'Error for cmd: {ffmpeg_cmd}')
    return False, None
  return True, output_path


def createImagesFromSnippet(input_path: str, tempdir: str, ext: str = 'png'):
  """Convert video to png with ffmpeg."""
  out_png = f'out_%d.{ext}'
  out_png = os.path.join(tempdir, out_png)
  ffmpeg_cmd = f'ffmpeg -i {input_path} -vf fps=1 -s 512x512 {out_png}'
  output = runSubprocessCmd(ffmpeg_cmd)
  if output != 0:
    print(f'Error for cmd: {ffmpeg_cmd}')
    return False
  return True


async def imagesToGPT(tempdir: str):
  img_path = os.path.join(tempdir, '*.png')
  image_paths = pathToPics(img_path)
  success, output = imagePathsToGPT4(image_paths)
  if success:
    return True, output
  print('GPT4 Error: ', output)
  return False, None
  

def snippetsToPngsFn(snip: Snippet):
  """parallel convert video to pictures."""
  tempdir = snip.tempdir
  snippet_path = snip.snippet_path
  return createImagesFromSnippet(snippet_path, tempdir.name)


async def snippetsToGPTFn(snips: List[Snippet]):
  # success, gpt_output = imagesToGPT(tempdir.name)
  tasks = [imagesToGPT(s.tempdir.name) for s in snips]
  return await asyncio.gather(*tasks)


def mergeSnippetsToVideo(snips: List[Snippet], tempdir: str, ext: str = 'webm'):
  snip_vids = [f"file \'{s.snippet_path}\'" for s in snips]
  snip_file = os.path.join(tempdir, 'snip_file.txt')
  with open(snip_file, 'w') as fd:
    fd.write('\n'.join(snip_vids))
  merged_path = os.path.join(tempdir, f'merged.{ext}')
  ffmpeg_cmd = f'ffmpeg -f concat -safe 0 -i {snip_file} -c copy {merged_path}'
  output = runSubprocessCmd(ffmpeg_cmd)
  if output != 0:
    print(f'Error for cmd: {ffmpeg_cmd}')
    return False, None
  return True, merged_path


fake = generateFakeSamples()
input_path = '/home/lodi/mindsdb/warriors_game/warriors_game.webm'
snippets = []
for f in fake:
  tempdir = tempfile.TemporaryDirectory()
  success, snippet_path = createVideoSnippet(f['start'], f['end'], input_path, tempdir.name)
  if not success:
    print('createVideoSnippet returned False!!!! FUCKKKKKK')
    raise ValueError("FUCKKKK")
  snip = Snippet(
    tempdir=tempdir,
    snippet_path=snippet_path,
    start=f['start'],
    whisper_text=f['text'])
  snippets.append(snip)

with multiprocessing.Pool() as pool:
  results = pool.map(snippetsToPngsFn, snippets)

results = asyncio.run(snippetsToGPTFn(snippets))
for (sucess, text), snip in zip(results, snippets):
  if success:
    snip.gptv_text = text

tempdir = tempfile.TemporaryDirectory()
success, merged_path = mergeSnippetsToVideo(snippets, tempdir.name)


