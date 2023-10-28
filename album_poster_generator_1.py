import math

from PIL import Image, ImageFilter, ImageDraw, ImageFont, ImageEnhance

import core


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


defaultSetting = Setting(
    25,
    70.143,
    13,
    11,
    0.4,
    3.1,
    2.1,
    1.4,
    2,
    10,
    1,
    (0, 0, 0),
    1.75
)


def Generator():
    while True:
        mode = ""
        while mode != "auto" and mode != "custom" and mode != "stop":
            print("Entrez le mode de génération ('auto' : automatique | 'custom' : personnalisé | 'stop' pour arrêter)")
            mode = input("[auto/custom/stop] > ")
        if mode == "auto":
            setting = defaultSetting
        elif mode == "custom":
            print("\n Mode de génération Personnalisé ! \n Entrez les informations suivantes :")
            setting = Setting(
                float(input("flou d'arrière plan (25 par défaut) > ")),
                float(input("rapport largeur/longueur en pourcentage (70.7143 par défaut pour du A3) > ")),
                float(input("pourcentage de la largeur consacré aux marges autour de la cover (13 par défaut) > ")),
                float(input("pourcentage de la largeur consacré à la marge au dessus de la cover (11 par défaut) > ")),
                float(input("assombrissement de l'arrière de 0 la couleur de base, à 1 l'arrière' toute noir (0.4 par défaut) > ")),
                float(input("pourcentage de la hauteur, de la police du titre de l'album si il n'est pas trop grand (3.1 par défaut) > ")),
                float(input("pourcentage de la hauteur, de la police du (des) nom(s) de(s) (l')artiste(s) si il n'est pas trop grand (2.1 par défaut) > ")),
                float(input("pourcentage de la hauteur, de la police des infos de l'album si elles ne sont pas trop grandes (1.15 par défaut) > ")),
                float(input("multiplicateur de la résolution de l'image (1 donne une image de 1 000px de hauteurs, 10 donne une image de 10 000px de hauteur), baisser pour augmenter la rapidité (20 par défaut) > ")),
                float(input("flou de l'ombre de la cover (6 par défaut) > ")),
                float(input("pourcentage de la largeur, de l'ombre de la cover (1 par défaut) > ")),
                (
                    int(input("valeur de 0 à 255 de la quantité de rouge dans la couleur de l'ombre (10 par défaut) >")),
                    int(input("valeur de 0 à 255 de la quantité de vert dans la couleur de l'ombre (10 par défaut) >")),
                    int(input("valeur de 0 à 255 de la quantité de bleu dans la couleur de l'ombre (10 par défaut) >")),
                ),
                float(input("multiplicateur de la saturation de l'arrière plan (1.5 par défaut) >"))
            )
        else:
            break

        print("\nEntrez le nom d'un album :")
        album_to_search = input("> ")

        album = core.getAlbum(album_to_search)

        tracks = ""
        tracks_second = ""
        longest_track = 0
        longest_second_track = 0
        if album.tracks_count_raw <= 16:
            max_per_column = 8
            default_text_font_size_percentage = 1.1 + 4 / min(album.tracks_count_raw, 8)
        else:
            max_per_column = 11
            default_text_font_size_percentage = 1.2

        cover = Image.open(album.cover_link).convert("RGB")

        poster = core.blurred_backround(cover, setting.background_blur_radius, setting.poster_width_percentage,
                                        setting.background_darkness, setting.resolution_multiplicator, setting.background_saturation)
        (poster_width, poster_height) = poster.size

        text_font_size = default_text_font_size_percentage * poster_height / 100
        ImageDraw.ImageDraw.font = ImageFont.truetype(
            "fonts/Poppins-Italic.ttf",
            size=math.ceil(text_font_size))

        for i in range(0, min(album.tracks_count_raw, max_per_column)):
            track_title = album.tracks[i]["title"]
            formated_track = str(i + 1) + ". " + track_title + "\n"
            tracks += formated_track
            if ImageDraw.ImageDraw.font.getlength(formated_track) > longest_track:
                longest_track = ImageDraw.ImageDraw.font.getlength(formated_track)

        for i in range(max_per_column, album.tracks_count_raw):
            track_title = album.tracks[i]["title"]
            formated_track_second = str(i + 1) + ". " + track_title + "\n"
            tracks_second += formated_track_second
            if ImageDraw.ImageDraw.font.getlength(formated_track_second) > longest_second_track:
                longest_second_track = ImageDraw.ImageDraw.font.getlength(formated_track_second)

        album_infos_font_size = setting.default_album_infos_font_size_percentage * poster_height / 100
        album_infos_font = ImageFont.truetype(
            "fonts/Poppins-Light.ttf",
            size=math.ceil(album_infos_font_size))

        if len(album.album_name) > 10:
            album_name_font_size = setting.default_album_name_font_size_percentage * poster_height / 100 - (
                    len(album.album_name) - 10) * 0.7
        else:
            album_name_font_size = setting.default_album_name_font_size_percentage * poster_height / 100
        album_name_font = ImageFont.truetype(
            "fonts/Poppins-ExtraBold.ttf",
            size=math.ceil(album_name_font_size))

        if len(album.artist_name) > 15:
            artist_name_font_size = setting.default_artist_name_font_size_percentage * poster_height / 100 - (
                    len(album.artist_name) - 10) * 0.25
        else:
            artist_name_font_size = setting.default_artist_name_font_size_percentage * poster_height / 100 - (
                    len(album.album_name) - 10) * 0.15
        artist_name_font = ImageFont.truetype(
            "fonts/Poppins-Regular.ttf",
            size=math.ceil(artist_name_font_size))

        center_image_padding_sides = math.ceil(poster_width * setting.center_image_padding_sides_percentage / 100)
        center_image_padding_top = math.ceil(poster_width * setting.center_image_padding_top_percentage / 100)
        center_image_size = math.ceil(poster_width - (center_image_padding_sides * 2))

        center_image = cover.resize((center_image_size, center_image_size))

        center_image_shadow_background = Image.new("RGB", poster.size, setting.center_image_shadow_color)
        center_image_shadow_mask = Image.new("L", poster.size, 0)
        center_image_shadow_mask_cutout = ImageDraw.Draw(center_image_shadow_mask)
        center_image_shadow_size = (setting.center_image_shadow_size_percentage - 1) * poster_width / 100
        center_image_shadow_mask_cutout_size = (
            center_image_padding_sides - center_image_shadow_size, center_image_padding_top - center_image_shadow_size,
            center_image_padding_sides + center_image_size + center_image_shadow_size,
            center_image_padding_top + center_image_size + center_image_shadow_size)
        center_image_shadow_mask_cutout.rectangle(center_image_shadow_mask_cutout_size, fill=255)
        center_image_shadow_mask = center_image_shadow_mask.filter(
            ImageFilter.GaussianBlur(setting.center_image_shadow_blur * setting.resolution_multiplicator))
        poster = Image.composite(center_image_shadow_background, poster, center_image_shadow_mask)

        poster.paste(center_image, (center_image_padding_sides, center_image_padding_top))

        draw = ImageDraw.Draw(poster)
        top_offset = center_image_padding_top + center_image_size + poster_height * 0.015
        draw.text((center_image_padding_sides, top_offset), album.album_name.upper(), font=album_name_font)

        top_offset += album_name_font_size + poster_height * 0.015
        draw.text((center_image_padding_sides, top_offset), album.artist_name.upper(), font=artist_name_font)

        top_offset += artist_name_font_size + poster_height * 0.02
        draw.line((center_image_padding_sides, top_offset) + (
            center_image_size + center_image_padding_sides, math.ceil(top_offset)),
                  width=math.ceil(0.0025 * poster_height))

        line_spacing = text_font_size / 2.5
        top_offset += poster_height * 0.02
        draw.multiline_text((center_image_padding_sides, top_offset), tracks, spacing=line_spacing)
        tracks_second_offset = ((poster_width - center_image_padding_sides - longest_second_track) + (
                center_image_padding_sides + longest_track)) / 2
        draw.multiline_text((tracks_second_offset, top_offset),
                            tracks_second, spacing=line_spacing)

        line_spacing = album_infos_font_size / 2.5
        album_infos = album.tracks_count + "\n" + album.release_date + "\n" + album.duration
        top_offset = center_image_padding_top + center_image_size + poster_height * 0.05
        draw.multiline_text((poster_width - center_image_padding_sides, top_offset), album_infos, align="right",
                            anchor="rm", font=album_infos_font)

        target_file_name = "results/" + "Poster " + album.album_name + " - " + album.artist_name + ".png"
        poster.save(target_file_name)
        poster.show()

        print("\nPoster réalisé avec enregistré sous " + target_file_name + " !\n\n\n")


print("Bienvenue dans le générateur de poster de cover d'album !\n")

Generator()
