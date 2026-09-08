from httpx import AsyncClient
import pytest


@pytest.mark.asyncio
async def test_create_subscriptions_student(client: AsyncClient, course, student_auth_headers, mock_email):
    response = await client.post(f'/subscriptions/?course_id={course.id}', headers=student_auth_headers)
    assert response.status_code == 201
    mock_email.assert_called_once()


@pytest.mark.asyncio
async def test_create_subscriptions_teacher(client: AsyncClient, course,  teacher_auth_headers):
    response = await client.post(f'/subscriptions/?course_id={course.id}', headers=teacher_auth_headers)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_duplicate_subscriptions(client: AsyncClient, course, student_auth_headers, active_subscription):
    response = await client.post(f'/subscriptions/?course_id={course.id}', headers=student_auth_headers)
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_get_subscriptions(client: AsyncClient, student_auth_headers):
    response = await client.get(f'/subscriptions/my', headers=student_auth_headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_cancel_subscriptions(client: AsyncClient, active_subscription, student_auth_headers):
    response = await client.delete(f'/subscriptions/{active_subscription.id}', headers=student_auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_cancel_subscriptions_no_owner(client: AsyncClient, active_subscription, another_student_auth_headers):
    response = await client.delete(f'/subscriptions/{active_subscription.id}', headers=another_student_auth_headers)
    assert response.status_code == 403
    data = response.json()
    assert data['error_code'] == "FORBIDDEN"

    