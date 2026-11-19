from dataclasses import dataclass


@dataclass
class TachiScore:
    score: int = None
    lamp: str = None
    matchType: str = "tachiSongID"
    identifier: str = None
    difficulty: str = None
    timeAchieved: int = None
    comment: str = None
    optional: dict = None

