import math
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import core


def Generator():
    while True:
        settings_list = core.getSettings()
        dict_scaffold = []
        for setting_item in settings_list:
            dict_scaffold.append([setting_item.name, setting_item])
        settings = dict(dict_scaffold)

        font = core.Fonts("Roboto")

        mode = ""
        while mode != "auto" and mode != "custom" and mode != "stop":
            print("Entrez le mode de génération ('auto' : automatique | 'custom' : personnalisé | 'stop' pour arrêter)")
            mode = input("[auto/custom/stop] > ")
        if mode == "auto":
            setting = settings["default"]
        elif mode == "custom":
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
                    setting = core.Setting(
                        float(input("flou d'arrière plan (" + str(settings['default'].background_blur_radius) + " par défaut) > ")),
                        float(input("rapport largeur/longueur en pourcentage (" + str(settings['default'].poster_width_percentage) + " par défaut pour du A3) > ")),
                        float(input("pourcentage de la largeur consacré aux marges autour de la cover (" + str(settings['default'].center_image_padding_sides_percentage) + " par défaut) > ")),
                        float(input("pourcentage de la largeur consacré à la marge au dessus de la cover (" + str(settings['default'].center_image_padding_top_percentage) + " par défaut) > ")),
                        float(input(
                            "assombrissement de l'arrière de 0 la couleur de base, à 1 l'arrière' toute noir (" + str(settings['default'].background_darkness) + " par "
                            "défaut) > ")),
                        float(input(
                            "pourcentage de la hauteur, de la police du titre de l'album si il n'est pas trop grand (" + str(settings['default'].default_album_name_font_size_percentage) + " "
                            "par défaut) > ")),
                        float(input(
                            "pourcentage de la hauteur, de la police du (des) nom(s) de(s) (l')artiste(s) si il n'est pas "
                            "trop grand (" + str(settings['default'].default_artist_name_font_size_percentage) + " par défaut) > ")),
                        float(input(
                            "pourcentage de la hauteur, de la police des infos de l'album si elles ne sont pas trop "
                            "grandes (" + str(settings['default'].default_album_infos_font_size_percentage) + " par défaut) > ")),
                        float(input(
                            "multiplicateur de la résolution de l'image (1 donne une image de 1 000px de hauteurs, "
                            "10 donne une image de 10 000px de hauteur), baisser pour augmenter la rapidité (" + str(settings['default'].resolution_multiplicator) + " par "
                            "défaut) > ")),
                        float(input("flou de l'ombre de la cover (6 par défaut) > ")),
                        float(input("pourcentage de la largeur, de l'ombre de la cover (1 par défaut) > ")),
                        (
                            int(input(
                                "valeur de 0 à 255 de la quantité de rouge dans la couleur de l'ombre (10 par défaut) > ")),
                            int(input("valeur de 0 à 255 de la quantité de vert dans la couleur de l'ombre (10 par "
                                      "défaut) > ")),
                            int(input("valeur de 0 à 255 de la quantité de bleu dans la couleur de l'ombre (10 par "
                                      "défaut) > ")),
                        ),
                        float(input("multiplicateur de la saturation de l'arrière plan (" + str(settings['default'].background_saturation) + " par défaut) > ")),
                        input("nom du nouveau profile (laisser vide pour ne pas sauvegarder) > ")
                    )
                    if setting.name != "":
                        core.newSetting(setting)
                except ValueError:
                    print("\n\n        Mauvaise valeur entrée, utilisation du profile par défault. \n")
                    setting = settings["default"]
        else:
            break

        print("\nEntrez le nom d'un album :")
        album_to_search = input("> ")

        album = core.getAlbum(album_to_search)

        tracks = ""
        tracks_second = ""
        longest_track = 0
        longest_second_track = 0
        if album.tracks_count_raw <= 10:
            max_per_column = 5
            default_text_font_size_percentage = 1.3 + 4 / min(album.tracks_count_raw, max_per_column)
        elif album.tracks_count_raw <= 16:
            max_per_column = 8
            default_text_font_size_percentage = 1.2 + 4 / min(album.tracks_count_raw, max_per_column)
        else:
            max_per_column = 12
            default_text_font_size_percentage = 1.2

        cover = Image.open(album.cover_link).convert("RGB")

        poster = core.blurred_backround(cover, setting.background_blur_radius, setting.poster_width_percentage,
                                        setting.background_darkness, setting.resolution_multiplicator,
                                        setting.background_saturation)
        (poster_width, poster_height) = poster.size

        text_font_size = default_text_font_size_percentage * poster_height / 100
        ImageDraw.ImageDraw.font = ImageFont.truetype(
            font.light.italic(),
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
            font.medium,
            size=math.ceil(album_infos_font_size))

        if len(album.album_name) > 10:
            album_name_font_size = setting.default_album_name_font_size_percentage * poster_height / 100 - (
                    len(album.album_name) - 10) * 0.7
        else:
            album_name_font_size = setting.default_album_name_font_size_percentage * poster_height / 100
        album_name_font = ImageFont.truetype(
            font.black,
            size=math.ceil(album_name_font_size))

        if len(album.artist_name) > 15:
            artist_name_font_size = setting.default_artist_name_font_size_percentage * poster_height / 100 - (
                    len(album.artist_name) - 10) * 0.25
        else:
            artist_name_font_size = setting.default_artist_name_font_size_percentage * poster_height / 100 - (
                    len(album.album_name) - 10) * 0.15
        artist_name_font = ImageFont.truetype(
            font.regular,
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
