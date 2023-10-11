from PIL import Image
import core


image_link = core.getAlbum(input("album > ")).cover_link
image = Image.open(image_link)

reduction = 50
autoreduction = 50
channels = "RGB"

small_cover = image.reduce(reduction).convert(channels)
constant_pixels = []
for i in range(small_cover.size[0]):
    for j in range(small_cover.size[1]):
        constant_pixels.append(small_cover.getpixel((i, j)))
print(constant_pixels)


def distance_couleur(couleur1, couleur2):
    r1, g1, b1 = couleur1
    r2, g2, b2 = couleur2
    # return math.sqrt((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2)
    # return abs(r1 - r2) + abs(g1 - g2) + abs(b1 - b2)
    return max(max(abs(r1 - r2), abs(g1 - g2)), b1 - b2)


important_pixels = []
index = 100
pixels = []
while len(important_pixels) != 5:
    important_pixels = []
    pixels = []
    for i in range(small_cover.size[0]):
        for j in range(small_cover.size[1]):
            pixels.append(small_cover.getpixel((i, j)))
    for i in range(len(pixels)):
        for j in range(i + 1, len(pixels)):
            if pixels[i] is not None and pixels[j] is not None:
                if distance_couleur(pixels[i], pixels[j]) < index:
                    pixels[j] = None
    for i in range(len(pixels)):
        if pixels[i] is not None:
            important_pixels.append(pixels[i])
    if len(important_pixels) > 5:
        index += 2
    elif len(important_pixels) < 5:
        index -= 2
    if index < 90:
        break

print(str(important_pixels) + str(index))

for i in range(len(important_pixels)):
    Image.new("RGB", (300, 300), important_pixels[i]).show()
