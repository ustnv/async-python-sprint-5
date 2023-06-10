import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from api.v1.routes import router
from main import app
from models.models import File


async def test_ping_handler(client: AsyncClient, async_session: AsyncSession):
    response = await client.get(app.url_path_for('ping'))
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= {'api': 'v1'}.items()


async def test_register_handler(client: AsyncClient, async_session: AsyncSession):
    data = {
        'email': 'test@test.com',
        'password': 'password'
    }
    response = await client.post(
        app.url_path_for('register:register'),
        json=data
    )
    assert response.status_code == 201
    assert response.json()['id'] is not None


async def test_files_list_handler(async_session: AsyncSession, client_auth: AsyncClient):
    file = File(user_id=client_auth.headers['user_id'], name='test', path='test', size=5)
    async_session.add(file)
    await async_session.commit()

    response = await client_auth.post(app.url_path_for('files_list_handler'))

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['files'][0]['name'] == 'test'
