import asyncio
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import sessionmaker

from db.db import get_session
from main import app
from core.config import settings
from models.models import Base
from services.users import auth_backend

TEST_DATABASE_URL = (
    f'postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}'
    f'@{settings.DB_HOST}:{settings.DB_PORT}'
    f'/{settings.TEST_DB_NAME}'
)

@pytest_asyncio.fixture(scope='session')
async def client() -> AsyncGenerator:
    async with AsyncClient(
        app=app,
        follow_redirects=False,
        base_url='http://testserver',
    ) as client:
        yield client


@pytest.fixture(scope='session')
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope='session')
async def initial_db() -> tuple[AsyncEngine, AsyncSession]:
    test_engine = create_async_engine(TEST_DATABASE_URL, future=True)
    test_async_session = sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session_func() -> AsyncSession:
        async with test_async_session() as session:
            yield session

    app.dependency_overrides[get_session] = get_session_func

    return test_engine, test_async_session


@pytest.fixture(scope='function')
async def async_session(initial_db) -> AsyncGenerator:
    test_engine, test_async_session = initial_db
    async with test_async_session() as s:
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        yield s
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()


@pytest_asyncio.fixture()
async def client_auth(async_session) -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url='http://test') as client:
        data = {
            'username': 'Mike@post.com',
            'email': 'Mike@post.com',
            'password': '12345'
        }
        response = await client.post(
            'v1/auth/register',
            json=data
        )
        assert response.status_code == 201
        user_id = response.json().get('id')
        response = await client.post(
            'v1/auth/jwt/login',
            data=data
        )
        assert response.status_code == 200
        assert 'access_token' in response.json()
        token = response.json().get('access_token')
        client.headers.update({'Authorization': f'Bearer {token}', 'user_id': user_id})
        yield client


# @pytest.fixture(scope="session")
# async def headers_with_token(user):
#     token = await auth_backend.get_strategy().write_token(user)
#     yield {'Authorization': f'Bearer {token}'}