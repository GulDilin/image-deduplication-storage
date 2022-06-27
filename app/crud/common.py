from typing import Any, Callable, Iterable, List, Type
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from sqlalchemy import delete, func, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import joinedload
from sqlalchemy.sql.selectable import Select

from app import schemas
from app.core import error
from app.db.base_class import Base


class DefaultCRUD:
    def __init__(self, db_session: AsyncSession, model, model_name):
        self.db_session = db_session
        self.model = model
        self.model_name = model_name

    def _define_filter_part(self, key: Any, value: Any):
        if type(value) == type(bool):
            return getattr(self.model, key).is_(value)
        if isinstance(value, list):
            return getattr(self.model, key).in_(value)
        return getattr(self.model, key) == value

    def _define_filter(self, query, filter_dict: dict, and_: bool):
        if and_:
            for k, v in filter_dict.items():
                query = query.where(self._define_filter_part(k, v))
        else:
            query = query.filter(or_(*(self._define_filter_part(k, v) for k, v in filter_dict.items())))
        return query

    def _define_prefetch_fields(self, query, prefetch_fields: Iterable):
        if prefetch_fields is not None:
            for field in prefetch_fields:
                query = query.options(joinedload(getattr(self.model, field)))
        return query

    @staticmethod
    def _define_query_modifiers(query, query_modifiers: Iterable):
        if query_modifiers is not None:
            for modifier in query_modifiers:
                query = modifier(query)
        return query

    def _create_query_by(
            self,
            offset: int = None,
            limit: int = None,
            prefetch_fields: List[str] = None,
            query_modifiers: List[Callable] = None,
            selectable: Any = None,
            and_: bool = True,
            query: any = None,
            operator: any = select,
            **kwargs
    ) -> Select:
        q = query or operator(selectable or self.model)
        q = self._define_filter(query=q, filter_dict=kwargs, and_=and_)
        q = self._define_prefetch_fields(query=q, prefetch_fields=prefetch_fields)
        q = self._define_query_modifiers(query=q, query_modifiers=query_modifiers)
        if offset is not None:
            q = q.offset(offset)
        if limit is not None:
            q = q.limit(limit)
        return q

    async def get_all(self, offset: int = 0, limit: int = None, **kwargs) -> List:
        return (await self.db_session.execute(
            self._create_query_by(offset=offset, limit=limit, **kwargs))).scalars().all()

    async def count(self, predicate: Any = None, **kwargs):
        if not predicate:
            predicate = self.model.id
        q = self._create_query_by(selectable=func.count(predicate), **kwargs)
        return (await self.db_session.execute(q)).scalar_one()

    async def get(self, item_id: UUID) -> Any:
        if item := (await self.db_session.execute(select(self.model).where(self.model.id == item_id))).scalar():
            return item
        raise error.ItemNotFound(model=self.model_name)

    async def get_by(self, **kwargs) -> Any:
        if item := (await self.db_session.execute(self._create_query_by(**kwargs))).scalar():
            return item
        raise error.ItemNotFound(model=self.model_name)

    async def has(self, item_id: UUID) -> bool:
        return bool((await self.db_session.execute(select(self.model).where(self.model.id == item_id))).scalar())

    async def has_by(self, **kwargs) -> bool:
        return bool(await self.get_by(**kwargs))

    async def get_all_with_pagination(
            self,
            *args,
            wrapper_class: Type[BaseModel],
            offset: int = 0,
            limit: int = None,
            method: Callable = None,
            **kwargs
    ) -> schemas.PaginatedResponse:
        if not method:
            method = self.get_all
        count = await self.count(**kwargs)
        results = [
            wrapper_class(**jsonable_encoder(it)) for it in
            await method(offset=offset, limit=limit, *args, **kwargs)
        ]
        return schemas.PaginatedResponse(results=results, count=count)

    async def _add_all(self, objects: Any) -> Any:
        try:
            self.db_session.add_all(objects)
            await self.db_session.flush()  # noqa
            return objects
        except Exception as e:
            await self.db_session.rollback()  # noqa
            raise e

    async def _create(self, item: Base, no_return: bool = False) -> Any:
        try:
            self.db_session.add(item)
            await self.db_session.flush()  # noqa
            if not no_return:
                return await self.get(item.id)
        except Exception as e:
            await self.db_session.rollback()  # noqa
            raise e

    async def _update(self, item_id: UUID, obj_in: Any) -> Any:
        if not self.has(item_id):
            raise error.ItemNotFound(model=self.model_name)
        q = (
            update(self.model)
            .where(self.model.id == item_id)
            .values(**jsonable_encoder(obj_in))
            .execution_options(synchronize_session="fetch")
        )
        try:
            await self.db_session.execute(q)
            return await self.get(item_id)
        except Exception as e:
            await self.db_session.rollback()  # noqa
            raise e

    async def delete(self, item_id: UUID) -> None:
        item = await self.get(item_id)
        if not item:
            raise error.ItemNotFound(model=self.model_name)
        await self.db_session.delete(item)
        await self.db_session.flush()  # noqa

    async def _delete_by(self, **kwargs):
        await self.db_session.execute(self._create_query_by(operator=delete, **kwargs))
        await self.db_session.flush()  # noqa
