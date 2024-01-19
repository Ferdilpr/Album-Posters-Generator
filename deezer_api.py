import shutil
import time
from datetime import datetime

from PIL import Image

import requests
import paths
import math
import secrets
import webbrowser


def search_track(query: str, download_cover: bool = False):
    params = {"q": query}
    response_raw = requests.get(url=paths.track_search_domain, params=params)
    response = response_raw.json()
    result_id = str(response["data"][0]["id"])
    return fetch_track(result_id, download_cover=download_cover)


def fetch_track(track_id, object=None, album_contributors=None, download_cover: bool = False):
    token = get_token()
    access_token = {"access_token": token}

    response_raw = requests.get(url=paths.track_domain + str(track_id), params=access_token)
    response = response_raw.json()

    title = response["title"]
    artist_name = response["artist"]["name"]

    try:
        contributors = []
        for contributor in response["contributors"]:
            contributors.append(Artist(
                contributor["id"],
                contributor["name"]
            ))
    except KeyError:
        contributors = [Artist(
            response["artist"]["name"],
            response["artist"]["name"]
        )]

    try:
        artist_id = response["artist"]["id"]
    except KeyError:
        artist_id = None

    try:
        cover = response["album"]["cover_xl"]
    except KeyError:
        cover = None

    track_object = Track(
        response["id"],
        title,
        response["duration"],
        response["explicit_lyrics"],
        Artist(
            artist_id,
            artist_name
        ),
        response["album"]["id"],
        response["album"]["title"],
        cover,
        contributors=contributors
    )

    if object is not None:
        object.title = format_title(track_object, album_contributors)
    else:
        format_title(track_object, album_contributors)

    if download_cover:
        track_object.fetch_cover()

    return track_object


def format_title(track_object, album_contributors=None):
    if album_contributors is None:
        album_contributors = [track_object.artist]
    if track_object.contributors is None:
        return

    formatted_title = str(track_object.title.rsplit(" (feat")[0])
    formatted_title = str(formatted_title.rsplit(" (Extrait")[0])
    if len(track_object.contributors) > len(album_contributors):
        formatted_title = formatted_title + " (ft."
        contributors = []
        for i in range(1, len(track_object.contributors)):
            if track_object.contributors[i].name not in contributors and \
                    track_object.contributors[i].name not in (artist.name for artist in album_contributors):
                contributors.append(track_object.contributors[i].name)
        for contributor in contributors:
            formatted_title = formatted_title + " " + contributor + ","
        formatted_title = formatted_title.removesuffix(",")
        formatted_title = formatted_title + ")"
    track_object.title = formatted_title

    return formatted_title


class Media:
    def __init__(self):
        self.id = None
        self.cover = None
        self.cover_link = None
        self.file_name = None
        self.artist = None
        self.title = None
        self.cover_url = None

    def fetch_cover(self):
        file_name = self.title + " - " + self.artist.name + ".jpg"
        self.file_name = file_name
        self.cover_link = paths.download_directory + file_name

        try:
            self.cover = Image.open(self.cover_link)
        except IOError:
            if self.cover_url is not None:
                image_response = requests.get(self.cover_url, stream=True)
                with open(paths.download_directory + file_name, "wb") as f:
                    shutil.copyfileobj(image_response.raw, f)
            else:
                file_name = input(
                    "\n Aucune cover n'est renseignée pour l'instant, téléchargez-en une dans le répertoire " +
                    paths.download_directory + " puis entrez le nom du fichier. \n > ")

            self.file_name = file_name
            self.cover_link = paths.download_directory + file_name
            self.cover = Image.open(self.cover_link)

            return self.file_name, self.cover_link, self.cover

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False


class Artist:
    def __init__(
            self,
            id,
            name
    ):
        self.id = id
        self.name = name

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.id == other.id
        else:
            return False


