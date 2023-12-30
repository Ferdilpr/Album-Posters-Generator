import math
import random

import core
from PIL import Image, ImageDraw, ImageFont
import pyexiv2

# Parameters
resolution_multiplicator = 2
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


def progress_bar(background: Image.Image,
                 duration_raw: int,
                 progress_percentage: int,
                 color: tuple[int, int, int],
                 xy,
                 time_font: ImageFont.FreeTypeFont,
                 resolution_multiplicator: float,
                 width):
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
        Image.new("RGB", (
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


def generator(show_lyrics: bool, height=None):
    # Getting track
    track_to_get = input("titre > ")
    track = core.search_track(track_to_get, download_cover=True)
    cover = track.cover

    title_font_size = math.ceil(min(30.0, 30 - max(0, len(track.title) - 5) * 0.3) * resolution_multiplicator)
    title_font = ImageFont.truetype(
        font.bold,
        size=title_font_size
    )
    artist_font_size = math.ceil(min(25.0, 25 - max(0, len(track.artist.name) - 8) * 0.425) * resolution_multiplicator)
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
        size=40 * resolution_multiplicator
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

    if show_lyrics:
        print(track.title + " - " + track.artist.name)
        lyrics = core.lyrics_picker(track.title, track.artist.name)

        top_cover_padding = 30 * resolution_multiplicator
        top_cover_side = 80 * resolution_multiplicator
        top_cover = cover.copy().resize((top_cover_side, top_cover_side))
        top_cover_radius = 15 * resolution_multiplicator
        lyrics_padding = (30 * resolution_multiplicator, 50 * resolution_multiplicator)

        draw = ImageDraw.Draw(background)

        title_font = core.format_too_long(track.title, draw, title_font,
                                          overlay_width - top_cover_padding * 3 - top_cover_side)

        formatted_lyrics = ""
        lyrics = lyrics.removesuffix("\n")
        for lyric in lyrics.rsplit("\n"):
            formatted_lyrics += core.format_too_long(
                lyric,
                draw,
                lyrics_font,
                overlay_width - lyrics_padding[0] * 2,
                wrap=True
            ) + "\n"
        formatted_lyrics = formatted_lyrics.removesuffix("\n\n").removeprefix("\n").removeprefix("\n")
        lyrics_size = draw.multiline_textbbox((0, 0), formatted_lyrics, lyrics_font, spacing=lyrics_font.size / 3)

        overlay_height = top_cover_padding + top_cover_side + lyrics_padding[1] * 2 + lyrics_size[3]
    else:
        center_cover_padding_sides = math.ceil(overlay_width * center_cover_padding_sides_percentage / 100)
        center_cover_padding_top = math.ceil(overlay_width * center_cover_padding_top_percentage / 100)
        center_cover_width = math.ceil(overlay_width - center_cover_padding_sides * 2)
        overlay_height = (3 * center_cover_padding_top + center_cover_width + 35 * resolution_multiplicator +
                          artist_font.size + title_font.size / 2 + 75 * resolution_multiplicator)

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
                                     blur_radius=(55 * (variant == 0 or variant == 1)) + (27.5 * (variant == 2)),
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

    if show_lyrics:
        poster = lyrics_content(poster, track.title, track.artist.name, formatted_lyrics, top_cover_side,
                                resolution_multiplicator, top_cover, top_cover_padding, title_font, artist_font,
                                overlay_width, overlay_width_offset, overlay_height_offset, 128,
                                lyrics_font, overlay_height, top_cover_radius, lyrics_padding, lyrics_size)
    else:
        poster = track_content(poster, cover, track, title_font, artist_font, time_font,
                               center_cover_width, overlay_width_offset, overlay_height_offset,
                               110, center_cover_padding_sides, center_cover_padding_top)

    target_file_name = "results/" + "Poster " + track.title + " - " + track.artist.name + ".png"
    poster.save(target_file_name)
    #metadata = pyexiv2.Image(target_file_name)
    #metadata.modify_exif({'Exif.Image.Artist': "Ferdi_lpr"})
    core.google_photo_api.cloud_upload(target_file_name.removeprefix("results/"))
    poster.show()


def lyrics_content(poster: Image.Image, title: str, artist_name: str, lyrics: str, top_cover_side,
                   resolution_multiplicator, top_cover: Image.Image, top_cover_padding,
                   title_font: ImageFont.FreeTypeFont, artist_font: ImageFont.FreeTypeFont,
                   overlay_width, overlay_width_offset, overlay_height_offset, text_color_threshold,
                   lyrics_font: ImageFont.FreeTypeFont, overlay_height, top_cover_radius,
                   lyrics_padding: tuple[float, float], lyrics_size):
    poster = core.rounded_corner_rectangle(poster, top_cover, (
        overlay_width_offset + top_cover_padding,
        overlay_height_offset + top_cover_padding
    ), top_cover_radius, 1)

    draw = ImageDraw.Draw(poster)

    color = core.background_color(poster, (
        overlay_width_offset + top_cover_side + top_cover_padding * 2,
        overlay_height_offset + top_cover_padding,
        overlay_width_offset + overlay_width - top_cover_padding,
        overlay_height_offset + top_cover_padding + top_cover_side
    ), text_color_threshold)

    x_offset = overlay_width_offset + top_cover_padding * 2 + top_cover_side
    y_offset = overlay_height_offset + top_cover_padding + top_cover_radius / 2
    draw.multiline_text((x_offset, y_offset), title, color, title_font, spacing=resolution_multiplicator)

    x_offset = overlay_width_offset + top_cover_padding * 2 + top_cover_side
    y_offset = overlay_height_offset + top_cover_padding + top_cover_side - artist_font.size - top_cover_radius / 2
    draw.text((x_offset, y_offset), artist_name, color, artist_font)

    lyrics_height_offset = ((overlay_height_offset + overlay_height - lyrics_size[3] - lyrics_padding[1]) +
                            (overlay_height_offset + top_cover_padding + top_cover_side + lyrics_padding[1])) / 2
    lyrics_width_offset = ((overlay_width_offset + lyrics_padding[0]) +
                           (overlay_width_offset + overlay_width - lyrics_padding[0] - lyrics_size[2])) / 2
    color = core.background_color(poster,
                                  (
                                      lyrics_width_offset,
                                      lyrics_height_offset,
                                      lyrics_width_offset + lyrics_size[2],
                                      lyrics_height_offset + lyrics_size[3]),
                                  text_color_threshold)
    draw.multiline_text((lyrics_width_offset, lyrics_height_offset), lyrics,
                        color, lyrics_font, spacing=lyrics_font.size / 3, align="center")

    return poster


def track_content(frame: Image.Image, cover: Image.Image, track: core.Track,
                  title_font: ImageFont.FreeTypeFont, artist_font: ImageFont.FreeTypeFont,
                  time_font: ImageFont.FreeTypeFont, center_cover_width, overlay_width_offset,
                  overlay_height_offset, text_color_threshold, center_cover_padding_sides,
                  center_cover_padding_top):
    poster = frame.copy()

    center_cover_width_offset = overlay_width_offset + center_cover_padding_sides
    center_cover_height_offset = overlay_height_offset + center_cover_padding_top

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
    draw = ImageDraw.Draw(poster)

    y_offset = center_cover_height_offset + center_cover_width + 35 * resolution_multiplicator
    x_offset = math.ceil(poster.width / 2 - draw.textlength(track.title, font=title_font) / 2)
    text_size = draw.textbbox((0, 0), track.title, font=title_font)
    color = core.background_color(
        poster,
        (x_offset, y_offset, x_offset + text_size[2], y_offset + text_size[3]),
        text_color_threshold
    )
    draw.text((x_offset, y_offset), track.title, font=title_font, fill=color)

    y_offset += artist_font.size + title_font.size / 2
    x_offset = math.ceil(poster.width / 2 - draw.textlength(track.artist.name, font=artist_font) / 2)
    text_size = draw.textbbox((0, 0), track.artist.name, font=artist_font)
    color = core.background_color(
        poster,
        (x_offset, y_offset, x_offset + text_size[2], y_offset + text_size[3]),
        text_color_threshold
    )
    draw.text((x_offset, y_offset), track.artist.name, font=artist_font, fill=color)

    x_offset = center_cover_width_offset
    y_offset += 75 * resolution_multiplicator
    size = (x_offset, y_offset, x_offset + center_cover_width, y_offset + time_font.size)
    color = core.background_color(poster, size, text_color_threshold)
    poster = progress_bar(
        poster,
        track.duration_raw,
        random.randint(5, 95),
        color,
        size,
        time_font,
        resolution_multiplicator,
        time_font.size * 0.4
    )
    return poster
