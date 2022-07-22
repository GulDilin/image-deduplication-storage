from PIL import Image, ImageChops, ImageDraw


def are_images_equal(img_1_path, img_2_path):
    img1 = Image.open(img_1_path)
    img2 = Image.open(img_2_path)
    diff = ImageChops.difference(img1, img2)
    return img1.size == img2.size and (diff.getbbox() is None)


def get_compare_image(img_1_path, img_2_path, output_path):
    img1 = Image.open(img_1_path)
    img2 = Image.open(img_2_path)
    diff = ImageChops.difference(img1, img2)
    pix = diff.load()
    draw = ImageDraw.Draw(diff)
    width, height = diff.size
    for x in range(width):
        for y in range(height):
            r = pix[x, y][0]
            g = pix[x, y][1]
            b = pix[x, y][2]
            sr = 0 if r or g or b else 255
            draw.point((x, y), (sr, sr, sr))
    diff.convert('RGB').save(output_path, 'JPEG')
