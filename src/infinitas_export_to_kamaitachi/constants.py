import os
from pathlib import Path

BASE_DIR = Path(os.getenv("PWD", default="./"))
DATA_DIR = BASE_DIR / Path("data")
TACHI_API_TOKEN = os.getenv("TACHI_API_TOKEN")
KAMAITACHI_API_URL = "https://kamai.tachi.ac/ir/direct-manual/import"
KAMAITACHI_SONG_LIST_URL = "https://raw.githubusercontent.com/zkldi/Tachi/refs/heads/main/db/seeds/songs-iidx.json"
