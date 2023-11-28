from __future__ import print_function
import math

import PIL
import requests
import shutil
from datetime import datetime
from PIL import Image, ImageFilter, ImageEnhance, ImageDraw, ImageFont
import json
from random import randrange

import genius_api
import google_photo_api
from classes import Font, Fonts, Album, Track, fonts_directory, Setting

DOMAIN = "https://api.deezer.com/"
album_search_domain = DOMAIN + "search/album"
track_search_domain = DOMAIN + "search/track"
album_domain = DOMAIN + "album/"
track_domain = DOMAIN + "track/"

results_directory = "results/"

google_photo_api.result_directory = results_directory

absolute_directory = "C:/Users/ferdinandleprince/PycharmProjects/pythonProject/"
download_directory = absolute_directory + "downloaded_covers/"


def getSettings():
    settings_file = open("settings.json", "r")
    settings_json = json.load(settings_file)
    settings_file.close()
    return jsonToSettings(settings_json)


def jsonToSettings(settings_json):
    settings = []
    for setting_json in settings_json:
        settings.append(Setting(
            setting_json["background_blur_radius"],
            setting_json["poster_width_percentage"],
            setting_json["center_image_padding_sides_percentage"],
            setting_json["center_image_padding_top_percentage"],
            setting_json["background_darkness"],
            setting_json["default_album_name_font_size_percentage"],
            setting_json["default_artist_name_font_size_percentage"],
            setting_json["default_album_infos_font_size_percentage"],
            setting_json["resolution_multiplicator"],
            setting_json["center_image_shadow_blur"],
            setting_json["center_image_shadow_size_percentage"],
            (
                setting_json["center_image_shadow_color"][0],
                setting_json["center_image_shadow_color"][1],
                setting_json["center_image_shadow_color"][2]
            ),
            setting_json["background_saturation"],
            setting_json["name"]
        ))
    return settings


def newSetting(new_setting):
    settings = getSettings()
    if new_setting not in settings:
        settings.append(new_setting)
    settings_json = "["
    for setting in settings:
        settings_json += json.dumps(setting.__dict__) + ", "
    settings_json.removesuffix(", ")
    settings_json += "]"
    settings_file = open("settings.json", "w")
    settings_file.write(settings_json)


def customSetting(settings, settings_list):
    print()
    for i in range(len(settings_list)):
        print(str(i + 1) + ". " + settings_list[i].name)
    try:
        profile = int(input("Entrez le numéro du profil souhaité (aucun pour en créer un nouveau) > "))
    except ValueError:
        profile = None
    if profile is not None and profile in range(1, len(settings_list) + 1):
        setting = settings_list[profile - 1]
    else:
        profile = None
    if profile is None:
        print("\nMode de génération Personnalisé !\nEntrez les informations suivantes :")
        try:
            setting = Setting(
                float(input(
                    "flou d'arrière plan (" + str(settings['default'].background_blur_radius) + " par défaut) > ")),
                float(input("rapport largeur/longueur en pourcentage (" + str(
                    settings['default'].poster_width_percentage) + " par défaut pour du A3) > ")),
                float(input("pourcentage de la largeur consacré aux marges autour de la cover (" + str(
                    settings['default'].center_image_padding_sides_percentage) + " par défaut) > ")),
                float(input("pourcentage de la largeur consacré à la marge au dessus de la cover (" + str(
                    settings['default'].center_image_padding_top_percentage) + " par défaut) > ")),
                float(input(
                    "assombrissement de l'arrière de 0 la couleur de base, à 1 l'arrière' toute noir (" + str(
                        settings['default'].background_darkness) + " par "
                                                                   "défaut) > ")),
                float(input(
                    "pourcentage de la hauteur, de la police du titre de l'album si il n'est pas trop grand (" + str(
                        settings['default'].default_album_name_font_size_percentage) + " "
                                                                                       "par défaut) > ")),
                float(input(
                    "pourcentage de la hauteur, de la police du (des) nom(s) de(s) (l')artiste(s) si il n'est pas "
                    "trop grand (" + str(
                        settings['default'].default_artist_name_font_size_percentage) + " par défaut) > ")),
                float(input(
                    "pourcentage de la hauteur, de la police des infos de l'album si elles ne sont pas trop "
                    "grandes (" + str(
                        settings['default'].default_album_infos_font_size_percentage) + " par défaut) > ")),
                float(input(
                    "multiplicateur de la résolution de l'image (1 donne une image de 1 000px de hauteurs, "
                    "10 donne une image de 10 000px de hauteur), baisser pour augmenter la rapidité (" + str(
                        settings['default'].resolution_multiplicator) + " par "
                                                                        "défaut) > ")),
                float(input("flou de l'ombre de la cover (6 par défaut) > ")),
                float(input("pourcentage de la largeur, de l'ombre de la cover (1 par défaut) > ")),
                (
                    print(input(
                        "valeur de 0 à 255 de la quantité de rouge dans la couleur de l'ombre (10 par défaut) > ")),
                    print(input("valeur de 0 à 255 de la quantité de vert dans la couleur de l'ombre (10 par "
                                "défaut) > ")),
                    print(input("valeur de 0 à 255 de la quantité de bleu dans la couleur de l'ombre (10 par "
                                "défaut) > ")),
                ),
                float(input("multiplicateur de la saturation de l'arrière plan (" + str(
                    settings['default'].background_saturation) + " par défaut) > ")),
                input("nom du nouveau profile (laisser vide pour ne pas sauvegarder) > ")
            )
            if setting.name != "":
                newSetting(setting)
        except ValueError:
            print("\n\n        Mauvaise valeur entrée, utilisation du profile par défault. \n")
            setting = settings["default"]

    return setting


