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
            setting = core.customSetting(settings, settings_list)
        else:
            break

        print("\nEntrez le nom d'un album :")
        album_to_search = input("> ")
        classement = None
        if " **" in album_to_search:
            classement = int(album_to_search.split(" **")[1])
            album_to_search = album_to_search.split(" **")[0]

        album = core.getAlbum(album_to_search)

        tracks = ""
        tracks_second = ""
        longest_track = 0
        longest_second_track = 0
        if album.tracks_count_raw <= 10:
            max_per_column = 6
            default_text_font_size_percentage = 1.25 + 4 / min(album.tracks_count_raw, max_per_column)
        elif album.tracks_count_raw <= 16:
            max_per_column = 8
            default_text_font_size_percentage = 1.2 + 4 / min(album.tracks_count_raw, max_per_column)
        elif album.tracks_count_raw <= 24:
            max_per_column = 12
            default_text_font_size_percentage = 1.2
        else:
            max_per_column = 15
            default_text_font_size_percentage = 1

        cover = Image.open(album.cover_link).convert("RGB")

        poster = core.blurred_backround(cover, setting.background_blur_radius, setting.poster_width_percentage,
                                        setting.background_darkness, setting.resolution_multiplicator,
                                        setting.background_saturation)
        # poster = core.gradiant_background(cover, 80, setting.poster_width_percentage,
        # resolution_multiplicator=setting.resolution_multiplicator)

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

        if classement is not None:
            poster = core.classement(poster, classement, setting.resolution_multiplicator, font)

        target_file_name = "results/" + "Poster " + album.album_name + " - " + album.artist_name + ".png"
        poster.save(target_file_name)
        poster.show()

        print("\nPoster réalisé avec enregistré sous " + target_file_name + " !\n\n\n")


print("Bienvenue dans le générateur de poster de cover d'album !\n")

Generator()
