import math
import string

import requests
import shutil
from datetime import datetime
from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance

DOMAIN = "https://api.deezer.com/"
search_domain = DOMAIN + "search/album"
album_domain = DOMAIN + "album/"
track_domain = DOMAIN + "track/"


class Setting:
    def __init__(
            self,
            background_blur_radius,
            poster_width_percentage,
            center_image_padding_sides_percentage,
            center_image_padding_top_percentage,
            background_darkness,
            default_album_name_font_size_percentage,
            default_artist_name_font_size_percentage,
            default_album_infos_font_size_percentage,
            resolution_multiplicator,
            center_image_shadow_blur,
            center_image_shadow_size_percentage,
            center_image_shadow_color,
            background_saturation

    ):
        self.background_blur_radius = background_blur_radius
        self.poster_width_percentage = poster_width_percentage
        self.center_image_padding_sides_percentage = center_image_padding_sides_percentage
        self.center_image_padding_top_percentage = center_image_padding_top_percentage
        self.background_darkness = background_darkness
        self.default_album_name_font_size_percentage = default_album_name_font_size_percentage
        self.default_artist_name_font_size_percentage = default_artist_name_font_size_percentage
        self.default_album_infos_font_size_percentage = default_album_infos_font_size_percentage
        self.resolution_multiplicator = resolution_multiplicator
        self.center_image_shadow_blur = center_image_shadow_blur
        self.center_image_shadow_size_percentage = center_image_shadow_size_percentage
        self.center_image_shadow_color = center_image_shadow_color
        self.background_saturation = background_saturation

    def copy(self,
             background_blur_radius=None,
             poster_width_percentage=None,
             center_image_padding_sides_percentage=None,
             center_image_padding_top_percentage=None,
             background_darkness=None,
             default_album_name_font_size_percentage=None,
             default_artist_name_font_size_percentage=None,
             default_album_infos_font_size_percentage=None,
             resolution_multiplicator=None,
             center_image_shadow_blur=None,
             center_image_shadow_size_percentage=None,
             center_image_shadow_color=None,
             background_saturation=None
             ):
        copy = self

        if background_blur_radius is not None:
            copy.background_blur_radius = background_blur_radius
        if poster_width_percentage is not None:
            copy.poster_width_percentage = poster_width_percentage
        if center_image_padding_sides_percentage is not None:
            copy.center_image_padding_sides_percentage = center_image_padding_sides_percentage
        if center_image_padding_top_percentage is not None:
            copy.center_image_padding_top_percentage = center_image_padding_top_percentage
        if background_darkness is not None:
            copy.background_darkness = background_darkness
        if default_album_name_font_size_percentage is not None:
            copy.default_album_name_font_size_percentage = default_album_name_font_size_percentage
        if default_artist_name_font_size_percentage is not None:
            copy.default_artist_name_font_size_percentage = default_artist_name_font_size_percentage
        if default_album_infos_font_size_percentage is not None:
            copy.default_album_infos_font_size_percentage = default_album_infos_font_size_percentage
        if resolution_multiplicator is not None:
            copy.resolution_multiplicator = resolution_multiplicator
        if center_image_shadow_blur is not None:
            copy.center_image_shadow_blur = center_image_shadow_blur
        if center_image_shadow_size_percentage is not None:
            copy.center_image_shadow_size_percentage = center_image_shadow_size_percentage
        if center_image_shadow_color is not None:
            copy.center_image_shadow_color = center_image_shadow_color
        if background_saturation is not None:
            copy.background_saturation = background_saturation

        return copy


class Album:

    def __init__(self, _album_name="", _release_date="", _tracks_count_raw=0,
                 _tracks_count="", _duration_raw="", _duration="", _cover_link="",
                 _tracks="", _artist_name="", _label=""):
        self.album_name = _album_name
        self.release_date = _release_date
        self.tracks_count_raw = _tracks_count_raw
        self.tracks_count = _tracks_count
        self.duration_raw = _duration_raw
        self.duration = _duration
        self.cover_link = _cover_link
        self.tracks = _tracks
        self.artist_name = _artist_name
        self.label = _label


def getAlbum(album_to_search):
    absolute_directory = ""
    download_directory = absolute_directory + "downloaded_covers/"

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

    if response["cover_xl"] is not None:
        file_name = album_name + " - " + artist_name + ".jpg"
        image_response = requests.get(response["cover_xl"], stream=True)
        with open(download_directory + file_name, "wb") as f:
            shutil.copyfileobj(image_response.raw, f)
    else:
        file_name = input(
            "\n Aucune cover n'est renseignée pour l'instant, téléchargez-en une dans le répertoire " + download_directory + " puis entrez le nom du fichier. \n > ")

    cover_link = download_directory + file_name

    tracks = []
    tracks_raw = response["tracks"]["data"]
    for track in tracks_raw:
        formatted_title = str(track["title"].rsplit(" (")[0])
        track_response_raw = requests.get(track_domain + str(track["id"]))
        track_response = track_response_raw.json()
        if len(track_response["contributors"]) > len(response["contributors"]):
            formatted_title = formatted_title + " (feat."
            contributors = []
            for i in range(len(response["contributors"]), len(track_response["contributors"])):
                if track_response["contributors"][i]["name"] != response["artist"]["name"] and \
                        track_response["contributors"][i]["name"] not in contributors:
                    contributors.append(track_response["contributors"][i]["name"])
            for contributor in contributors:
                formatted_title = formatted_title + " " + contributor + ","
            formatted_title = formatted_title.removesuffix(",")
            formatted_title = formatted_title + ")"
        track["title"] = formatted_title
        tracks.append(track)

    label = response["label"]

    album = Album(album_name, release_date, tracks_count_raw, tracks_count, duration_raw,
                  duration, cover_link, tracks, artist_name, label)
    return album


def blurred_backround(cover, blur_radius=25, width_ratio=70.7143, darkness=0.4,
                      resolution_multiplicator=1, saturation=1.75):
    cover = cover.resize(
        (math.ceil(cover.size[0] * resolution_multiplicator), math.ceil(cover.size[1] * resolution_multiplicator)))

    (cover_width, cover_height) = cover.size
    poster_width = math.ceil(cover_height * width_ratio / 100)
    left = (cover_width - poster_width) / 2
    right = cover_width - left
    (upper, lower) = (0, cover_height)

    poster = cover.filter(ImageFilter.GaussianBlur(blur_radius * resolution_multiplicator))
    poster = poster.crop((math.ceil(left), upper, math.ceil(right), lower))
    poster = ImageEnhance.Color(poster).enhance(saturation)
    black_background_profile = Image.new("RGB", poster.size, (0, 0, 0))
    poster = Image.blend(poster, black_background_profile, darkness)

    return poster
