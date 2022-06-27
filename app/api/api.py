from fastapi import APIRouter

from .endpoints import images

api_router = APIRouter()
for router in [(images.router, "/images", ["images"])]:
    api_router.include_router(router[0], prefix=router[1], tags=router[2])