class Track(Media):
    def __init__(
            self,
            id,
            title: str,
            duration_raw: int,
            explicit_lyrics: bool,
            artist: Artist,
            album_id,
            album_name: str,
            cover_url: str,
            cover_link: str = None,
            file_name: str = None,
            contributors: list[Artist] = None,
            album_contributors: list[Artist] = None
    ):
        super().__init__()
        self.id = id
        self.title = title
        self.duration_raw = duration_raw
        self.explicit_lyrics = explicit_lyrics
        self.artist = artist
        self.album_id = album_id
        self.album_name = album_name
        self.cover_url = cover_url
        self.contributors = contributors
        self.cover_link = cover_link
        self.file_name = file_name
        self.album_contributors = album_contributors

        if cover_link is None:
            self.cover = None
        else:
            self.cover = Image.open(cover_link).convert("RGB")

        minutes = math.floor(duration_raw / 60)
        seconds = duration_raw - minutes * 60
        if seconds >= 10:
            seconds_formated = str(seconds)
        else:
            seconds_formated = "0" + str(seconds)
        self.duration = str(minutes) + ":" + seconds_formated

    def populate(self):
        fetch_track(self.id, self)

    def format_title(self):
        fetch_track(self.id, self, self.album_contributors)

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.title == other.title and self.artist.name == other.artist.name
        else:
            return False


class Album(Media):
    def __init__(
            self,
            id,
            title: str,
            release_date: str,
            tracks_count: int,
            duration: int,
            tracks: list[Track],
            artist: Artist,
            contributors: list[Artist],
            label: str,
            cover_url: str,
            cover_link: str = None,
            file_name: str = None
    ):
        super().__init__()
        self.id = id
        self.title = title
        self.release_date = release_date
        self.tracks_count_raw = tracks_count
        self.duration_raw = duration
        self.tracks = tracks
        self.artist = artist
        self.contributors = contributors
        self.label = label
        self.cover_url = cover_url
        self.cover_link = cover_link
        self.file_name = file_name
        if cover_link is None:
            self.cover = None
        else:
            self.cover = Image.open(cover_link).convert("RGB")

        minutes = math.floor(self.duration_raw / 60)
        seconds = self.duration_raw - minutes * 60
        if seconds >= 10:
            seconds_formated = str(seconds)
        else:
            seconds_formated = "0" + str(seconds)
        self.duration = str(minutes) + ":" + seconds_formated

        self.tracks_count = str(self.tracks_count_raw) + " titres"

        self.artists_formatted = ", ".join(artist.name for artist in self.contributors)


class DeezerUser:
    def __init__(
            self,
            id,
            name,
            email,
            inscription_date,
            picture_url,
            picture_link=None
    ):
        self.id = id
        self.name = name
        self.email = email
        self.inscription_date = inscription_date
        self.picture_url = picture_url
        self.picture_link = picture_link


class Playlist:
    def __init__(
            self,
            id,
            title,
            duration,
            nb_tracks,
            fans,
            picture,
            creation_date,
            creator_id,
            creator_name,
            tracks: list[Track]
    ):
        self.id = id
        self.title = title
        self.duration = duration
        self.nb_tracks = nb_tracks
        self.fans = fans
        self.creation_date = creation_date
        self.creator_id = creator_id
        self.picture = picture
        self.creator_name = creator_name
        self.tracks = tracks


def search_album(query: str, download_cover: bool = False):
    params = {"q": query}
    response_raw = requests.get(url=paths.album_search_domain, params=params)
    response = response_raw.json()
    result_id = str(response["data"][0]["id"])
    album = fetch_album(result_id, download_cover=download_cover)
    return album


def fetch_album(album_id, download_cover: bool = False):
    response_raw = requests.get(url=paths.album_domain + str(album_id))
    response = response_raw.json()

    contributors = []
    for contributor in response["contributors"]:
        contributors.append(Artist(
            contributor["id"],
            contributor["name"]
        ))

    release_date_raw = response["release_date"]
    release_date = datetime.strptime(release_date_raw, "%Y-%m-%d").strftime('%d/%m/%Y')

    tracks = get_tracks_from_list(response["tracks"]["data"], contributors)

    album = Album(
        response["id"],
        response["title"],
        release_date,
        response["nb_tracks"],
        response["duration"],
        tracks,
        Artist(
            response["artist"]["id"],
            response["artist"]["name"]
        ),
        contributors,
        response["label"],
        response["cover_xl"]
    )

    if download_cover:
        album.fetch_cover()

    return album


