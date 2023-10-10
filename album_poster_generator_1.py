import math

from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance
import requests
import shutil
from datetime import datetime

DOMAIN = "https://api.deezer.com/"
search_domain = DOMAIN + "search/album"
album_domain = DOMAIN + "album/"

absolute_directory = "C:/Users/ferdinandleprince/PycharmProjects/pythonProject/"
download_directory = absolute_directory + "downloaded_covers/"

print("Bienvenue dans le générateur de poster de cover d'album !\n")

while True:
    mode = ""
    while mode != "auto" and mode != "custom" and mode != "stop":
        print("Entrez le mode de génération ('auto' : automatique | 'custom' : personnalisé | 'stop' pour arrêter)")
        mode = input("[auto/custom/stop] > ")
    if mode == "auto":
        background_blur_radius = 25
        poster_width_percentage = 70.7143
        center_image_padding_sides_percentage = 13
        center_image_padding_top_percentage = 11
        background_darkness = 0.4
        default_album_name_font_size_percentage = 3.1
        default_artist_name_font_size_percentage = 2.1
        default_album_infos_font_size_percentage = 1.15
        resolution_multiplicator = 2
        center_image_shadow_blur = 9
        center_image_shadow_size_percentage = 1.2
        center_image_shadow_color = (0, 0, 0)
        background_saturation = 1.75
    elif mode == "custom":
        print("\n Mode de génération Personnalisé ! \n Entrez les informations suivantes :")
        background_blur_radius = float(input("flou d'arrière plan (25 par défaut) > "))
        poster_width_percentage = float(
            input("rapport largeur/longueur en pourcentage (70.7143 par défaut pour du A3) > "))
        center_image_padding_sides_percentage = float(
            input("pourcentage de la largeur consacré aux marges autour de la cover (13 par défaut) > "))
        center_image_padding_top_percentage = float(
            input("pourcentage de la largeur consacré à la marge au dessus de la cover (11 par défaut) > "))
        background_darkness = float(input(
            "assombrissement de l'arrière de 0 la couleur de base, à 1 l'arrière' toute noir (0.4 par défaut) > "))
        default_album_name_font_size_percentage = float(input(
            "pourcentage de la hauteur, de la police du titre de l'album si il n'est pas trop grand (3.1 par défaut) > "))
        default_artist_name_font_size_percentage = float(input(
            "pourcentage de la hauteur, de la police du (des) nom(s) de(s) (l')artiste(s) si il n'est pas trop grand (2.1 par défaut) > "))
        default_album_infos_font_size_percentage = float(input(
            "pourcentage de la hauteur, de la police des infos de l'album si elles ne sont pas trop grandes (1.15 par défaut) > "))
        resolution_multiplicator = float(input(
            "multiplicateur de la résolution de l'image (1 donne une image de 1 000px de hauteurs, 10 donne une image de 10 000px de hauteur), baisser pour augmenter la rapidité (20 par défaut) > "))
        center_image_shadow_blur = float(input("flou de l'ombre de la cover (6 par défaut) > "))
        center_image_shadow_size_percentage = float(
            input("pourcentage de la largeur, de l'ombre de la cover (1 par défaut) > "))
        center_image_shadow_color_red = float(
            input("valeur de 0 à 255 de la quantité de rouge dans la couleur de l'ombre (10 par défaut) >"))
        center_image_shadow_color_green = float(
            input("valeur de 0 à 255 de la quantité de vert dans la couleur de l'ombre (10 par défaut) >"))
        center_image_shadow_color_blue = float(
            input("valeur de 0 à 255 de la quantité de bleu dans la couleur de l'ombre (10 par défaut) >"))
        center_image_shadow_color = (
            center_image_shadow_color_red, center_image_shadow_color_green, center_image_shadow_color_blue)
        background_saturation = float(input("multiplicateur de la saturation de l'arrière plan (1.5 par défaut) >"))
    else:
        break

    print("\nEntrez le nom d'un album :")
    album_to_search = input("> ")
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

    tracks = ""
    tracks_second = ""
    longest_track = 0
    longest_second_track = 0
    if tracks_count_raw <= 16:
        max_per_column = 8
        default_text_font_size_percentage = 1 + 4 / min(tracks_count_raw, 8)
    else:
        max_per_column = 11
        default_text_font_size_percentage = 1.2

    file_name = album_name + " - " + artist_name + ".jpg"
    image_response = requests.get(response["cover_xl"], stream=True)
    with open(download_directory + file_name, "wb") as f:
        shutil.copyfileobj(image_response.raw, f)

    cover_link = download_directory + file_name

    cover = Image.open(cover_link).convert("RGB")

    cover = cover.resize(
        (math.ceil(cover.size[0] * resolution_multiplicator), math.ceil(cover.size[1] * resolution_multiplicator)))

    (cover_width, cover_height) = cover.size
    poster_width = math.ceil(cover_height * poster_width_percentage / 100)
    left = (cover_width - poster_width) / 2
    right = cover_width - left
    (upper, lower) = (0, cover_height)

    text_font_size = default_text_font_size_percentage * cover_height / 100
    ImageDraw.ImageDraw.font = ImageFont.truetype(
        absolute_directory + "fonts/Poppins-Italic.ttf",
        size=math.ceil(text_font_size))

    for i in range(0, min(tracks_count_raw, max_per_column)):
        track_title = response["tracks"]["data"][i]["title"]
        formated_track = str(i + 1) + ". " + track_title + "\n"
        tracks += formated_track
        if ImageDraw.ImageDraw.font.getlength(formated_track) > longest_track:
            longest_track = ImageDraw.ImageDraw.font.getlength(formated_track)

    for i in range(max_per_column, tracks_count_raw):
        track_title = response["tracks"]["data"][i]["title"]
        formated_track_second = str(i + 1) + ". " + track_title + "\n"
        tracks_second += formated_track_second
        if ImageDraw.ImageDraw.font.getlength(formated_track_second) > longest_second_track:
            longest_second_track = ImageDraw.ImageDraw.font.getlength(formated_track_second)

    album_infos_font_size = default_album_infos_font_size_percentage * cover_height / 100
    album_infos_font = ImageFont.truetype(
        absolute_directory + "fonts/Poppins-Light.ttf",
        size=math.ceil(album_infos_font_size))

    if len(album_name) > 10:
        album_name_font_size = default_album_name_font_size_percentage * cover_height / 100 - (
                len(album_name) - 10) * 0.7
    else:
        album_name_font_size = default_album_name_font_size_percentage * cover_height / 100
    album_name_font = ImageFont.truetype(
        absolute_directory + "fonts/Poppins-ExtraBold.ttf",
        size=math.ceil(album_name_font_size))

    if len(artist_name) > 15:
        artist_name_font_size = default_artist_name_font_size_percentage * cover_height / 100 - (
                len(artist_name) - 10) * 0.25
    else:
        artist_name_font_size = default_artist_name_font_size_percentage * cover_height / 100 - (
                len(album_name) - 10) * 0.15
    artist_name_font = ImageFont.truetype(
        absolute_directory + "fonts/Poppins-Regular.ttf",
        size=math.ceil(artist_name_font_size))

    center_image_padding_sides = math.ceil(poster_width * center_image_padding_sides_percentage / 100)
    center_image_padding_top = math.ceil(poster_width * center_image_padding_top_percentage / 100)
    center_image_size = math.ceil(poster_width - (center_image_padding_sides * 2))

    center_image = cover.resize((center_image_size, center_image_size))

    poster = cover.filter(ImageFilter.GaussianBlur(background_blur_radius * resolution_multiplicator))
    poster = poster.crop((math.ceil(left), upper, math.ceil(right), lower))
    poster = ImageEnhance.Color(poster).enhance(background_saturation)
    black_background_profile = Image.new("RGB", poster.size, (0, 0, 0))
    poster = Image.blend(poster, black_background_profile, background_darkness)

    center_image_shadow_background = Image.new("RGB", poster.size, center_image_shadow_color)
    center_image_shadow_mask = black_background_profile.copy().convert("L")
    center_image_shadow_mask_cutout = ImageDraw.Draw(center_image_shadow_mask)
    center_image_shadow_size = (center_image_shadow_size_percentage - 1) * poster_width / 100
    center_image_shadow_mask_cutout_size = (
    center_image_padding_sides - center_image_shadow_size, center_image_padding_top - center_image_shadow_size,
    center_image_padding_sides + center_image_size + center_image_shadow_size,
    center_image_padding_top + center_image_size + center_image_shadow_size)
    center_image_shadow_mask_cutout.rectangle(center_image_shadow_mask_cutout_size, fill=255)
    center_image_shadow_mask = center_image_shadow_mask.filter(
        ImageFilter.GaussianBlur(center_image_shadow_blur * resolution_multiplicator))
    poster = Image.composite(center_image_shadow_background, poster, center_image_shadow_mask)

    poster.paste(center_image, (center_image_padding_sides, center_image_padding_top))

    draw = ImageDraw.Draw(poster)

    top_offset = center_image_padding_top + center_image_size + cover_height * 0.015
    draw.text((center_image_padding_sides, top_offset), album_name.upper(), font=album_name_font)

    top_offset += album_name_font_size + cover_height * 0.015
    draw.text((center_image_padding_sides, top_offset), artist_name.upper(), font=artist_name_font)

    top_offset += artist_name_font_size + cover_height * 0.02
    draw.line((center_image_padding_sides, top_offset) + (center_image_size + center_image_padding_sides, math.ceil(top_offset)),
              width=math.ceil(0.001 * cover_height))

    line_spacing = text_font_size / 2
    top_offset += cover_height * 0.03
    draw.multiline_text((center_image_padding_sides, top_offset), tracks, spacing=line_spacing)
    tracks_second_offset = ((poster_width - center_image_padding_sides - longest_second_track) + (
                center_image_padding_sides + longest_track)) / 2
    draw.multiline_text((tracks_second_offset, top_offset),
                        tracks_second, spacing=line_spacing)

    line_spacing = album_infos_font_size / 2
    album_infos = tracks_count + "\n" + release_date + "\n" + duration
    top_offset = center_image_padding_top + center_image_size + cover_height * 0.05
    draw.multiline_text((poster_width - center_image_padding_sides, top_offset), album_infos, align="right",
                        anchor="rm", font=album_infos_font, spacing=line_spacing)

    target_file_name = "results/" + "Poster " + album_name + " - " + artist_name + ".png"
    poster.save(target_file_name)
    poster.show()

    print("\nPoster réalisé avec enregistré sous " + target_file_name + " !\n\n\n")
