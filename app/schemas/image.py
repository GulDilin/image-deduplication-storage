from typing import Optional
from uuid import UUID

from pydantic import BaseModel

from .util import TimeStamped, ValuesEnum


class Image(TimeStamped):
    id: UUID
    original_filename: str
    file_type: str
    name: Optional[str]
    hash: str
    size: Optional[int]
    duplicate_counter: int


class ImageUpdate(BaseModel):
    name: str


class ImageCompareStatus(BaseModel):
    equal: bool


class Thumbnail(TimeStamped):
    id: UUID
    width: int
    height: int
    image_id: UUID


class ThumbnailCreate(BaseModel):
    scale: Optional[float]
    width: Optional[int]
    height: Optional[int]


class ImageFormats(ValuesEnum):
    JPG = 'jpg'
    JPEG = 'jpeg'
    PNG = 'png'
    WEBP = 'webp'
