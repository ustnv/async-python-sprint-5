import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import status

from models.models import FileModel


@pytest.mark.asyncio
async def test_ping_handler(client: AsyncClient, async_session: AsyncSession):
    response = await client.get('v1/ping')
    assert response.status_code == status.HTTP_200_OK
    assert response.json().items() >= {'api': 'v1'}.items()


@pytest.mark.asyncio
async def test_register_handler(client: AsyncClient, async_session: AsyncSession):
    data = {
        'email': 'test@test.com',
        'password': 'password'
    }
    response = await client.post(
        'v1/auth/register',
        json=data
    )
    assert response.status_code == 201
    assert response.json()['id'] is not None


@pytest.mark.asyncio
async def test_files_list_handler(async_session: AsyncSession, client_auth: AsyncClient):
    file = FileModel(created_by=client_auth.headers['user_id'], name='test', path='test', size=5)
    async_session.add(file)
    await async_session.commit()

    response = await client_auth.post('v1/files/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['files'][0]['name'] == 'test'


