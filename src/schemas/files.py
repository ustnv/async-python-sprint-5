import datetime
from typing import Any

from pydantic import BaseModel
from pydantic.types import UUID


class FileBase(BaseModel):
    id: UUID
    name: str
    path: str
    size: int
    is_downloadable: bool


class FileCreate(FileBase):
    user_id: UUID


class FileUpdate(FileBase):
    updated_by: UUID


class FileInDBBase(FileBase):
    created_at: datetime.datetime | None

    class Config:
        orm_mode = True


class Ping(BaseModel):
    api: str
    python: list
    db: datetime.timedelta


class Files(BaseModel):
    account_id: str
    files: list[FileInDBBase]


class MemoryUsage(BaseModel):
    files: int
    used: int
