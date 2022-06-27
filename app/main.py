import logging
import os
import traceback

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.api.api import api_router
from app.core import error
from app.core.config import settings

logger = logging.getLogger(__name__)

# automatic run migrations at start, useful for docker
if settings.AUTORUN_MIGRATIONS and (rc := os.system('python -m alembic upgrade head') != 0):
    exit(rc)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url="/openapi.json",
)

app.mount("/stored", StaticFiles(directory=settings.STORAGE_DIR), name="stored")

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

logger.info('Start')

app.include_router(api_router, prefix="/api")


def handle_default_error(exc: Exception, status_code: int, headers: dict = None) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={'detail': str(exc)},
        headers=headers
    )


@app.exception_handler(Exception)
async def internal_server_error_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa
    logging.error(traceback.format_exc())
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={'detail': "Internal Server Error"},
    )


@app.exception_handler(error.IncorrectDataFormat)
@app.exception_handler(ValueError)
async def request_error_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa
    return handle_default_error(exc, status.HTTP_400_BAD_REQUEST)


@app.exception_handler(error.ItemNotFound)
async def entity_entry_not_found_exception_handler(request: Request, exc: Exception) -> JSONResponse:  # noqa
    return handle_default_error(exc, status.HTTP_404_NOT_FOUND)
