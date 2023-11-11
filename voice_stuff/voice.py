import subprocess
import os
from openai import OpenAI
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

summaries = [
  {
    "start": 73,
    "end": 84,
    "original": " And it's Andrew Wiggins gets inside and gets the bucket  To me. He's the key they need  25 from him tonight to be able to score enough to win",
    "new": "The ball is inbounded and the offensive team starts up the court. They're moving with urgency, looking to exploit the defense early in the shot clock. A player drives hard to the rim\u2014oh, a quick dish to his teammate! The teammate goes up for the layup amidst the defenders, and it's good! Two points! Quick transition defense now as the other team races back to start their offense. What a smooth play!"
  },
  {
    "start": 142,
    "end": 160,
    "original": " James to Davis Davis goes right at Draymond Green again. Well defended Davis thought he was hit  Lakers have not been dominant at home this season clearly a lot of that had to do with missing the two players",
    "new": "Lakers on the attack, dribbling out on the perimeter. Sudden drive towards the basket, a quick pass, and the shooter goes for a three-point shot from the corner. It's up in the air... and it's good! Count it! Three points as the Lakers close the gap! What a smooth execution and a fantastic finish from downtown!"
  },
  {
    "start": 251,
    "end": 270,
    "original": " James to Davis  James with the tip in with the left hand and Frank Vogel's irate. He thought David Davis got fouled again  I thought it was a good block  Curry flips it up shot too strong Looney back out to Baysmore wide open three",
    "new": "And here we go! The Lakers are on the offense. A quick hand-off, he drives through, slices past the defense, up for the layup - and it\u2019s good! Two points! Unstoppable move to the basket! What a play! The Lakers cut the deficit, now trailing by 5! The Warriors retrieve the ball, looking to answer back swiftly. Let\u2019s see how they'll respond to that aggressive offensive play!"
  },
  {
    "start": 2037,
    "end": 2051,
    "original": "Boy active hands again from the Warriors pool explodes to the rim and finishes",
    "new": ""
  },
  {
    "start": 2766,
    "end": 2778,
    "original": "green try to jam it James and drumming right there James down the other end lamp lock a foul count it and one still went down and a chance for a three-point",
    "new": "In the paint, he goes up strong\u2014denied! Blocked, but he stays with it, grabs the loose ball! Puts it back up and in for the score\u2014resilience on the inside! Fighting through the contact and not giving up on the play. That's determination! And now a quick nod, acknowledging the effort and maybe a little self-motivation. The scoreboard ticks. This is what basketball grit is all about!"
  },
  {
    "start": 4233,
    "end": 4244,
    "original": "Got it! Anthony Davis, his first three-pointer of the night. He was 0 for 5, and it's back to a five-point Laker lead.",
    "new": "It's a clutch three-pointer! Player #3 in yellow sets up beyond the arc, takes the shot\u2014swish! That's a big-time bucket, stretching the lead to five. The crowd erupts and the momentum is with the yellow team as the defense now has to regroup!"
  },
  {
    "start": 4530,
    "end": 4545,
    "original": "Schroeder drives inside Caruso, missed the layup. Curry the rebound.",
    "new": "Lakers advancing, LeBron passes to the wing. Quick back pass to LeBron, he drives in, goes airborne, under heavy pressure, and lays it in for a SPECTACULAR finish! The crowd erupts as LeBron delivers once again! What a play!"
  },
  {
    "start": 5068,
    "end": 5081,
    "original": "Each team with one timeout left and as Mark said both teams in the penalty. Baysmore to pull.",
    "new": "The game is tied at 98 with just over two minutes left on the clock. A player in yellow dribbles past half-court, closely guarded by a player in black. He cuts left around a teammate's screen, accelerates towards the basket, evades another defender, and lays the ball up. It's a smooth, calculated move through traffic\u2014basket counts! Excitement builds as the home crowd erupts. The yellow team takes the lead\u2014a critical moment as the clock ticks down!"
  },
  {
    "start": 5115,
    "end": 5127,
    "original": "Inside Davis for the slam. Lakers back up to with a minute",
    "new": "Ball inbounded, the pressure's on. Quick pass to the key player\u2014he's sizing up the defense. There's a drive down the baseline, fending off defenders. Oh, a stunning pass back out! He shakes off his opponent, leaps, and... YES! A picture-perfect jump shot! The ball sails through the hoop! That's two points and the crowd goes wild! The defense looks stunned as the home team takes the lead with just over 90 seconds to play! What a moment!"
  },
  {
    "start": 5228,
    "end": 5239,
    "original": "Curry sets leans in. Knocked away get it back from Curry shot clock at seven. And. The Lakers are up two to three. And.",
    "new": "The ball swings out to the top! It's a hard drive to the basket! The defense collapses! A no-look dish to the right corner! The defender scrambles! The corner three is up... and it's good! What a clutch bucket! The lead extends, a critical moment in this nail-biter of a game!"
  }
]

#  cut file to n (5) seconds
def cutMp3ToTime(input_mp3: str, output_mp3: str, seconds: int):
  ffmpeg_cmd = f'ffmpeg -ss 0 -i {input_mp3} -t {seconds} -c copy {output_mp3}'
  output = runSubprocessCmd(ffmpeg_cmd)
  if output != 0:
    print(f"Error for cmd: {ffmpeg_cmd}")
    return False
  return True


def addSilenceToMp3(input_mp3: str, output_mp3: str, seconds: int):
  ffmpeg_cmd = f'ffmpeg -i {input_mp3} -af "apad=pad_dur={seconds}" {output_mp3}'
  output = runSubprocessCmd(ffmpeg_cmd)
  if output != 0:
    print(f"Error for cmd: {ffmpeg_cmd}")
    return False
  return True


def runSubprocessCmd(cmd: str):
  return subprocess.Popen([cmd], shell=True).wait()


def getMp3Time(input_mp3: str): 
  cmd = f'ffmpeg -i {input_mp3} -f null -'
  out = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
  err, comm = out.communicate() 
  mtime = comm.find(b'time=') + len('time=')
  mend = comm.find(b' ', mtime)
  mp3_time = comm[mtime:mend]
  h, m, s = mp3_time.decode('utf-8').split(':')
  return int(s.split('.')[0])

input_dir = '/home/lodi/mindsdb/audios'
for s in summaries:
  start = s['start']
  end = s['end']
  timelimit = end - start
  curfile = f"narration-{start}.mp3"
  curfile = os.path.join(input_dir, curfile)
  mp3_time = getMp3Time(curfile)
  outfinal = f"narration_final_{start}.mp3"
  outfinal = os.path.join(input_dir, outfinal)
  if mp3_time > timelimit:
    to_cut = mp3_time - timelimit
    cutMp3ToTime(curfile, outfinal, timelimit)
  else:
    to_add = timelimit - mp3_time
    addSilenceToMp3(curfile, outfinal, to_add)
