from PIL import Image
import core
import math


image_link = core.getAlbum(input("album > ")).cover_link
image = Image.open(image_link)

reduction = 10
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


important_pixels = []
default_threshold = 120
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

print(str(important_pixels) + str(threshold))


result = image.copy()
for i in range(len(important_pixels)):
    color = Image.new(channels, (math.ceil(image.size[0] / len(important_pixels)), 150), important_pixels[i])
    result.paste(color, (math.ceil(i * (image.size[0] / len(important_pixels))), 0))
result.show()
