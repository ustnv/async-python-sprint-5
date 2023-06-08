import datetime
import logging
import sys
import uuid
from shutil import copyfileobj

import aiofiles
import asyncpg
from fastapi import Depends, APIRouter, UploadFile
from sqlalchemy import text, exc
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.responses import FileResponse

from core.config import settings
from db.db import get_session
from models.models import User
from schemas.files import FileCreate
from services.files import file_crud
from services.users import current_active_user

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get('/ping', description='Check services status', summary='Check services status')
async def ping(db: AsyncSession = Depends(get_session)):
    logger.info('Test ping.')
    db_response_time = await ping_db(db)
    return {
        'api': 'v1',
        'python': sys.version_info,
        'db': db_response_time
    }


async def ping_db(db):
    logger.info('Test ping dependent services.')
    statement = text('SELECT version();')
    start = datetime.datetime.now()
    try:
        await db.execute(statement)
        ping_db_time = datetime.datetime.now() - start
        return ping_db_time
    except (exc.SQLAlchemyError, asyncpg.PostgresError) as err:
        return err.message


@router.post('/files/', description='Files list', summary='Files list')
async def files_list_handler(user: User = Depends(current_active_user), db: AsyncSession = Depends(get_session)):
    query = await file_crud.get_multi(db=db, created_by=str(user.id))
    return {"account_id": str(user.id), "files": query}


@router.post('/files/upload', description='Upload file', summary='Upload file')
async def upload_file_handler(
        file: UploadFile,
        path: str,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    logger.info('Save file.')
    id_ = uuid.uuid4()
    filename = file.filename
    out_file_path = rf'{settings.FILE_FOLDER}{id_}.' + filename.split('.')[-1]
    file_path = rf'{path}/{filename}'
    size = 0

    async with aiofiles.open(out_file_path, 'wb') as out_file:
        while content := await file.read(2 ** 16):
            size += len(content)  # async read chunk
            await out_file.write(content)  # async write chunk

    obj_in = FileCreate(
        id=id_,
        path=file_path,
        name=file.filename,
        size=size,
        created_by=user.id,
        is_downloadable=True
    )
    db_obj = await file_crud.create(db=db, obj_in=obj_in)
    return db_obj


@router.get('/files/download', description='Download file', summary='Download file')
async def download_file_handler(
        id_: uuid.UUID,
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    logger.info(f'Download file {id_}.')
    query = await file_crud.get_multi(db=db, id=id_, is_downloadable=True)
    file_model = query[0]

    return FileResponse(
        rf'{settings.FILE_FOLDER}{id_}.{file_model.name.split(".")[-1]}',
        media_type='application/octet-stream',
        filename=file_model.name
    )


@router.get('/user/status', status_code=status.HTTP_200_OK)
async def usage_memory(
        db: AsyncSession = Depends(get_session),
        user: User = Depends(current_active_user)
):
    logger.info('Get usage memory.')
    query = await file_crud.get_multi(db=db, created_by=str(user.id))

    return {
        "files": len(query),
        "used": sum([file.size for file in query])
    }