def get_token():
    with open("deezer_token") as file:
        token = file.read()
    if token != "":
        return token
    else:
        webbrowser.open(
            paths.get_code_domain + "?" +
            "app_id=" + secrets.app_id +
            "&redirect_uri=" + paths.deezer_api_redirect +
            "&perms=basic_access,email,offline_access,manage_library,manage_community,delete_library,listening_history"
        )
        code = requests.get(paths.deezer_get_code_page).text
        while requests.get(paths.deezer_get_code_page).text == code:
            time.sleep(0.05)
        code = requests.get(paths.deezer_get_code_page).text

        token = requests.get(
            paths.get_token_url + "?" +
            "app_id=" + secrets.app_id +
            "&secret=" + secrets.app_secret +
            "&code=" + code
        ).text

        token = token.rsplit("&")[0]
        token = token.removeprefix("access_token=")

        with open("deezer_token", "w") as file:
            file.write(token)

        return token


def fetch_user(user_id="me"):
    token = get_token()
    access_token = {"access_token": token}

    user = requests.get(paths.user_domain + user_id, params=access_token).json()

    return DeezerUser(
        user["id"],
        user["name"],
        user["email"],
        user["inscription_date"],
        user["picture_xl"]
    )


def fetch_user_playlists(user_id="me"):
    token = get_token()
    access_token = {"access_token": token}

    playlists = requests.get(paths.user_domain + user_id + "/playlists", params=access_token)
    playlists = playlists.json()

    elements = []
    for playlist in playlists["data"]:
        elements.append(fetch_playlist(playlist["id"]))

    return elements


def get_tracks_from_list(list, album_contributors=None, backup_picture=None):
    tracks = []
    for track in list:
        try:
            cover = track["album"]["cover_xl"]
        except KeyError:
            cover = backup_picture

        try:
            artist_id = track["artist"]["id"]
        except KeyError:
            artist_id = None

        tracks.append(Track(
            track["id"],
            track["title"],
            track["duration"],
            track["explicit_lyrics"],
            Artist(
                artist_id,
                track["artist"]["name"]
            ),
            track["album"]["id"],
            track["album"]["title"],
            cover,
            album_contributors=album_contributors
        ))
    return tracks


def get_albums_from_list(list, backup_picture=None):
    albums = []
    for album in list:
        albums.append(Album(
            album["id"],
            album["title"],
            None,
            None,
            60,
            None,
            Artist(
                album["artist"]["id"],
                album["artist"]["name"]
            ),
            None,
            None,
            album["cover_xl"]
        ))
    return albums


def find(list: list[Artist | Album | Track | Playlist], name: str = None, id: str | int = None):
    for element in list:
        if id is None:
            if isinstance(element, Artist):
                if element.name == name:
                    return element
            if isinstance(element, Album) or isinstance(element, Track) or isinstance(element, Playlist):
                if element.title == name:
                    return element
        if name is None:
            if element.id == id:
                return element
    RuntimeError(ValueError)


def get_artists_from_list(list):
    artists = []
    for artist in list:
        artists.append(Artist(
            artist["id"],
            artist["name"]
        ))
    return artists


def fetch_playlist(playlist_id):
    token = get_token()
    access_token = {"access_token": token, "limit": 1000}

    playlist = requests.get(paths.playlist_domain + str(playlist_id), params=access_token)
    playlist = playlist.json()

    tracks = get_tracks_from_list(playlist["tracks"]["data"], playlist["picture_xl"])

    playlist_object = Playlist(
        playlist["id"],
        playlist["title"],
        playlist["duration"],
        playlist["nb_tracks"],
        playlist["fans"],
        playlist["picture_xl"],
        playlist["creation_date"],
        playlist["creator"]["id"],
        playlist["creator"]["name"],
        tracks
    )

    return playlist_object


