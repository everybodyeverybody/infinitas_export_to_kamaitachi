import csv
import datetime
import json
import logging
import sys
from typing import Any
from zoneinfo import ZoneInfo

from . import constants as CONSTANTS
from . import kamaitachi_client
from .local_dataclasses import TachiScore


def translate_konami_clear_to_tachi_clear(clear: str):
    mapping = {
        "ASSIST CLEAR": "ASSIST CLEAR",
        "EASY CLEAR": "EASY CLEAR",
        "CLEAR": "CLEAR",
        "HARD CLEAR": "HARD CLEAR",
        "EX HARD CLEAR": "EX HARD CLEAR",
        "FULLCOMBO CLEAR": "FULL COMBO",
        "FAILED": "FAILED",
    }
    return mapping[clear]


def convert_score_chunk_to_tachi_score(
    difficulty: str, tachi_song_id: str, chunk: list[str]
) -> TachiScore | None:
    konami_date_format = "%Y-%m-%d %H:%M"
    score_str, updated, miss_count, clear, _, _ = chunk
    if clear == "NO PLAY":
        return None
    tachi_clear = translate_konami_clear_to_tachi_clear(clear)
    if miss_count == "---":
        miss_count = "0"
    optional_bp = {"bp": int(miss_count)}
    comment = "infinitas export to kamaitachi"
    score = int(score_str)
    # TODO: figure out time zones
    updated_datetime = datetime.datetime.strptime(updated, konami_date_format).replace(
        tzinfo=ZoneInfo("Japan")
    )
    tachi_time_achieved_ms = int(updated_datetime.timestamp() * 1000)
    score_entry = TachiScore(
        score=score,
        lamp=tachi_clear,
        identifier=tachi_song_id,
        difficulty=difficulty,
        timeAchieved=tachi_time_achieved_ms,
        comment=comment,
        optional=optional_bp,
    )
    return score_entry


def read_scores_from_csv(song_list: dict[tuple[str, str] : str]) -> list[TachiScore]:
    scores = []
    if len(sys.argv) < 2:
        # TODO: have this read multiple csvs with argparse
        raise RuntimeError("need the path of a infinitas csv export file")
    data = sys.argv[1]
    log.info(f"Reading konami infinitas score info from {data}")
    score_chunk_size = 6
    score_start_column = 3
    score_order = ["BEGINNER", "NORMAL", "HYPER", "ANOTHER", "LEGGENDARIA"]
    with open(data) as file_reader:
        csv_reader = csv.reader(file_reader)
        row_count = 0
        for row in csv_reader:
            row_count += 1
            if row_count == 1:
                # skip header
                continue
            title = row[1]
            artist = row[2]
            song_lookup_tuple = (
                title,
                artist,
            )
            if song_lookup_tuple not in song_list:
                raise RuntimeError(
                    f"could not find {song_lookup_tuple} in kamaitachi data"
                )
            tachi_song_id = song_list[song_lookup_tuple]
            for difficulty_index, score_index in enumerate(
                range(score_start_column, len(row), score_chunk_size)
            ):
                chunk = row[score_index : score_index + score_chunk_size]
                difficulty = score_order[difficulty_index]
                score = convert_score_chunk_to_tachi_score(
                    difficulty, tachi_song_id, chunk
                )
                if not score:
                    continue
                scores.append(score)
    return scores


def get_song_list() -> dict[tuple[str, str] : str]:
    log.info("Getting song data from Tachi github")
    song_list = {}
    kamaitachi_songlist: list[dict[str, Any]] = (
        kamaitachi_client.download_kamaitachi_song_list()
    )
    for entry in kamaitachi_songlist:
        title_artist_tuple = (entry["title"], entry["artist"])
        song_list[title_artist_tuple] = entry["id"]

    normalized_json = CONSTANTS.DATA_DIR / "normalize.json"
    with open(normalized_json) as reader:
        normalized_json = json.load(reader)
    for entry in normalized_json:
        tachi_tuple = (entry["kamaitachi_title"], entry["kamaitachi_artist"])
        if tachi_tuple in song_list:
            konami_tuple = (
                entry["konami_title"],
                entry["konami_artist"],
            )
            song_list[konami_tuple] = song_list[tachi_tuple]
    return song_list


def main():
    song_list = get_song_list()
    scores = read_scores_from_csv(song_list)
    kamaitachi_client.infinitas_scores(scores)


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
main()
