import hashlib
from PIL import Image
import io
import argparse
# import imagehash
from itertools import chain, product
import numpy as np

from PIL import ImageFile
ImageFile.LOAD_TRUNCATED_IMAGES = True


def get_md_5_bytes_hash(bytes):
    result = hashlib.md5(bytes).hexdigest()
    return result


def get_md_5_file_hash(file):
    with open(file, "rb") as f:
        return get_md_5_bytes_hash(f.read())


def md5_from_image_path(img_path, format="JPEG"):
    img = Image.open(img_path, mode='r')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format=format)
    img_byte_arr = img_byte_arr.getvalue()
    return get_md_5_bytes_hash(img_byte_arr)


def md5_color_from_image(img):
    pix = img.load()
    w, h = img.size
    bytes_arr = bytes(chain(*[pix[xy] for xy in product(range(w), range(h))]))
    return get_md_5_bytes_hash(bytes_arr)


def md5_color_from_image_path(img_path):
    img = Image.open(img_path)
    return md5_color_from_image(img)


def md5_convert_from_image(img, convert_to="RGBA"):
    na = np.array(img.convert(convert_to), dtype=np.byte)
    return get_md_5_bytes_hash(na)


def md5_convert_from_image_path(img_path, convert_to="RGBA"):
    img = Image.open(img_path)
    return md5_convert_from_image(img, convert_to)


def md5_cv_pix_from_image_path(img_path):
    import cv2
    img = cv2.imread(img_path)
    na = np.array(img)
    return get_md_5_bytes_hash(na)


def md5_ski_pix_from_image_path(img_path):
    from skimage import io
    na = io.imread(img_path)
    return get_md_5_bytes_hash(na)


def get_file_type(path):
    return path.rsplit(".", 1)[1]


hash_funcs = {
    # "colorhash": lambda img_path: imagehash.colorhash(Image.open(img_path)),
    # "phash": lambda img_path: imagehash.phash(Image.open(img_path)),
    # "dhash": lambda img_path: imagehash.dhash(Image.open(img_path)),
    # "average_hash": lambda img_path: imagehash.average_hash(Image.open(img_path)),
    # 'whash': lambda img_path: imagehash.whash(Image.open(img_path)),
    # 'whash-db4': lambda img_path: imagehash.whash(Image.open(img_path), mode='db4'),
    # "crop_resistant_hash": lambda img_path: imagehash.crop_resistant_hash(Image.open(img_path)),
    "md5": get_md_5_file_hash,
    "md5-image-jpeg": lambda img_path: md5_from_image_path(img_path, "JPEG"),
    "md5-image-png": lambda img_path: md5_from_image_path(img_path, "PNG"),
    "md5-image-color": md5_color_from_image_path,
    "md5-image-rgba": lambda img_path: md5_convert_from_image_path (img_path, "RGBA"),
    "md5-image-rgb": lambda img_path: md5_convert_from_image_path (img_path, "RGB"),
    "md5-image-cv": md5_cv_pix_from_image_path,
    "md5-image-ski": md5_ski_pix_from_image_path,
}

AVAILABLE_HASH_FUNCS = list(hash_funcs.keys())


def valid_hash_func_name(s):
    if s in hash_funcs:
        return s
    else:
        msg = "Not a valid hash func: '{0}'. Available: {1}".format(
            s, ", ".join(AVAILABLE_HASH_FUNCS))
        raise argparse.ArgumentTypeError(msg)


def valid_key_int_value(s):
    try:
        key, value = s.split("=", 2)
        if not key or not value:
            raise ValueError("Key and value are required")
        value = int(value)

        return {
            "key": key,
            "value": value
        }
    except:
        raise argparse.ArgumentTypeError("Not a valid key=int_value: '{0}'.".format(s))


def rm_el_from_str_path(path, index, ignore_parts=None):
    path = path.replace("\\", "/")
    parts = path.split("/")

    if parts and not parts[0]:
        parts = parts[1:]
    if ignore_parts:
        parts = [part for part in parts if part not in ignore_parts]

    if index == -1:
        parts = parts[:-1]
    else:
        parts = parts[:index] + parts[index+1:]
    return "/".join(parts)


def find_amount_of_similar_elements(list):
    list = sorted(list)
    summary = 0
    amount = 1

    for i, elem in enumerate(list[1:], 1):
        if elem == list[i - 1]:
            amount += 1
        else:
            if amount > 1:
                summary += amount
            amount = 1

    if amount > 1:
        summary += amount

    return summary


def execution_time(func):
    import time

    def wrapper(*args, **kwargs):
        start = time.time()
        return_value = func(*args, **kwargs)
        end = time.time()
        print('Execution time: {} s.'.format(end-start))
        return return_value
    return wrapper


SUFFIXES = {1000: ['KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'],
            1024: ['KiB', 'MiB', 'GiB', 'TiB', 'PiB', 'EiB', 'ZiB', 'YiB']}


def approximate_size(size, a_kilobyte_is_1024_bytes=False):
    if size < 0:
        raise ValueError('number must be non-negative')

    multiple = 1024 if a_kilobyte_is_1024_bytes else 1000
    for suffix in SUFFIXES[multiple]:
        size /= multiple
        if size < multiple:
            return '{0:.1f} {1}'.format(size, suffix)

    raise ValueError('number too large')
