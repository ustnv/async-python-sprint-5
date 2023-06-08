import logging

import uvicorn
from fastapi import FastAPI

from api.v1.auth import api_auth_router
from api.v1.routes import router
from core.config import settings

logger = logging.getLogger(__name__)


app = FastAPI(
    title=settings.APP_TITLE,
)

app.include_router(router, prefix='/v1', tags=['v1'],)
app.include_router(api_auth_router, prefix='/v1', tags=['auth'],)


if __name__ == '__main__':
    uvicorn.run('main:app', host=settings.PROJECT_HOST, port=settings.PROJECT_PORT, reload=True)
