import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_create_course_teacher(client: AsyncClient, teacher_user, teacher_auth_headers):
    response = await client.post('/courses/', headers=teacher_auth_headers,
                           json={
                               'title': "TestCourse",
                               'description': 'test',
                               'price': 100.00,
                           })
    assert response.status_code == 201
    data = response.json()
    assert 'id' in data
    assert 'created_at' in data


@pytest.mark.asyncio
async def test_create_course_student(client: AsyncClient, student_user, student_auth_headers):
    response = await client.post('/courses/', headers=student_auth_headers,
                           json={
                               'title': "TestCourse",
                               'description': 'test',
                               'price': 100.00,
                           })
    assert response.status_code == 403
    data = response.json()
    assert data['error_code'] == 'FORBIDDEN'


@pytest.mark.asyncio
async def test_get_courses_pagination(client: AsyncClient):
    response = await client.get('/courses/?skip=0&limit=10')

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_course_id(client: AsyncClient, course):
    response = await client.get(f'/courses/{course.id}')
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_get_course_id_no_found(client: AsyncClient):
    response = await client.get(f'/courses/99999')
    assert response.status_code == 404
    data = response.json()
    assert data['error_code'] == 'NOT_FOUND'


@pytest.mark.asyncio
async def test_update_course(client: AsyncClient, course, teacher_auth_headers):
    response = await client.patch(f'/courses/{course.id}', headers=teacher_auth_headers,
                                  json={
                                      'title': 'Update Course',
                                      'description': 'Update Description'
                                  })

    assert response.status_code == 200
    data = response.json()
    assert data['title'] == 'Update Course'
    assert data['description'] == 'Update Description'


@pytest.mark.asyncio
async def test_update_course_no_owner(client: AsyncClient, another_teacher_auth_headers, course):
    response = await client.patch(f'/courses/{course.id}', headers=another_teacher_auth_headers,
                                      json={
                                          'title': 'Update Course',
                                          'description': 'Update Description'
                                      })
    assert response.status_code == 403  


@pytest.mark.asyncio
async def test_delete_course(client: AsyncClient, course, teacher_auth_headers):
    response = await client.delete(f'/courses/{course.id}', headers=teacher_auth_headers)
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_course_active_subs(client: AsyncClient, course, teacher_auth_headers, active_subscription):
    response = await client.delete(f'/courses/{course.id}', headers=teacher_auth_headers)
    assert response.status_code == 409