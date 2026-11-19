import dataclasses
import json
import logging
import time
from pathlib import Path
from typing import Any

import requests

from . import constants as CONSTANTS
from .local_dataclasses import TachiScore

log = logging.getLogger(__name__)


def submit_score_request(scores: dict[str, Any]) -> None:
    log.info("submitting scores to kamaitachi")
    headers = {"Authorization": f"Bearer {CONSTANTS.TACHI_API_TOKEN}"}
    response = requests.post(CONSTANTS.KAMAITACHI_API_URL, headers=headers, json=scores)
    if response.status_code in [200, 202]:
        response_json = response.json()
        queue_url = response_json["body"]["url"]
        while True:
            queue_response = requests.get(queue_url, headers=headers)
            log.info(queue_response.status_code)
            log.info(queue_response.text)
            if queue_response.status_code not in [200, 202]:
                break
            status = queue_response.json()["body"]["importStatus"]
            if status == "completed":
                break
            time.sleep(5)
    else:
        log.info(f"Submit score request failed: {response.status_code} {response.text}")


def infinitas_scores(tachi_scores: list[TachiScore], play_type: str = "SP"):
    if not CONSTANTS.TACHI_API_TOKEN:
        log.error(
            "Kamaitachi export failed, must set TACHI_API_TOKEN in env for script"
        )
        return

    scores_to_submit = {"meta": {"game": "iidx", "service": "infinitas"}, "scores": []}
    if play_type == "SP":
        scores_to_submit["meta"]["playtype"] = "SP"
    else:
        scores_to_submit["meta"]["playtype"] = "DP"
    for score in tachi_scores:
        scores_to_submit["scores"].append(dataclasses.asdict(score))
    submit_score_request(scores_to_submit)


def download_kamaitachi_song_list() -> dict[str, Any]:
    log.info("Downloading kamaitachi song list")
    kamaitachi_json_file = CONSTANTS.DATA_DIR / Path("kamaitachi-iidx-songs.json")
    if not kamaitachi_json_file.exists():
        with open(kamaitachi_json_file, "wt") as json_writer:
            song_list_json_response = requests.get(CONSTANTS.KAMAITACHI_SONG_LIST_URL)
            if song_list_json_response.status_code == 200:
                json_writer.write(song_list_json_response.text)
                return song_list_json_response.json()
            else:
                raise RuntimeError(
                    f"could not download kamaitachi source from "
                    f"{CONSTANTS.KAMAITACHI_SONG_LIST_URL} "
                    f"code: {song_list_json_response.status_code} "
                    f"error: {song_list_json_response.text}"
                )
    else:
        with open(kamaitachi_json_file, "rt") as reader:
            return json.load(reader)
