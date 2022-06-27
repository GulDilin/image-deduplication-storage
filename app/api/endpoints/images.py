import os.path
import traceback
from typing import Optional

from fastapi import APIRouter, Depends, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

from app import models, schemas
from app.api import deps
from app.core import hasher, image_resizer, util, error, message
from app.crud import ImageCRUD, ThumbnailCRUD

router = APIRouter()


@router.get('/', response_model=schemas.PaginatedResponse)
async def get_all_images(
        pagination_data: schemas.PaginationData = Depends(),
        image_crud: ImageCRUD = Depends(deps.get_image_crud),
) -> schemas.PaginatedResponse:
    data = await image_crud.get_all_with_pagination(
        wrapper_class=schemas.Image,
        offset=pagination_data.offset,
        limit=pagination_data.limit,
    )
    return await schemas.paginate_response(data, pagination_data)


@router.get('/{image_id}', response_model=schemas.Image)
async def get_image(
        image: models.Image = Depends(deps.get_path_image),
) -> schemas.Image:
    return schemas.Image(**jsonable_encoder(image))


@router.get('/{image_id}/file')
async def get_image_file(
        scale: float = None,
        w: int = None,
        h: int = None,
        image: models.Image = Depends(deps.get_path_image),
        image_crud: ThumbnailCRUD = Depends(deps.get_image_crud),
        thumbnail_crud: ThumbnailCRUD = Depends(deps.get_thumbnail_crud)
) -> FileResponse:
    try:
        path = util.get_image_path(image=image)
        if not os.path.exists(path):
            await image_crud.delete_with_content(image.id)
            await thumbnail_crud.delete_by_with_content(image_id=image.id)
        if scale:
            (w, h) = image_resizer.get_scaled_size(path, scale)
        if w or h:
            (w, h) = image_resizer.get_new_size(path, w, h)
            if not await thumbnail_crud.has_by(image_id=image.id, width=w, height=h):
                thumbnail = await thumbnail_crud.create(image=image, width=w, height=h, file_type=image.file_type)
                image_resizer.resize_image(path, util.get_thumbnail_path(thumbnail), (w, h))
            else:
                thumbnail = await thumbnail_crud.get_by(image_id=image.id, width=w, height=h)
            path = util.get_thumbnail_path(thumbnail)
        return FileResponse(
            path=path,
            headers={
                'Content-Type': f'image/{image.file_type}'
            }
        )
    except Exception as e:
        await image_crud.db_session.rollback()
        traceback.print_exc()
        raise e


@router.post('/', response_model=schemas.Image)
async def create_image(
        file: UploadFile,
        name: Optional[str] = None,
        image_crud: ImageCRUD = Depends(deps.get_image_crud),
) -> schemas.Image:
    try:
        file_data = file.file.read()
        hash_value = hasher.get_image_hash(file_data)
        if await image_crud.has_by(hash=hash_value):
            image = await image_crud.get_by(hash=hash_value)
            print(f'{image=}')
            await image_crud.increment_counter(image_id=image.id)
            return schemas.Image(**jsonable_encoder(image))
        image = await image_crud.create_and_write(
            original_filename=file.filename,
            hash_value=hash_value,
            file_data=file_data,
            name=name,
        )
        return schemas.Image(**jsonable_encoder(image))
    except Exception as e:
        await image_crud.db_session.rollback()
        traceback.print_exc()
        raise e


@router.put('/{image_id}', response_model=schemas.Image)
async def update_image(
        item_in: schemas.ImageUpdate,
        image: models.Image = Depends(deps.get_path_image),
        image_crud: ImageCRUD = Depends(deps.get_image_crud),
) -> schemas.Image:
    return schemas.Image(**jsonable_encoder(await image_crud.update(image_id=image.id, obj_in=item_in)))


@router.delete('/{image_id}')
async def delete_image(
        image: models.Image = Depends(deps.get_path_image),
        thumbnail_crud: ImageCRUD = Depends(deps.get_thumbnail_crud),
        image_crud: ImageCRUD = Depends(deps.get_image_crud),
) -> None:
    await image_crud.decrement_counter(image_id=image.id)
    if image.duplicate_counter <= 0:
        await thumbnail_crud.delete_by_with_content(image_id=image.id)
        await image_crud.delete_with_content(image.id)


@router.get('/{image_id}/thumbnails', response_model=schemas.PaginatedResponse)
async def get_image_thumbnails(
        pagination_data: schemas.PaginationData = Depends(),
        image: models.Image = Depends(deps.get_path_image),
        thumbnail_crud: ImageCRUD = Depends(deps.get_thumbnail_crud),
) -> schemas.PaginatedResponse:
    data = await thumbnail_crud.get_all_with_pagination(
        wrapper_class=schemas.Thumbnail,
        offset=pagination_data.offset,
        limit=pagination_data.limit,
        image_id=image.id,
    )
    return await schemas.paginate_response(data, pagination_data)


@router.get('/{image_id}/thumbnails/{thumbnail_id}', response_model=schemas.Thumbnail)
async def get_thumbnail(
        thumbnail: models.Thumbnail = Depends(deps.get_path_thumbnail),
) -> schemas.Thumbnail:
    return schemas.Thumbnail(**jsonable_encoder(thumbnail))


@router.get('/{image_id}/thumbnails/{thumbnail_id}/file')
async def get_thumbnail_file(
        thumbnail: models.Thumbnail = Depends(deps.get_path_thumbnail),
) -> FileResponse:
    path = util.get_thumbnail_path(thumbnail)
    return FileResponse(
        path=path,
        headers={
            'Content-Type': f'image/{thumbnail.file_type}'
        }
    )


@router.post('/{image_id}/thumbnails', response_model=schemas.Thumbnail)
async def create_image_thumbnail(
        item_in: schemas.ThumbnailCreate,
        image: models.Image = Depends(deps.get_path_image),
        thumbnail_crud: ThumbnailCRUD = Depends(deps.get_thumbnail_crud),
) -> schemas.Thumbnail:
    path = util.get_image_path(image=image)
    if item_in.scale:
        (item_in.width, item_in.height) = image_resizer.get_scaled_size(path, item_in.scale)
    (w, h) = image_resizer.get_new_size(path, item_in.width, item_in.height)
    if await thumbnail_crud.has_by(image_id=image.id, width=w, height=h):
        raise error.ItemAlreadyExists(model=message.MODEL_THUMBNAIL)
    thumbnail = await thumbnail_crud.create(image=image, width=w, height=h, file_type=image.file_type)
    image_resizer.resize_image(path, util.get_thumbnail_path(thumbnail), (w, h))
    return schemas.Thumbnail(**jsonable_encoder(thumbnail))


@router.delete('/{image_id}/thumbnails/{thumbnail_id}')
async def delete_thumbnail(
        thumbnail_crud: ThumbnailCRUD = Depends(deps.get_thumbnail_crud),
        thumbnail: models.Thumbnail = Depends(deps.get_path_thumbnail),
) -> None:
    await thumbnail_crud.delete_with_content(thumbnail.id)
