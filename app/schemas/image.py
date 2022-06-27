from .util import TimeStamped
from uuid import UUID
from .util import ValuesEnum
from pydantic import BaseModel


class Image(TimeStamped):
    id: UUID
    original_filename: str
    file_type: str
    name: str
    hash: str
    size: int
    duplicate_counter: int


class ImageUpdate(BaseModel):
    name: str


class Thumbnail(TimeStamped):
    id: UUID
    width: int
    height: int
    image_id: UUID


class ThumbnailCreate(BaseModel):
    width: int
    height: int
    image_id: UUID


class ImageFormats(ValuesEnum):
    JPG = 'jpg'
    JPEG = 'jpeg'
    PNG = 'png'
    WEBP = 'webp'
