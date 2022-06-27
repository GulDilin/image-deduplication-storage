import os

from app import models
from app.core.config import settings


def get_file_type(filename):
    return filename.rsplit('.', 1)[1] if '.' in filename else None


def save_to_storage(dir_path, filename, data):
    path = os.path.join(dir_path, filename)
    with open(path, 'wb') as f:
        f.write(data)


def save_image_to_storage(filename, data):
    save_to_storage(
        dir_path=settings.STORAGE_DIR,
        filename=filename,
        data=data
    )


def save_thumbnail_to_storage(filename, data):
    save_to_storage(
        dir_path=settings.THUMBNAILS_DIR,
        filename=filename,
        data=data
    )


def generate_image_filename(image_id, file_type):
    return f'{str(image_id)}.{file_type}'


def generate_thumbnail_filename(image_id, width, height, file_type):
    return f'{str(image_id)}_{width}x{height}.{file_type}'


def get_image_path(image: models.Image) -> str:
    return os.path.join(settings.STORAGE_DIR, generate_image_filename(
        image_id=image.id,
        file_type=image.file_type
    ))


def get_thumbnail_path(thumbnail: models.Thumbnail):
    return os.path.join(settings.STORAGE_DIR, generate_thumbnail_filename(
        image_id=thumbnail.image_id,
        width=thumbnail.width,
        height=thumbnail.height,
        file_type=thumbnail.file_type
    ))
