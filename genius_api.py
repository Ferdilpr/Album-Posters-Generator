import lyricsgenius
import paths

TOKEN = "QfowmHjM3hdXb8N9pGARnSh1DDVwATgl_VZRaWEIUjrzvkCd_1OyuGDRe18xvDWr"


def get_lyrics(title: str, artist_name: str = ""):
    client = lyricsgenius.Genius(TOKEN)
    song = client.search_song(title, artist_name)
    lyrics = str(song.lyrics)
    lyrics = lyrics.replace("\n\n", "\n")
    lyrics = lyrics.split("\n")
    lyrics.pop(0)
    return lyrics
