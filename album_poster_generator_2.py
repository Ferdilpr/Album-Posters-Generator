from PIL import Image
import math

absolute_directory = ""

image = Image.open(
    absolute_directory + "downloaded_covers/UNE MAIN LAVE L'AUTRE - Alpha Wann.jpg")

reduction = 50
autoreduction = 50
channels = "RGB"

small_cover = image.reduce(reduction)
pixels = list()
for i in range(math.ceil(1000 / reduction)):
    for j in range(math.ceil(1000 / reduction)):
        pixels.append(small_cover.getpixel((i, j)))


def distance_couleur(couleur1, couleur2):
    r1, g1, b1 = couleur1
    r2, g2, b2 = couleur2
    return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)


important_pixels = []
pixels = []
for x in range(small_cover.size[0]):
    for y in range(small_cover.size[1]):
        pixels.append(small_cover.getpixel((x, y)))

for i in range(len(pixels)):
    for j in range(i, len(pixels)):
        if pixels[j] is not None and pixels[i] is not None:
            if distance_couleur(pixels[i], pixels[j]) < 10:
                pixels[j] = None

i = 0
while None in pixels:
    if pixels[i] is None:
        pixels.pop(i)
    else:
        i += 1

print(pixels)