def getAlbum(album_to_search):
    PARAMS = {"q": album_to_search}

    response_raw = requests.get(url=album_search_domain, params=PARAMS)
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

    tracks_count_raw = math.ceil(response["nb_tracks"])
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
            formatted_title = formatted_title + " (ft."
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


def getTrack(track_to_search):
    PARAMS = {"q": track_to_search}

    response_raw = requests.get(url=track_search_domain, params=PARAMS)
    response = response_raw.json()
    result_id = str(response["data"][0]["id"])

    response_raw = requests.get(url=track_domain + result_id)
    response = response_raw.json()

    title = response["title"]
    formatted_title = str(title.rsplit(" (feat")[0])
    formatted_title = str(formatted_title.rsplit(" (Extrait")[0])
    if len(response["contributors"]) > 1:
        formatted_title = formatted_title + " (feat."
        contributors = []
        for i in range(1, len(response["contributors"])):
            if response["contributors"][i]["name"] != response["artist"]["name"] and \
                    response["contributors"][i]["name"] not in contributors:
                contributors.append(response["contributors"][i]["name"])
        for contributor in contributors:
            formatted_title = formatted_title + " " + contributor + ","
        formatted_title = formatted_title.removesuffix(",")
        formatted_title = formatted_title + ")"
    title = formatted_title

    duration_raw = response["duration"]
    minutes = math.floor(duration_raw / 60)
    seconds = duration_raw - minutes * 60
    if seconds >= 10:
        seconds_formated = str(seconds)
    else:
        seconds_formated = "0" + str(seconds)
    duration = str(minutes) + ":" + seconds_formated
    explicit_lyrics = response["explicit_lyrics"]
    artist_name = response["artist"]["name"]

    album_id = response["album"]["id"]
    album_response = requests.get(album_domain + str(album_id)).json()
    if album_response["nb_tracks"] > 1:
        album_name = album_response["title"]
    else:
        album_name = None

    if response["album"]["cover_xl"] is not None:
        file_name = album_response["title"] + " - " + artist_name + ".jpg"
        image_response = requests.get(response["album"]["cover_xl"], stream=True)
        with open(download_directory + file_name, "wb") as f:
            shutil.copyfileobj(image_response.raw, f)
    else:
        file_name = input(
            "\n Aucune cover n'est renseignée pour l'instant, téléchargez-en une dans le répertoire " + download_directory + " puis entrez le nom du fichier. \n > ")
    cover_link = download_directory + file_name

    return Track(
        title,
        duration_raw,
        duration,
        explicit_lyrics,
        artist_name,
        album_name,
        file_name,
        cover_link
    )


def lyrics_picker(title: str, artist_name: str = ""):
    lyrics = genius_api.get_lyrics(title, artist_name)
    for i in range(len(lyrics)):
        if "(" in lyrics[i]:
            lyrics[i] = lyrics[i].rsplit("(")[0]
        try:
            if lyrics[i][0] == "[" and lyrics[i][1] != "?":
                if lyrics[i].removeprefix("[").rsplit(" ")[0] == "Partie":
                    print("\n--- " + lyrics[i].removeprefix("[").removesuffix("]") + " ---\n")
                else:
                    print("\n- " + lyrics[i].removeprefix("[").removesuffix("]") + " -\n")
            else:
                print(str(i) + ". " + lyrics[i])
        except IndexError:
            print(str(i) + ". " + lyrics[i])
    lines = input("\nEntrez les lignes de paroles que vous voulez insérer séparés de ':' > ")
    lines = lines.rsplit(":")
    result = ""
    try:
        try:
            for i in range(int(lines[0]), int(lines[1]) + 1):
                result += lyrics[i] + "\n"
            result.removesuffix("\n")
            return result
        except IndexError:
            return lyrics[int(lines[0])]
    except ValueError:
        return ""