def fetch_user_charts():
    token = get_token()
    access_token = {"access_token": token}

    charts = requests.get(paths.user_domain + "me/charts", params=access_token)
    charts = charts.json()

    return get_tracks_from_list(charts["data"])


def fetch_charts():
    charts = requests.get(paths.charts_domain).json()
    tracks = get_tracks_from_list(charts["tracks"]["data"])
    albums = get_albums_from_list(charts["albums"]["data"])

    return tracks, albums


def fetch_user_history():
    token = get_token()
    access_token = {"access_token": token}

    history = requests.get(paths.user_domain + "me/history", params=access_token)
    history = history.json()

    return get_tracks_from_list(history["data"])


def fetch_user_artists(user_id="me"):
    token = get_token()
    params = {"access_token": token, "limit": 100}

    artists = requests.get(paths.user_domain + str(user_id) + "/artists", params=params)
    artists = artists.json()
    return get_artists_from_list(artists["data"])


def update_user_artists(source: list[Track], occurence_min=2):
    print("\n")
    print("-" * 100)
    token = get_token()
    artists = fetch_user_artists()
    artists_to_add = []
    for track in source:
        nb_artist = list((track_artist.artist for track_artist in source)).count(track.artist)
        if nb_artist > occurence_min and track.artist not in artists_to_add and type(track.artist.id) is int:
            artists_to_add.append(track.artist)
    artists_to_delete = []
    for artist in artists:
        if artist not in artists_to_add:
            artists_to_delete.append(artist)
        if artist in artists_to_add:
            artists_to_add.remove(artist)
    print("Deleting from artists favorites:")
    for artist in artists_to_delete:
        print(artist.name)
        requests.delete(paths.user_domain + "me/artists", params={"artist_id": str(artist.id), "access_token": token})
    print("-" * 50)
    print("Adding to artists favorites:")
    for artist in artists_to_add:
        print(artist.name)
        requests.post(paths.user_domain + "me/artists", params={"artist_id": str(artist.id), "access_token": token})


def playlist_to_playlist(source_playlist: Playlist, target_playlist: Playlist, artist: list[Artist] = None):
    token = get_token()
    tracks_to_add = []
    print("\n\n" + ("-" * 100) + "\n")
    print("Adding from " + source_playlist.title + " to " + target_playlist.title + ":")
    for track in source_playlist.tracks:
        if (track.id not in (target_track.id for target_track in target_playlist.tracks)
                and (artist is None or track.artist in artist)):
            tracks_to_add.append(track)
            print(track.title + " - " + track.artist.name)
    tracks_to_add = ",".join(str(track.id) for track in tracks_to_add)
    if tracks_to_add != "":
        params = {"access_token": token, "songs": tracks_to_add}
        requests.post(paths.playlist_domain + str(target_playlist.id) + "/tracks", params=params)


def azzed():
    playlists = fetch_user_playlists()
    time_playlist = find(playlists, id=11530560224)  # ⏳🍯🥶
    infinite_playlist = find(playlists, id=11086449142)  # ♾️🫥
    loved_playlist = find(playlists, name="Loved Tracks")
    new_gen_playlist = find(playlists, id=11246744764)  # 🤖👽👾
    turn_up_playlist = find(playlists, id=11704578004)  # 💥👹🦻
    winter_playlist = find(playlists, id=11813126801)  # ❄️🧊🌨️

    playlist_to_playlist(time_playlist, infinite_playlist)
    playlist_to_playlist(loved_playlist, time_playlist)
    playlist_to_playlist(loved_playlist, infinite_playlist)
    playlist_to_playlist(new_gen_playlist, infinite_playlist)
    playlist_to_playlist(turn_up_playlist, infinite_playlist)
    update_user_artists(time_playlist.tracks, 3)
