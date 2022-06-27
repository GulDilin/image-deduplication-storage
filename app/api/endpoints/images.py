import os.path

from fastapi import APIRouter, Depends, UploadFile
from fastapi.encoders import jsonable_encoder
from fastapi.responses import FileResponse

from app import models, schemas
from app.api import deps
from app.core import hasher, image_resizer, util
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


@router.get('/{image_id}/file', response_model=FileResponse)
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
            headers={"Content-Disposition": f"attachment; filename={os.path.basename(path)}"}
        )
    except:
        await image_crud.db_session.rollback()


@router.post('/', response_model=schemas.Image)
async def create_image(
        file: UploadFile,
        name: str,
        image_crud: ImageCRUD = Depends(deps.get_image_crud),
) -> schemas.Image:
    try:
        file_data = file.file.read()
        hash_value = hasher.get_image_hash(file_data)
        if await image_crud.has_by(hash=hash_value):
            image = await image_crud.get_by(hash=hash_value)
            await image_crud.increment_counter(image_id=image.id)
            return schemas.Image(**jsonable_encoder(image))
        image = await image_crud.create_and_write(
            original_filename=file.filename,
            hash_value=hash_value,
            file_data=file_data,
            name=name,
        )
        return schemas.Image(**jsonable_encoder(image))
    except:
        await image_crud.db_session.rollback()


@router.put('/{image_id}', response_model=schemas.Image)
async def update_image(
        item_in: schemas.ImageUpdate,
        image: models.Image = Depends(deps.get_path_image),
        image_crud: ImageCRUD = Depends(deps.get_image_crud),
) -> schemas.Image:
    return await image_crud.update(image_id=image.id, obj_in=item_in)
