from typing import AsyncGenerator, Union
from uuid import UUID
from fastapi import Depends, Path
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import ImageCRUD, ThumbnailCRUD
from app.models import Image
from app import schemas
from app.db.session import async_session


async def get_db_session() -> AsyncSession:
    async with async_session() as session:
        async with session.begin():
            yield session


async def get_image_crud(
        session: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[AsyncSession, None]: yield ImageCRUD(session)


async def get_thumbnail_crud(
        session: AsyncSession = Depends(get_db_session)
) -> AsyncGenerator[AsyncSession, None]: yield ThumbnailCRUD(session)


async def get_path_image(
        image_crud: ImageCRUD = Depends(get_image_crud),
        image_id: Union[UUID, str] = Path(None, title="Image ID")
) -> Image:
    return await image_crud.get_by(**{'id' if schemas.is_valid_uuid(str(image_id)) else 'name': image_id})
