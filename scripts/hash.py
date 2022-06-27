from time import time
import hashlib
import cv2
import zlib
import numpy as np
from PIL import Image, ImageChops, ImageDraw


def get_md_5_bytes_hash(bytes): return hashlib.md5(bytes).hexdigest()


def get_sha1_bytes_hash(bytes): return hashlib.sha1(bytes).hexdigest()


def get_sha224_bytes_hash(bytes): return hashlib.sha224(bytes).hexdigest()


def get_sha256_bytes_hash(bytes): return hashlib.sha256(bytes).hexdigest()


def get_sha384_bytes_hash(bytes): return hashlib.sha384(bytes).hexdigest()


def get_sha512_bytes_hash(bytes): return hashlib.sha512(bytes).hexdigest()


def get_adler_bytes_hash(bytes): return zlib.adler32(bytes)


def get_blake2b_bytes_hash(bytes): return hashlib.blake2b(bytes).hexdigest()


def get_hashlib_alg_bytes_hash(bytes, alg_name): return getattr(hashlib, alg_name)(bytes).hexdigest(
    *[it for it in ([(int(alg_name.rsplit('_', 2)[::-1][0]) - 1)] if alg_name.startswith('shake') else [])])


def hash_cv_pix_from_image_path(img_path, hash_func): return hash_func(np.array(cv2.imread(img_path)))


def hashlib_cv_pix_from_image_path(img_path, alg): return hash_cv_pix_from_image_path(img_path, lambda
    x: get_hashlib_alg_bytes_hash(x, alg))


def adler_cv_pix_from_image_path(img_path): return hash_cv_pix_from_image_path(img_path, get_adler_bytes_hash)


def diff(img_1_path, img_2_path):
    img1 = Image.open(img_1_path)
    img2 = Image.open(img_2_path)
    diff = ImageChops.difference(img1, img2)
    eql = img1.size == img2.size and (diff.getbbox() is None)
    print(f"{eql=}")
    if eql:
        return
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

    diff.show()


def alg_try(func, path, alg, is_bytes_arg=False, amount=1):
    start_time = time()
    h = None
    data_to_encode = None
    if is_bytes_arg:
        with open(path, 'rb') as file:
            data_to_encode = file.read()
    for i in range(amount):
        h = func(data_to_encode if is_bytes_arg else path)
    stop_time = time()
    print(f'{alg:15s} = {str(h):130s} time = {stop_time - start_time}')


def get_md5_and_sha_hash(path, amount=100):
    alg_try(lambda x: hashlib.md5(x).hexdigest(), path, 'md5', is_bytes_arg=True, amount=amount)
    for alg in hashlib.algorithms_guaranteed:
        alg_try(lambda x: hashlib_cv_pix_from_image_path(x, alg), path, f'rgba {alg}', is_bytes_arg=False,
                amount=amount)


print('-' * 100)
get_md5_and_sha_hash('./image1.jpg')
print('-' * 100)
get_md5_and_sha_hash('./image2.jpg')
