
import json
import time
from typing import Any
import requests
from datetime import datetime

repo = "himangshu147-git/krypton-Rewrite"
def get_latest_change():
    r = requests.get(f"https://api.github.com/repos/{repo}/commits/master?per_page=1")
    data = r.json()
    sha = data['sha']
    url = data['html_url']
    author = data['commit']['author']['name']
    message = data['commit']['message']
    time = data['commit']['author']['date']
    dt = datetime.fromisoformat(time[:-1])
    timestamp = dt.timestamp()
    return sha, url, message, author, timestamp

def generate_thumbnail(identifier):
    r = requests.get(f"https://embed.spotify.com/oembed/?url=spotify:track:{identifier}")
    return r.json()["thumbnail_url"]

def format_string(number: int, value: str) -> str:
    """
    "Humanizes" a name, Ex: 1 time, 2 times
    """
    return f"{number} {value}" if number == 1 else f"{number} {value}s"


def format_list(item_list: list[Any], *, seperator: str = ", ", last: str = "and") -> str | list[Any]:
    """
    Makes a list easier to read
    """
    if not item_list:
        return item_list
    if len(item_list) == 1:
        return item_list[0]
    if len(item_list) == 2:
        return f" {last} ".join(item_list)
    return f"{seperator.join(str(item) for item in item_list[:-1])} {last} {item_list[-1]}"


class Timer:
    __slots__ = ("start_time", "end_time")

    def __init__(self) -> None:
        self.start_time: float | None = None
        self.end_time: float | None = None

    def __enter__(self):
        self.start()
        return self

    async def __aenter__(self):
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.stop()

    async def __aexit__(self, exc_type, exc_value, exc_traceback) -> None:
        self.stop()

    def start(self) -> None:
        self.start_time = time.perf_counter()

    def stop(self) -> None:
        self.end_time = time.perf_counter()

    def __str__(self) -> str:
        return str(self.total_time)

    def __int__(self) -> int:
        return int(self.total_time)

    def __repr__(self) -> str:
        return f"<Timer time={self.total_time}>"

    @property
    def total_time(self) -> float:
        if self.start_time is None:
            raise ValueError("Timer has not been started")
        if self.end_time is None:
            raise ValueError("Timer has not been stopped")
        return self.end_time - self.start_time


# The following code is not mine Thanks Axel :)
# https://github.com/Axelancerr/Life/blob/508e1e9c5b02f56f76a53a2cfd9b521ddacdd8f3/Life/utilities/utils.py#L51-L64
def format_seconds(seconds: float, *, friendly: bool = False) -> str:

    seconds = round(seconds)

    minute, second = divmod(seconds, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)

    days, hours, minutes, seconds = (
        round(day),
        round(hour),
        round(minute),
        round(second),
    )

    if friendly:
        day = f"{days}d " if days != 0 else ""
        hour = f"{hours}h " if hours != 0 or days != 0 else ""
        minsec = f"{minutes}m {seconds}s"
        return f"{day}{hour}{minsec}"
    day = f"{days:02d}:" if days != 0 else ""
    hour = f"{hours:02d}:" if hours != 0 or days != 0 else ""
    minsec = f"{minutes:02d}:{seconds:02d}"
    return f"{day}{hour}{minsec}"


def format_times(number: int) -> str:
    if number == 1:
        return "once"
    elif number == 2:
        return "twice"
    return f"{number} times"