def format_too_long(text, draw: ImageDraw.ImageDraw, font: ImageFont.FreeTypeFont,
                    max_width, max_heigth=None, wrap=False):
    formatted_title = text
    while formatted_title[-1] == " ":
        formatted_title = formatted_title.removesuffix(" ")
    if wrap:
        while draw.multiline_textbbox((0, 0), formatted_title, font)[2] > max_width:
            segment = formatted_title
            if "\n" in formatted_title:
                segment = formatted_title.rsplit("\n")[-1]
            segment = segment.removeprefix("\n")
            floor = len(segment) - 1
            segment_result = segment
            while draw.multiline_textbbox((0, 0), segment_result.rsplit("\n")[0], font)[2] > max_width:
                space_pos = 0
                for i in range(floor, 0, -1):
                    if segment[i] == " ":
                        space_pos = i
                        break
                segment_result = ""
                for i in range(len(segment)):
                    if i == space_pos:
                        segment_result += "\n"
                    else:
                        segment_result += segment[i]
                floor -= 1
                if floor < 1:
                    break
            formatted_title = formatted_title.removesuffix("\n").removesuffix(segment) + "\n" + segment_result
        while '\n\n' in formatted_title:
            formatted_title = formatted_title.replace("\n\n", "\n")
        return formatted_title
    else:
        font = font
        while draw.multiline_textbbox((0, 0), formatted_title, font)[2] > max_width:
            font = ImageFont.truetype(font.path, font.size - 1)
        return font


def background_color(background: Image.Image, xy, threshold=128):
    cropped = background.copy().crop(xy)
    pixel = cropped.resize((1, 1)).getpixel((0, 0))
    absolute = (pixel[0] + pixel[1] + pixel[2]) / 3
    color = (absolute < threshold) * 255
    return color, color, color


def blurred_backround(cover, blur_radius=25, width_ratio=70.147, darkness=0,
                      resolution_multiplicator=1, saturation=1, luminosity=0):
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
    black_background_profile = Image.new("L", poster.size, 0).convert("RGB")
    poster = Image.blend(poster, black_background_profile, darkness)
    white_background_profile = Image.new("L", poster.size, 255).convert("RGB")
    poster = Image.blend(poster, white_background_profile, luminosity)

    return poster


def gradiant_background(cover, blend, width_ratio, darkness=0,
                        resolution_multiplicator=1, saturation=1.75):
    resolution = math.ceil(100 / blend)
    pattern = cover.resize((resolution, resolution))
    pixels = []
    for x in range(resolution):
        for y in range(resolution):
            pixels.append(pattern.getpixel((x, y)))
    pixel1 = pixels[randrange(0, resolution * resolution)]
    pixel2 = pixel1
    while pixel2 == pixel1:
        pixel2 = pixels[randrange(0, resolution * resolution)]
    height = math.ceil(cover.height * resolution_multiplicator)
    width = math.ceil(height * width_ratio / 100)
    return gradiant(pixel1, pixel2, width, height)


def gradiant(color1, color2, width, height):
    im = Image.new("RGB", (width, height), (0, 0, 0))
    for x in range(width):
        vertical = x / width
        for y in range(height):
            horizontal = y / height
            top_right = ((1 - horizontal) + vertical) / 2
            bottom_left = (horizontal + (1 - vertical)) / 2
            red = math.ceil((color1[0] * top_right) + (color2[0] * bottom_left))
            green = math.ceil((color1[1] * top_right) + (color2[1] * bottom_left))
            blue = math.ceil((color1[2] * top_right) + (color2[2] * bottom_left))
            im.putpixel((x, y), (red, green, blue))
    return im


