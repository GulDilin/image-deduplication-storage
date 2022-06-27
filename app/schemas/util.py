from enum import Enum
from pydantic import BaseModel
from datetime import datetime
import uuid


class ValuesEnum(Enum):
    @classmethod
    def values(cls):
        return [it.value for it in cls]

    @classmethod
    def from_value(cls, val):
        return [it for it in cls if it.value == val][0]


class TimeStamped(BaseModel):
    created_at: datetime
    updated_at: datetime


def is_valid_uuid(val):
    try:
        return uuid.UUID(str(val))
    except ValueError:
        return None
