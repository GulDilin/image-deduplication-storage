from PIL import Image


def resize_image(
        input_path,
        output_path,
        size,
        is_grayscale=False
):
    original_image = Image.open(input_path)
    resized_image = original_image.resize(size)
    if is_grayscale:
        resized_image = resized_image.convert("L")
    resized_image.save(output_path)


def get_scaled_size(input_image_path, scale):
    with Image.open(input_image_path) as original_image:
        return (int(elem / scale) for elem in original_image.size)


def get_new_size(input_image_path, width, height):
    if width and height:
        return width, height
    with Image.open(input_image_path) as original_image:
        if not width and not height:
            raise ValueError('width or height or both are required')
        elif not width:
            k = height / original_image.size[1]
            width = int(k * original_image.size[0])
        elif not height:
            k = width / original_image.size[0]
            height = int(k * original_image.size[1])
        return width, height