def classement(poster, grade, resolution_multiplicator, font_family):
    draw = ImageDraw.Draw(poster)
    if grade == 1:
        color = (204, 136, 0)
    elif grade == 2:
        color = (97, 97, 97)
    elif grade == 3:
        color = (107, 51, 2)
    else:
        color = (0, 0, 0)
    draw.ellipse((30 * resolution_multiplicator, 30 * resolution_multiplicator) + (
        110 * resolution_multiplicator, 110 * resolution_multiplicator), fill=color, outline=(255, 255, 255),
                 width=2 * resolution_multiplicator)
    font = ImageFont.truetype(font_family.black, 45 * resolution_multiplicator)
    text_size = draw.textlength(text=str(grade), font=font) / 2
    draw.text((70 * resolution_multiplicator - text_size, 46 * resolution_multiplicator), str(grade), font=font)

    return poster


def rounded_corner_rectangle(image1: Image, image2: Image, xy, radius, opacity=1):
    xy = (math.ceil(xy[0]), math.ceil(xy[1]))
    mask = Image.new("L", image1.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.rounded_rectangle(xy + (xy[0] + image2.width, xy[1] + image2.height), radius, math.ceil(255 * opacity))
    to_paste = image1.copy()
    to_paste.paste(image2, xy)
    return Image.composite(to_paste, image1, mask)


def square_shadow(background: Image, xy, resolution_multiplicator=1, blur=10, color=(0, 0, 0)):
    center_image_shadow_background = Image.new("RGB", background.size, color)
    center_image_shadow_mask = Image.new("L", background.size, 0)
    center_image_shadow_mask_cutout = ImageDraw.Draw(center_image_shadow_mask)
    center_image_shadow_mask_cutout.rectangle(xy, fill=255)
    center_image_shadow_mask = center_image_shadow_mask.filter(
        ImageFilter.GaussianBlur(blur * resolution_multiplicator))
    return Image.composite(center_image_shadow_background, background, center_image_shadow_mask)


def flip_image(image: Image):
    pixels = []
    for x in range(image.width):
        for y in range(image.height):
            pixels.append(image.getpixel((x, y)))
    result = Image.new("RGB", image.size, (0, 0, 0))
    i = 0
    for x in range(image.width):
        for y in range(image.height):
            i += 1
            result.putpixel((x, y), pixels[len(pixels) - i])
    return result


def rounded_corner_triangle(image1: Image, image2: Image, xy, radius, opacity=1):
    xy = (math.ceil(xy[0]), math.ceil(xy[1]))
    mask = Image.new("L", image1.size, 0)
    draw = ImageDraw.Draw(mask)

    draw.line((xy[0] + radius, xy[1] + image2.height / 2 - radius) + (xy[0] + image2.width - radius * 2, xy[1] + radius), 255 * opacity)
    draw.line((xy[0] + radius, xy[1] + image2.height / 2 + radius) + (xy[0] + image2.width - radius * 2, xy[1] + image2.height - radius), 255 * opacity)
    draw.line((xy[0] + image2.width, xy[1] + radius) + (xy[0] + image2.width, xy[1] + image2.height - radius), 255 * opacity)
    draw.arc((xy[0], xy[1] + image2.height / 2 - radius) + (xy[0] + radius, xy[1] + image2.height / 2 + radius), 90,
             -90, 255 * opacity)
    draw.arc((xy[0] + image2.width - radius * 2, xy[1]) + (xy[0] + image2.width, xy[1] + radius), 150,
             30, 255 * opacity)
    return mask

    to_paste = image1.copy()
    to_paste.paste(image2, xy)
    return Image.composite(to_paste, image1, mask)


def map_range(x, min_source, max_source, min_destination, max_destination):
    # Vérification pour éviter une division par zéro
    if min_source == max_source:
        raise ValueError("min_source et max_source ne peuvent pas être égaux.")

    # Calcul de la valeur transformée
    y = ((x - min_source) / (max_source - min_source)) * (max_destination - min_destination) + min_destination
    return y


def round_corner_profile(radius, angle, rotation):
    angle = math.radians(angle)
    rotation = math.radians(rotation)
    center_to_corner = radius / math.cos(angle)
    width = abs(math.sin(angle))


def invert_image(source: Image):
    image = source.copy()
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.getpixel((x, y))
            r = 255 - pixel[0]
            g = 255 - pixel[1]
            b = 255 - pixel[2]
            image.putpixel((x, y), (r, g, b))
    return image


def luminosity_mask(source: PIL.Image, resolution_multiplicator=1):
    image = source.copy().resize((3, 4)).convert("L")
    image = invert_image(image.convert("RGB")).convert("L")
    if image.getpixel((1, 2)) > 130:
        return Image.new("RGB", source.size, (255, 255, 255))
    else:
        return Image.new("RGB", source.size, (0, 0, 0))
