import hashlib
import numpy as np
import cv2


def get_hashlib_alg_bytes_hash(bytes, alg_name):
    hash_func = getattr(hashlib, alg_name)
    if alg_name.startswith('shake'):
        arg = int(alg_name.rsplit('_', 2)[::-1][0]) - 1
        return hash_func(bytes).hexdigest(arg)
    else:
        return hash_func(bytes).hexdigest(arg)


def hash_cv_pix_from_image_path(img_path, hash_func):
    return hash_func(np.array(cv2.imread(img_path)))


def hashlib_cv_pix_from_image_path(img_path, alg):
    return hash_cv_pix_from_image_path(
        img_path,
        lambda x: get_hashlib_alg_bytes_hash(x, alg)
    )


hash_functions = {
    alg: lambda x: hashlib_cv_pix_from_image_path(x, alg)
    for alg in hashlib.algorithms_guaranteed
}
