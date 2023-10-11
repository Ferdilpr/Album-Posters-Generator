import math

import requests
import shutil
from datetime import datetime

DOMAIN = "https://api.deezer.com/"
search_domain = DOMAIN + "search/album"
album_domain = DOMAIN + "album/"

absolute_directory = ""
download_directory = absolute_directory + "downloaded_covers/"


class Album:
    album_name = "Garçon"        # example values
    artist_name = "Luther"
    release_date = "01/01/2000"
    tracks_count_raw = 0
    tracks_count = "0 titres"
    duration_raw = 0
    duration = "0 min 00"
    cover_link = "download_directory/cover.jpg"
    tracks = [{"title": "ALAKAZAM", "note": "8.5/10"}, {"title": "Garçon", "note": "10/10"}]

    def __init__(self, _album_name=album_name, _release_date=release_date, _tracks_count_raw=tracks_count_raw,
                 _tracks_count=tracks_count, _duration_raw=duration_raw, _duration=duration, _cover_link=cover_link,
                 _tracks=tracks, _artist_name=artist_name):
        self.album_name = _album_name
        self.release_date = _release_date
        self.tracks_count_raw = _tracks_count_raw
        self.tracks_count = _tracks_count
        self.duration_raw = _duration_raw
        self.duration = _duration
        self.cover_link = _cover_link
        self.tracks = _tracks
        self.artist_name = _artist_name


def getAlbum(album_to_search):
    PARAMS = {"q": album_to_search}

    response_raw = requests.get(url=search_domain, params=PARAMS)
    response = response_raw.json()
    result_id = str(response["data"][0]["id"])

    response_raw = requests.get(url=album_domain + result_id)
    response = response_raw.json()

    album_name = response["title"]

    artist_name = response["artist"]["name"]
    if len(response["contributors"]) > 1:
        for i in range(1, len(response["contributors"])):
            artist_name = artist_name + ", " + response["contributors"][i]["name"]

    release_date_raw = response["release_date"]
    release_date = datetime.strptime(release_date_raw, "%Y-%m-%d").strftime('%d/%m/%Y')

    tracks_count_raw = int(response["nb_tracks"])
    tracks_count = str(tracks_count_raw) + " titres"
    if tracks_count_raw > 22:
        RuntimeError("The album contains too much tracks")

    duration_raw = response["duration"]
    minutes = math.floor(duration_raw / 60)
    seconds = duration_raw - minutes * 60
    if seconds >= 10:
        seconds_formated = str(seconds)
    else:
        seconds_formated = "0" + str(seconds)
    duration = str(minutes) + " min " + seconds_formated

    file_name = album_name + " - " + artist_name + ".jpg"
    image_response = requests.get(response["cover_xl"], stream=True)
    with open(download_directory + file_name, "wb") as f:
        shutil.copyfileobj(image_response.raw, f)

    cover_link = download_directory + file_name

    tracks = response["tracks"]["data"]

    album = Album(album_name, release_date, tracks_count_raw, tracks_count, duration_raw,
                  duration, cover_link, tracks, artist_name)
    return album
