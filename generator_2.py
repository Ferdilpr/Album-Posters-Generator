import math
import random

import core
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageEnhance

# Parameters
resolution_multiplicator = 1
width_ratio = 56.25
overlay_width_percentage = 80
overlay_height_percentage = 67
overlay_outline_width = 2
center_cover_padding_sides_percentage = 10
center_cover_padding_top_percentage = 10
center_cover_outline = True
variant = 2

font = core.Fonts("Roboto")
overlay_outline_width = overlay_outline_width * resolution_multiplicator


def progress_bar(background, duration_raw, progress_percentage, color, xy, time_font, resolution_multiplicator, width):
    duration = format_time(duration_raw)
    avancement_raw = math.ceil(duration_raw * progress_percentage / 100)
    avancement = format_time(avancement_raw)
    draw = ImageDraw.Draw(background)
    avancement_text_size = draw.textlength(avancement, font=time_font)
    duration_text_size = draw.textlength(duration, font=time_font)
    draw.text((xy[0], xy[1]), avancement, fill=color, font=time_font)
    draw.text((xy[2] - duration_text_size, xy[1]), duration, fill=color, font=time_font)
    background = core.rounded_corner_rectangle(
        background,
        Image.new("L", (
            math.ceil(xy[2] - xy[0] - 20 * resolution_multiplicator - avancement_text_size - duration_text_size),
            math.ceil(width + 1)
        ), color),
        (xy[0] + avancement_text_size + 10 * resolution_multiplicator, xy[1] + time_font.size / 2 - width / 2),
        math.ceil(width / 2),
        0.35
    )
    bar_length = (xy[2] - duration_text_size - 10 * resolution_multiplicator) - (
            xy[0] + avancement_text_size + 10 * resolution_multiplicator)
    draw = ImageDraw.Draw(background)
    draw.rounded_rectangle((
        xy[0] + avancement_text_size + 10 * resolution_multiplicator,
        math.ceil(xy[1] + time_font.size / 2 - width / 2),
        xy[0] + avancement_text_size + 10 * resolution_multiplicator + bar_length * progress_percentage / 100,
        math.ceil(xy[1] + time_font.size / 2 + width / 2)
    ), radius=width * 0.5, fill=color)
    return background


def format_time(time):
    if time < 3600:
        minutes = int(time / 60)
        seconds = time - minutes * 60
        formatted = str(minutes) + ":" + format_dec(seconds)
    else:
        hours = int(time / 3600)
        minutes = int((time - hours * 3600) / 60)
        seconds = time - hours * 3600 - minutes * 60
        formatted = str(hours) + ":" + format_dec(minutes) + ":" + format_dec(seconds)
    return formatted


def format_dec(number):
    if number < 10:
        return "0" + str(number)
    else:
        return str(number)


