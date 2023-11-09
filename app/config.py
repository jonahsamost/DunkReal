import pathlib

CACHE_DIR = "/cache"
NFS_NAME = "dunk-reel-cache-joao-test-2"

CHUNKED_AUDIO_DIR = pathlib.Path(CACHE_DIR, "chunked_audio")
TRANSCRIPTIONS_DIR = pathlib.Path(CACHE_DIR, "transcriptions")
VIDEO_DIR = pathlib.Path(CACHE_DIR, "videos")

AUDIO_CHUNK_SIZE = 60
# Location of web frontend assets.
ASSETS_PATH = pathlib.Path(__file__).parent / "frontend" / "dist"
