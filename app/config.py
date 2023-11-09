import pathlib

CACHE_DIR = "/cache"
# Where downloaded podcasts are stored, by guid hash.
# Mostly .mp3 files 50-100MiB.
RAW_AUDIO_DIR = pathlib.Path(CACHE_DIR, "raw_audio")
CHUNKED_AUDIO_DIR = pathlib.Path(CACHE_DIR, "chunked_audio")
# Stores metadata of individual podcast episodes as JSON.
PODCAST_METADATA_DIR = pathlib.Path(CACHE_DIR, "podcast_metadata")
# Completed episode transcriptions. Stored as flat files with
# files structured as '{guid_hash}-{model_slug}.json'.
TRANSCRIPTIONS_DIR = pathlib.Path(CACHE_DIR, "transcriptions")
# Searching indexing files, refreshed by scheduled functions.
SEARCH_DIR = pathlib.Path(CACHE_DIR, "search")
VIDEO_DIR = pathlib.Path(CACHE_DIR, "videos")

AUDIO_CHUNK_SIZE = 60
# Location of web frontend assets.
ASSETS_PATH = pathlib.Path(__file__).parent / "frontend" / "dist"
