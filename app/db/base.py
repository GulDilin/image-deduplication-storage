# Import all the models, so that Base has them before being
from app.db.base_class import Base  # noqa
from app.models.image import Image, Thumbnail  # noqa
