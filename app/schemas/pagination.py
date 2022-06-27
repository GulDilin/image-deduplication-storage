from typing import List, Optional

from fastapi import Request
from pydantic import AnyHttpUrl, BaseModel, validator
from starlette.datastructures import URL


class PaginatedResponse(BaseModel):
    results: List
    next: Optional[AnyHttpUrl]
    previous: Optional[AnyHttpUrl]
    amount: int


class PaginationData(BaseModel):
    request: Request
    limit: int = 10
    offset: int = 0

    @classmethod
    def _raise_for_negative(cls, v, field):
        if v < 0:
            raise ValueError(f"{field} need to be non-negative")

    @validator("limit")
    def validate_limit(cls, v):
        PaginationData._raise_for_negative(v, 'limit')
        return v

    @validator("offset")
    def validate_offset(cls, v):
        PaginationData._raise_for_negative(v, 'offset')
        return v

    class Config:
        arbitrary_types_allowed = True


async def paginate_response(
        paginated_response: PaginatedResponse,
        paginator: PaginationData
) -> PaginatedResponse:
    url = URL(str(paginator.request.url))
    paginated_response.previous = str(url.replace_query_params(
        limit=paginator.limit,
        offset=paginator.offset - paginator.limit
    )) if paginator.offset >= paginator.limit else None
    paginated_response.next = str(url.replace_query_params(
        limit=paginator.limit,
        offset=offset
    )) if (offset := paginator.offset + paginator.limit) < paginated_response.amount else None
    return paginated_response
