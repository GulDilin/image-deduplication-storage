import imagehash
from PIL import Image

hash_funcs = {
    "colorhash": lambda img_path: imagehash.colorhash(Image.open(img_path)),
    "phash": lambda img_path: imagehash.phash(Image.open(img_path)),
    "dhash": lambda img_path: imagehash.dhash(Image.open(img_path)),
    "average_hash": lambda img_path: imagehash.average_hash(Image.open(img_path)),
    "whash": lambda img_path: imagehash.whash(Image.open(img_path)),
    "whash-db4": lambda img_path: imagehash.whash(Image.open(img_path), mode='db4'),
    "crop_resistant_hash": lambda img_path: imagehash.crop_resistant_hash(Image.open(img_path)),
}


def test_imagehash_algs(path):
    for alg, func in hash_funcs.items():
        print(f'{alg:15s} = {str(func(path)):130s}')


print('-' * 100)
test_imagehash_algs('3.jpg')
print('-' * 100)
test_imagehash_algs('4.jpg')
