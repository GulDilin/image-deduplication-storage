from dataclasses import dataclass
from typing import Iterable

from app.core import message


@dataclass
class ItemNotFound(Exception):
    model: str = "Item"

    def __str__(self) -> str:
        return message.ERROR_ITEM_NOT_FOUND.format(entity=self.model)


@dataclass
class IncorrectDataFormat(Exception):
    allowed_formats: Iterable = None
    format: str = None
    model: str = ''

    def __str__(self) -> str:
        return message.ERROR_INCORRECT_DATA_FORMAT.format(
            format=self.format or 'Format',
            model=self.model,
            formats=tuple(set(self.allowed_formats)) or ''
        )


class ImageNameUniqueCheckFailed(Exception):
    def __str__(self) -> str:
        return message.ERROR_IMAGE_NAME_UNIQUE


class StorageSaveError(Exception):
    def __str__(self) -> str:
        return message.ERROR_STORAGE_SAVE