def generator():
    text_color = (255 * (variant == 1), 255 * (variant == 1), 255 * (variant == 1))

    # Getting track
    track_to_get = input("titre > ")
    track = core.getTrack(track_to_get)
    cover = track.cover

    title_font_size = math.ceil(min(30.0, 30 - max(0, len(track.title) - 5) * 0.325) * resolution_multiplicator)
    title_font = ImageFont.truetype(
        font.bold,
        size=title_font_size
    )
    artist_font_size = math.ceil(min(25.0, 25 - max(0, len(track.artist_name) - 8) * 0.45) * resolution_multiplicator)
    artist_font = ImageFont.truetype(
        font.light,
        size=artist_font_size
    )
    time_font = ImageFont.truetype(
        font.light,
        size=17 * resolution_multiplicator
    )
    lyrics_font = ImageFont.truetype(
        font.black,
        size=35 * resolution_multiplicator
    )

    # Creation of background
    background = core.blurred_backround(cover,
                                        blur_radius=(20 * (variant == 0 or variant == 1)) + (0 * (variant == 2)),
                                        darkness=(0.5 * (variant == 0)) + (0.3 * (variant == 2)),
                                        resolution_multiplicator=resolution_multiplicator,
                                        width_ratio=width_ratio,
                                        luminosity=0.05 * (variant == 1))

    # Overlay parameters calculations
    overlay_width = background.width * overlay_width_percentage / 100
    overlay_height = background.height * overlay_height_percentage / 100

    overlay_width_offset = math.ceil((background.width - overlay_width) / 2)
    overlay_height_offset = math.ceil((background.height - overlay_height) / 2)

    # Creating overlay outline
    overlay_outline = core.blurred_backround(cover,
                                             blur_radius=25,
                                             luminosity=(0.5 * (variant == 0)) + (0.2 * (variant == 1)) + (
                                                     0.3 * (variant == 2)),
                                             resolution_multiplicator=resolution_multiplicator,
                                             width_ratio=width_ratio, saturation=1.4)
    overlay_outline = overlay_outline.crop(
        (
            overlay_width_offset - overlay_outline_width,
            overlay_height_offset - overlay_outline_width
        ) +
        (
            background.width - overlay_width_offset + overlay_outline_width,
            background.height - overlay_height_offset + overlay_outline_width
        )
    )

    # Creating overlay
    overlay = core.blurred_backround(cover,
                                     luminosity=0.2 * (variant == 0),
                                     blur_radius=(65 * (variant == 0 or variant == 1)) + (27.5 * (variant == 2)),
                                     resolution_multiplicator=resolution_multiplicator,
                                     width_ratio=width_ratio,
                                     darkness=0.5 * (variant == 1))
    overlay = overlay.crop(
        (overlay_width_offset, overlay_height_offset) +
        (background.width - overlay_width_offset, background.height - overlay_height_offset)
    )

    # Blending overlays
    poster = background
    if center_cover_outline:
        poster = core.rounded_corner_rectangle(
            poster, overlay_outline,
            (overlay_width_offset - overlay_outline_width, overlay_height_offset - overlay_outline_width),
            50 * resolution_multiplicator
        )
    poster = core.rounded_corner_rectangle(poster, overlay, (overlay_width_offset, overlay_height_offset),
                                           50 * resolution_multiplicator)

    if variant == 2:
        alpha_channel = Image.new("L", poster.size,
                                  (poster.crop(
                                      (overlay_width_offset, overlay_height_offset) +
                                      (overlay_width_offset + overlay_width,
                                       overlay_height_offset + overlay_height))
                                   .resize((1, 1)).convert("L").getpixel((0, 0)) < 128) * 255
                                  ).convert("RGB")
    else:
        alpha_channel = Image.new("L", poster.size, 255 * variant)

    # poster = track_content(poster, cover, track, title_font, artist_font, time_font,
    #                       overlay_width, overlay_width_offset, overlay_height_offset,
    #                       alpha_channel)

    poster = lyrics_content(poster, cover, track, resolution_multiplicator, title_font,
                            artist_font, overlay_width, overlay_width_offset, overlay_height_offset,
                            alpha_channel, lyrics_font, overlay_height)

    target_file_name = "results/" + "Poster " + track.title + " - " + track.artist_name + ".png"
    poster.save(target_file_name)
    # core.google_photo_api.cloud_upload(target_file_name.removeprefix("results/"))
    poster.show()


def lyrics_content(frame: Image, cover: Image, track: core.Track, resolution_multiplicator,
                   title_font: ImageFont.FreeTypeFont, artist_font: ImageFont.FreeTypeFont,
                   overlay_width, overlay_width_offset, overlay_height_offset, alpha_channel: Image,
                   lyrics_font: ImageFont.FreeTypeFont, overlay_height):
    lyrics = lyrics_picker(track.title, track.artist_name)

    poster = frame.copy()
    top_cover_padding = 30 * resolution_multiplicator
    top_cover_side = 80 * resolution_multiplicator
    top_cover = cover.copy().resize((top_cover_side, top_cover_side))
    top_cover_radius = 15 * resolution_multiplicator
    poster = core.rounded_corner_rectangle(poster, top_cover, (
        overlay_width_offset + top_cover_padding,
        overlay_height_offset + top_cover_padding
    ), top_cover_radius, 1)

    infos_mask = Image.new("L", poster.size, 0)
    draw = ImageDraw.Draw(infos_mask)
    formatted_title = format_too_long(track.title, draw, title_font,
                                      overlay_width - top_cover_padding * 3 - top_cover_side)

    draw.multiline_text((
        overlay_width_offset + top_cover_padding * 2 + top_cover_side,
        overlay_height_offset + top_cover_padding + top_cover_radius / 3
    ), formatted_title, 255, title_font, spacing=resolution_multiplicator)
    draw.text((
        overlay_width_offset + top_cover_padding * 2 + top_cover_side,
        overlay_height_offset + top_cover_padding + top_cover_side - artist_font.size - top_cover_radius / 3
    ), track.artist_name, 255, artist_font)

    lyrics_padding = 1 * resolution_multiplicator
    formatted_lyrics = ""
    for lyric in lyrics.rsplit("\n\n"):
        formatted_lyrics += format_too_long(lyric, draw, lyrics_font,
                                            overlay_width - lyrics_padding * 2) + "\n"
    formatted_lyrics = formatted_lyrics.removesuffix("\n\n")

    lyrics_size = draw.multiline_textbbox((0, 0), formatted_lyrics, lyrics_font)
    lyrics_height_offset = ((overlay_height_offset + overlay_height - lyrics_size[3] - lyrics_padding) +
                            (overlay_height_offset + top_cover_padding + top_cover_side + lyrics_padding)) / 2
    lyrics_width_offset = ((overlay_width_offset + lyrics_padding) +
                           (overlay_width_offset + overlay_width - lyrics_padding - lyrics_size[2])) / 2
    draw.multiline_text((lyrics_width_offset, lyrics_height_offset), formatted_lyrics,
                        255, lyrics_font, spacing=lyrics_font.size / 3, align="center")

    poster = Image.composite(alpha_channel, poster, infos_mask)

    return poster


