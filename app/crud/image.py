from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.core import message, util, error
from app.models import Image, Thumbnail
from app import schemas

from .common import DefaultCRUD


class ImageCRUD(DefaultCRUD):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session=db_session, model=Image, model_name=message.MODEL_IMAGE)

    async def raise_for_incorrect_format(self, file_name: str) -> None:
        file_type = util.get_file_type(file_name)
        if file_type not in schemas.ImageFormats.values():
            raise error.IncorrectDataFormat(
                allowed_formats=schemas.ImageFormats.values(),
                format=file_type,
                model=self.model_name,
            )

    async def create_and_write(
            self,
            original_filename: str,
            hash_value: str,
            file_data,
            name: str = None,
    ) -> Image:
        file_type = util.get_file_type(original_filename)
        await self.raise_for_incorrect_format(file_type)
        item = await self._create(item=Image(
            original_filename=original_filename[-300:],
            file_type=file_type,
            hash=hash_value,
            name=name,
        ))
        filename = util.generate_image_filename(image_id=item.id, file_type=file_type)
        util.save_image_to_storage(filename=filename, data=file_data)
        item.size = os.path.getsize(filename)
        return item

    async def create(
            self,
            original_filename: str,
            hash_value: str,
            name: str = None,
    ) -> Image:
        file_type = util.get_file_type(original_filename)
        await self.raise_for_incorrect_format(file_type)
        return await self._create(item=Image(
            original_filename=original_filename[-300:],
            file_type=file_type,
            hash=hash_value,
            name=name,
        ))

    async def increment_counter(self, image_id: UUID):
        try:
            image = await self.get(image_id)
            await self._update(item_id=image_id, obj_in={'duplicate_counter': image.duplicate_counter + 1})
        except:
            await self.db_session.rollback()

    async def update(self, image_id: UUID, obj_in: schemas.ImageUpdate) -> Image:
        if await self.has_by(name=obj_in.name):
            raise error.ImageNameUniqueCheckFailed()
        return await self._update(item_id=image_id, obj_in=obj_in)

    @staticmethod
    async def delete_content(item: Image) -> None:
        if (path := util.get_image_path(item)) and os.path.exists(path):
            os.remove(path)

    async def delete_with_content(self, item_id: UUID):
        item = await self.get(item_id)
        await self.delete_content(item)
        await self.delete(item_id)

    async def delete_by_with_content(self, **kwargs):
        items = await self.get_all(**kwargs)
        for item in items:
            await self.delete_content(item)
        await self._delete_by(**kwargs)


class ThumbnailCRUD(DefaultCRUD):
    def __init__(self, db_session: AsyncSession):
        super().__init__(db_session=db_session, model=Thumbnail, model_name=message.MODEL_THUMBNAIL)

    async def create_and_write(
            self,
            image: Image,
            width: int,
            height: int,
            file_type: str,
            file_data: bytes,
    ) -> Thumbnail:
        item = await self._create(item=Thumbnail(
            image_id=image.id,
            width=width,
            height=height,
            file_type=file_type,
        ))
        filename = util.generate_image_filename(image_id=item.id, file_type=file_type)
        util.save_image_to_storage(filename=filename, data=file_data)
        item.size = os.path.getsize(filename)
        return item

    async def create(
            self,
            image: Image,
            width: int,
            height: int,
            file_type: str,
    ) -> Thumbnail:
        return await self._create(item=Thumbnail(
            image_id=image.id,
            width=width,
            height=height,
            file_type=file_type,
        ))

    @staticmethod
    async def delete_content(item: Thumbnail) -> None:
        if (path := util.get_thumbnail_path(item)) and os.path.exists(path):
            os.remove(path)

    async def delete_with_content(self, item_id: UUID) -> None:
        item = await self.get(item_id)
        await self.delete_content(item)
        await self.delete(item_id)

    async def delete_by_with_content(self, **kwargs) -> None:
        items = await self.get_all(**kwargs)
        for item in items:
            await self.delete_content(item)
        await self._delete_by(**kwargs)
