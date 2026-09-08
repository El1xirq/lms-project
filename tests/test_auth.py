from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_registration_user(client: AsyncClient, db_session):
    response = await client.post(
        "/auth/register", 
        json={
        "email": "test@example.com",
        "password": "password123",
        "role": "student"
        })
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == 'Bearer'


@pytest.mark.asyncio
async def test_duplicate_registration_user(client: AsyncClient, db_session):
    response1 = await client.post(
        "/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "role": "teacher"
        }
    )
    assert response1.status_code == 200

    response2 = await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "password123",
                "role": "teacher"
            }
        )
    assert response2.status_code == 409
    data = response2.json()
    assert data['error_code'] == 'CONFLICT'


@pytest.mark.asyncio
async def test_registration_incorrect_role(client: AsyncClient, db_session):
    response = await client.post('/auth/register',
                                 json={
                                    "email": "duplicate@example.com",
                                    "password": "password123",
                                    "role": "admin"
                                 })
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient, db_session, student_user):
    response = await client.post('/auth/login',
                                 data={
                                    "username": student_user.email,
                                    "password": "password123"
                                 })
    refresh_token = response.cookies.get('refresh_token')
    data = response.json()
    assert refresh_token
    assert response.status_code == 200
    assert data['token_type'] == "Bearer"
    assert "access_token" in data


@pytest.mark.asyncio
async def test_login_incorrect_password_user(client: AsyncClient, db_session, student_user):
    response = await client.post('/auth/login',
                                     data={
                                        "username": student_user.email,
                                        "password": "uncorrentpass"
                                     })
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_refresh(client: AsyncClient, student_user):
    from app.utils.security import create_refresh_token

    refresh_token = create_refresh_token(user_id=student_user.id, role="student", email="student@example.com")
    response = await client.post('/auth/refresh', cookies={"refresh_token": refresh_token})

    assert response.status_code == 200
    data = response.json()
    assert data['token_type'] == "Bearer"
    assert "access_token" in data


@pytest.mark.asyncio
async def test_refresh_no_cookie(client: AsyncClient):
    response = await client.post('/auth/refresh')
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_logout(client: AsyncClient, student_user):
    from app.utils.security import create_refresh_token

    refresh_token = create_refresh_token(user_id=student_user.id, role="student", email="student@example.com")
    response = await client.post('/auth/logout', cookies={"refresh_token": refresh_token})

    response_cookie = response.cookies.get("refresh_token")
    
    assert response.status_code == 204