def track_content(frame: Image, cover: Image, track: core.Track,
                  title_font: ImageFont.FreeTypeFont, artist_font: ImageFont.FreeTypeFont,
                  time_font: ImageFont.FreeTypeFont, overlay_width, overlay_width_offset,
                  overlay_height_offset, alpha_channel: Image):
    poster = frame.copy()

    # Center cover parameters calculations
    center_cover_padding_sides = math.ceil(overlay_width * center_cover_padding_sides_percentage / 100)
    center_cover_padding_top = math.ceil(overlay_width * center_cover_padding_top_percentage / 100)

    center_cover_width_offset = overlay_width_offset + center_cover_padding_sides
    center_cover_height_offset = overlay_height_offset + center_cover_padding_top

    center_cover_width = math.ceil(overlay_width - center_cover_padding_sides * 2)

    # Place shadow
    poster = core.square_shadow(poster, (
        center_cover_width_offset,
        center_cover_height_offset,
        center_cover_width_offset + center_cover_width,
        center_cover_height_offset + center_cover_width
    ), resolution_multiplicator, )

    # Place cover in middle of overlay
    center_cover = cover.copy().resize((center_cover_width, center_cover_width))
    poster = core.rounded_corner_rectangle(
        poster, center_cover,
        (center_cover_width_offset, center_cover_height_offset),
        20 * resolution_multiplicator)

    # Write infos
    infos_mask = Image.new("L", poster.size, 0)
    draw = ImageDraw.Draw(infos_mask)
    y_offset = center_cover_height_offset + center_cover_width + 35 * resolution_multiplicator
    x_offset = math.ceil(poster.width / 2 - draw.textlength(track.title, font=title_font) / 2)
    draw.text((x_offset, y_offset), track.title, font=title_font, fill=255)
    y_offset += artist_font.size + title_font.size / 2
    x_offset = math.ceil(poster.width / 2 - draw.textlength(track.artist_name, font=artist_font) / 2)
    draw.text((x_offset, y_offset), track.artist_name, font=artist_font, fill=255)
    x_offset = center_cover_width_offset
    y_offset += 75 * resolution_multiplicator
    infos_mask = progress_bar(
        infos_mask,
        track.duration_raw,
        random.randint(5, 95),
        255,
        (x_offset, y_offset, x_offset + center_cover_width),
        time_font,
        resolution_multiplicator,
        time_font.size * 0.4
    )
    poster = Image.composite(alpha_channel, poster, infos_mask)
    return poster


def lyrics_picker(title: str, artist_name: str = ""):
    lyrics = core.genius_api.get_lyrics(title, artist_name)
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
                    max_width):
    formatted_title = text
    floor = len(formatted_title) - 1
    while draw.multiline_textbbox((0, 0), formatted_title, font)[2] > max_width:
        space_pos = 0
        for i in range(floor, 0, -1):
            if text[i] == " ":
                space_pos = i
                break
        new_string = ""
        for i in range(len(text)):
            if i == space_pos:
                new_string += "\n"
            else:
                new_string += text[i]
        formatted_title = new_string
        floor -= 1
        if floor < 1:
            formatted_title = text
            break
    return formatted_title


generator()