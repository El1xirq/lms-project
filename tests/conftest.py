import asyncio
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool
from unittest.mock import patch

from app.config import settings
from app.database import Base, get_connection_db
from app.main import app


test_engine = create_async_engine(
    settings.test_db,
    poolclass=NullPool,
)
test_session_local = async_sessionmaker(test_engine, expire_on_commit=False)


async def override_get_db():
    async with test_session_local() as session:
        yield session

app.dependency_overrides[get_connection_db] = override_get_db


@pytest_asyncio.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture
async def db_session():
    async with test_session_local() as session:
        yield session


@pytest_asyncio.fixture(autouse=True)
async def cleanup():
    yield
    async with test_session_local() as session:
        await session.execute(text("TRUNCATE users, courses, subscriptions RESTART IDENTITY CASCADE"))
        await session.commit()


@pytest_asyncio.fixture
async def student_user(db_session):
    from app.crud.user import create_user
    from app.schemas.auth_schema import RegistrationData
    from app.utils.security import get_password_hash

    user_data = RegistrationData(
        email="student@test.com",
        hashed_password=get_password_hash("password123"),
        role="student"
    )
    return await create_user(user_data, db_session)


@pytest_asyncio.fixture
async def teacher_user(db_session):
    from app.crud.user import create_user
    from app.schemas.auth_schema import RegistrationData
    from app.utils.security import get_password_hash

    user_data = RegistrationData(
        email="teacher@test.com",
        hashed_password=get_password_hash("password123"),
        role="teacher"
    )
    return await create_user(user_data, db_session)


@pytest_asyncio.fixture
async def teacher_auth_headers(teacher_user):
    from app.utils.security import create_access_token

    token = create_access_token(
        user_id=teacher_user.id,
        role=teacher_user.role,
        email=teacher_user.email
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def student_auth_headers(student_user):
    from app.utils.security import create_access_token

    token = create_access_token(
        user_id=student_user.id,
        role=student_user.role,
        email=student_user.email
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def course(db_session, teacher_user):
    from app.crud.course import create_course
    from app.schemas.course_schema import CreateCourseSchema
    
    course_data = CreateCourseSchema(
        title="Test Course",
        description="Description",
        price=100.00
    )
    return await create_course(course_data, teacher_user.id, db_session)


@pytest_asyncio.fixture
async def another_teacher_user(db_session):
    from app.crud.user import create_user
    from app.schemas.auth_schema import RegistrationData
    from app.utils.security import get_password_hash
    
    user_data = RegistrationData(
        email="another_teacher@test.com",
        hashed_password=get_password_hash("password123"),
        role="teacher"
    )
    return await create_user(user_data, db_session)


@pytest_asyncio.fixture
async def another_teacher_auth_headers(another_teacher_user):
    from app.utils.security import create_access_token

    token = create_access_token(
        user_id=another_teacher_user.id,
        role=another_teacher_user.role,
        email=another_teacher_user.email
    )
    return {"Authorization": f"Bearer {token}"}


@pytest_asyncio.fixture
async def active_subscription(student_user, course, db_session):
    from app.crud.subscription import create_subscription
    subs = await create_subscription(db_session, student_user.id, course.id)
    return subs


@pytest_asyncio.fixture()
async def mock_email():
    with patch("app.api.subscription.send_subscription_email") as mock:
        yield mock


@pytest_asyncio.fixture
async def another_student_user(db_session):
    from app.crud.user import create_user
    from app.schemas.auth_schema import RegistrationData
    from app.utils.security import get_password_hash
    
    user_data = RegistrationData(
        email="another_student@test.com",
        hashed_password=get_password_hash("password123"),
        role="student"
    )
    return await create_user(user_data, db_session)


@pytest_asyncio.fixture
async def another_student_auth_headers(another_student_user):
    from app.utils.security import create_access_token

    token = create_access_token(
        user_id=another_student_user.id,
        role=another_student_user.role,
        email=another_student_user.email
    )
    return {"Authorization": f"Bearer {token}"}

    