from PIL import Image, ImageDraw
import core
import math

# TODO: Second poster generator algorythme

poster_width_percentage = 68
resolution_multiplicator = 1
background_color = (234, 212, 199)
center_image_padding_sides_percentage = 6
center_image_padding_top_percentage = 5.5
color_size_percentage = 6
colors_spacing = 0.3


image_link = core.getAlbum(input("album > ")).cover_link
image = Image.open(image_link)

reduction = 50
channels = "RGB"

small_cover = image.reduce(reduction).convert(channels)
constant_pixels = []
for i in range(small_cover.size[0]):
    for j in range(small_cover.size[1]):
        constant_pixels.append(small_cover.getpixel((i, j)))


def distance_couleur(couleur1, couleur2):
    r1, g1, b1 = couleur1
    r2, g2, b2 = couleur2
    # return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)
    # return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
    # return max(max(abs(r1 - r2), abs(g1 - g2)), b1 - b2) - min(min(abs(r1 - r2), abs(g1 - g2)), b1 - b2)
    # return max(max(abs(r1 - r2), abs(g1 - g2)), b1 - b2) + min(min(abs(r1 - r2), abs(g1 - g2)), b1 - b2)
    return max(max(abs(r1 - r2), abs(g1 - g2)), b1 - b2)


def average_color(colors):
    r_sum = 0
    g_sum = 0
    b_sum = 0
    for a in range(len(colors)):
        r, g, b = colors[a]
        r_sum += r
        g_sum += g
        b_sum += b
    return math.ceil(r_sum / len(colors)), math.ceil(g_sum / len(colors)), math.ceil(b_sum / len(colors))


def invert_color(color_to_invert):
    r, g, b = color_to_invert
    return 255 - r, 255 - g, 255 - b


important_pixels = []
default_threshold = 80
threshold = default_threshold
pixels = []
skip_to = 0
while len(important_pixels) != 5:
    important_pixels = []
    pixels = []
    for i in range(small_cover.size[0]):
        for j in range(small_cover.size[1]):
            pixels.append(small_cover.getpixel((i, j)))
    for i in range(len(pixels)):
        for j in range(i + 1, len(pixels)):
            if pixels[i] is not None and pixels[j] is not None:
                if distance_couleur(pixels[i], pixels[j]) < threshold:
                    pixels[j] = None
    for i in range(len(pixels)):
        if pixels[i] is not None:
            important_pixels.append(pixels[i])
    if len(important_pixels) > 5:
        threshold += 2
    elif len(important_pixels) < 5:
        threshold -= 2
    if threshold < default_threshold * (2/3):
        skip_to = len(important_pixels)
        threshold = default_threshold
    if len(important_pixels) == skip_to:
        break

background_color = invert_color(average_color(constant_pixels))

print(str(important_pixels) + str(threshold))

poster_height = math.ceil(image.size[1] * resolution_multiplicator)
poster_width = math.ceil(poster_height * poster_width_percentage / 100)
poster = Image.new(channels,
                   (poster_width, poster_height),
                   background_color)

center_image_padding_sides = math.ceil(center_image_padding_sides_percentage * poster_width / 100)
center_image_padding_top = math.ceil(center_image_padding_top_percentage * poster_width / 100)
center_image_size = math.ceil(poster_width - center_image_padding_sides * 2)

cover = image.copy().resize((center_image_size, center_image_size))
poster.paste(cover, (center_image_padding_sides, center_image_padding_top))

draw = ImageDraw.Draw(poster)

top_offset = math.ceil(center_image_padding_top * 1.5 + center_image_size)
color_size = math.ceil(color_size_percentage * poster_width / 100)
for i in range(len(important_pixels)):
    color = Image.new(channels, (color_size, color_size), important_pixels[i])
    horizontal_offset = math.ceil(poster_width - center_image_padding_sides - (color_size * i * colors_spacing) - (color_size * (i+1)))
    poster.paste(color, (horizontal_offset, top_offset))

poster.show()
