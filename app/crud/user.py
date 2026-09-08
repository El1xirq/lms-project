from sqlalchemy import select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from app.database import SessionDep
from app.models.user import UserORM
from app.schemas.auth_schema import UpdateUserSchema, RegistrationData
from app.exceptions.domain import NotFoundException, DatabaseException, ConflictException




async def get_user_by_id(user_id: int, session: SessionDep):
    stmt = select(UserORM).where(UserORM.id == user_id, UserORM.is_active==True)
    result = (await session.execute(stmt)).scalar_one_or_none()
    if result is None:
        raise NotFoundException("User not found")
    return result
    

async def get_user_by_email(email: str, session: SessionDep):
    stmt = select(UserORM).where(UserORM.email == email, UserORM.is_active==True)
    result = (await session.execute(stmt)).scalar_one_or_none()
    return result
    

async def create_user(user: RegistrationData, session: SessionDep):
    try:
        new_user = UserORM(email=user.email, hashed_password=user.hashed_password, role=user.role)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user

    except IntegrityError:
        await session.rollback()
        raise ConflictException("User with this email already exists")
    except SQLAlchemyError:
        await session.rollback()
        raise DatabaseException()


async def update_user(user_id: int, user_update: UpdateUserSchema, session: SessionDep):
    user = await get_user_by_id(user_id, session)

    update_options = user_update.model_dump(exclude_none=True)
    
    if not update_options:
        return None

    stmt = update(UserORM).where(UserORM.id == user_id).values(update_options)
    await session.execute(stmt)
    await session.commit()
    return await get_user_by_id(user_id, session)


async def delete_user(user_id: int, session: SessionDep):
    user = await get_user_by_id(user_id, session)

    stmt = update(UserORM).where(UserORM.id == user_id).values(is_active = False)
    await session.execute(stmt)
    await session.commit()
    return True
    
