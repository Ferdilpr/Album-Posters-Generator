import math
from PIL import Image, ImageFilter, ImageDraw, ImageFont
import core


def generator():
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
            setting = core.customSetting(settings, settings_list)
        else:
            break

        print("\nEntrez le nom d'un album :")
        album_to_search = input("> ")
        classement = None
        max_per_column = None
        if " **" in album_to_search:
            classement = int(album_to_search.split(" **")[1])
            album_to_search = album_to_search.split(" **")[0]
        if " ^^" in album_to_search:
            max_per_column = int(album_to_search.split(" ^^")[1])
            album_to_search = album_to_search.split(" ^^")[0]

        album = core.search_album(album_to_search, download_cover=True)
        for track in album.tracks:
            track.format_title()

        tracks = ""
        tracks_second = ""
        longest_track = 0
        longest_second_track = 0
        if max_per_column is None:
            max_per_column = 10
        default_text_font_size_percentage = 1.8

        cover = Image.open(album.cover_link).convert("RGB")

        poster = core.blurred_backround(cover, setting.background_blur_radius, setting.poster_width_percentage,
                                        setting.background_darkness, setting.resolution_multiplicator,
                                        setting.background_saturation)
        # poster = core.gradiant_background(cover, 80, setting.poster_width_percentage,
        # resolution_multiplicator=setting.resolution_multiplicator)

        (poster_width, poster_height) = poster.size

        center_image_padding_sides = math.ceil(poster_width * setting.center_image_padding_sides_percentage / 100)
        center_image_padding_top = math.ceil(poster_width * setting.center_image_padding_top_percentage / 100)
        center_image_size = math.ceil(poster_width - (center_image_padding_sides * 2))

        album_name_font = ImageFont.truetype(
            font.black,
            size=35 * setting.resolution_multiplicator
        )
        while album_name_font.getlength(album.title.upper()) > center_image_size * 0.65:
            album_name_font = ImageFont.truetype(
                font.black,
                size=album_name_font.size - setting.resolution_multiplicator
            )

        artist_name_font = ImageFont.truetype(
            font.regular,
            size=album_name_font.size
        )
        while artist_name_font.getlength(album.artists_formatted.upper()) > center_image_size * 0.65:
            artist_name_font = ImageFont.truetype(
                font.regular,
                size=artist_name_font.size - setting.resolution_multiplicator
            )

        album_infos_font = ImageFont.truetype(
            font.regular,
            size=int(album_name_font.size * 0.6)
        )

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
        draw.text((center_image_padding_sides, top_offset), album.title.upper(), font=album_name_font)

        top_offset += album_name_font.size * 1.35
        draw.text((center_image_padding_sides, top_offset), album.artists_formatted.upper(), font=artist_name_font)

        top_offset += artist_name_font.size * 1.35
        draw.line((center_image_padding_sides, top_offset) + (
            center_image_size + center_image_padding_sides, math.ceil(top_offset)),
                  width=math.ceil(0.0025 * poster_height))

        top_offset += poster_height * 0.02

        first_column, second_column = [], []
        tracks_space = (center_image_size, poster_height - top_offset - center_image_padding_top)
        tracks_font = ImageFont.truetype(
            font.light.italic(),
            size=21 * setting.resolution_multiplicator
        )
        line_spacing_multiplicator = 0.35
        end = False
        while True:
            for i in range(album.tracks_count_raw, math.ceil(album.tracks_count_raw / 2) - 1, -1):
                first_column_tracks = album.tracks[0:i]
                second_column_tracks = album.tracks[i:album.tracks_count_raw]
                first_column = list(
                    (str(x + 1) + ". " + first_column_tracks[x].title)
                    for x in range(len(first_column_tracks))
                )
                second_column = list(
                    (str(x + i + 1) + ". " + second_column_tracks[x].title)
                    for x in range(len(second_column_tracks))
                )
                first_column_size = draw.multiline_textbbox(
                    (0, 0),
                    "\n".join(first_column[0:len(second_column) + 1]),
                    font=tracks_font,
                    spacing=tracks_font.size * line_spacing_multiplicator
                )[2:4]
                whole_first_column_size = draw.multiline_textbbox(
                    (0, 0),
                    "\n".join(first_column),
                    font=tracks_font,
                    spacing=tracks_font.size * line_spacing_multiplicator
                )[2:4]
                second_column_size = draw.multiline_textbbox(
                    (0, 0),
                    "\n".join(second_column),
                    font=tracks_font,
                    spacing=tracks_font.size * line_spacing_multiplicator
                )[2:4]
                if (first_column_size[0] + second_column_size[0] + poster_width * 0.1 < tracks_space[0]
                        and whole_first_column_size[0] + poster_width * 0.05 < tracks_space[0]
                        and whole_first_column_size[1] < tracks_space[1]):
                    end = True
                    break
            if end:
                break

            tracks_font = ImageFont.truetype(
                font.light.italic(),
                size=int(tracks_font.size - setting.resolution_multiplicator / 5)
            )

        draw.multiline_text(
            (center_image_padding_sides, top_offset),
            "\n".join(first_column),
            font=tracks_font,
            spacing=tracks_font.size * line_spacing_multiplicator
        )
        second_column_size = draw.multiline_textbbox(
            (0, 0),
            "\n".join(second_column),
            font=tracks_font,
            spacing=tracks_font.size * line_spacing_multiplicator
        )[2:4]
        if first_column_size[0] < whole_first_column_size[0]:
            vertical = poster_width - center_image_padding_sides - second_column_size[0]
        else:
            vertical = (
                            poster_width - center_image_padding_sides - second_column_size[0] +
                            center_image_padding_sides + first_column_size[0]
                       ) / 2
        draw.multiline_text(
            (vertical, top_offset),
            "\n".join(second_column),
            font=tracks_font,
            spacing=tracks_font.size * line_spacing_multiplicator
        )

        album_infos = album.tracks_count + "\n" + album.release_date + "\n" + album.duration.replace(":", " min ")
        album_infos_size = draw.multiline_textbbox(
            (0, 0),
            album_infos,
            align="right",
            font=album_infos_font,
            spacing=album_infos_font.size * 0.25
        )
        top_offset = (
                center_image_padding_top + center_image_size +
                center_image_padding_top + center_image_size + poster_height * 0.015 + album_name_font.size * 1.35 + artist_name_font.size * 1.35 - album_infos_size[3]
        ) / 2
        draw.multiline_text(
            (poster_width - center_image_padding_sides, top_offset),
            album_infos,
            align="right",
            anchor="ra",
            font=album_infos_font,
            spacing=album_infos_font.size * 0.25
        )

        if classement is not None:
            poster = core.classement(poster, classement, setting.resolution_multiplicator, font)

        if setting.name == "default":
            target_file_name = "results/" + "Poster " + album.title + " - " + album.artist.name + ".png"
        else:
            target_file_name = "results/" + "Poster " + album.title + " - " + album.artist.name + " (" + setting.name + ")" + ".png"
        if classement is not None:
            target_file_name = target_file_name.removesuffix(".png") + " [" + str(classement) + "].png"
        poster.save(target_file_name)

        core.google_photo_api.cloud_upload(target_file_name.removeprefix("results/"))
        poster.show()

        print("\nPoster réalisé avec succès et enregistré sous " + target_file_name + " !\n\n\n")


print("Bienvenue dans le générateur de poster de cover d'album !\n")

# generator()
