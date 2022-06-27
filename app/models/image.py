import uuid

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from .util import TimeStamped


class Image(TimeStamped):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    original_filename = Column(String(300), unique=False)
    file_type = Column(String(50), unique=False)
    name = Column(String(300), unique=True)
    hash = Column(String(512), unique=True, index=True)
    size = Column(Integer)
    duplicate_counter = Column(Integer, default=1, server_default="1", nullable=False)
    thumbnails = relationship('Thumbnail', back_populates='image', cascade="delete")

    def __repr__(self):
        return '<Image %r, %r, %r, %r>' % (self.id, self.hash, self.original_filename, self.duplicate_counter)


class Thumbnail(TimeStamped):
    id = Column(UUID(as_uuid=True), primary_key=True, index=True, default=uuid.uuid4)
    file_type = Column(String(50), unique=False)
    width = Column(Integer)
    height = Column(Integer)
    size = Column(Integer)
    image_id = Column(UUID(as_uuid=True), ForeignKey("image.id"), nullable=False, index=True)
    image = relationship('Image', back_populates='thumbnail', cascade="delete")

    def __repr__(self):
        return '<Thumbnail %r, %r>' % (self.id, self.name)
