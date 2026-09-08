from sqlalchemy import select, update, func
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import SubscriptionORM
from app.database import SessionDep
from app.exceptions.domain import NotFoundException, ConflictException



async def create_subscription(session: SessionDep, student_id: int, course_id: int):
    try:
        await session.execute(
            update(SubscriptionORM)
            .where(
                SubscriptionORM.student_id == student_id,
                SubscriptionORM.course_id == course_id,
                SubscriptionORM.is_active == True,
                SubscriptionORM.end_date <= datetime.now(timezone.utc),
            )
            .values(is_active=False)
        )
        new_sub = SubscriptionORM(student_id=student_id, course_id=course_id)
        session.add(new_sub)
        await session.commit()
        await session.refresh(new_sub)
        return new_sub
    except IntegrityError:
        await session.rollback()
        raise ConflictException("The user already has an active subscription to this course")
    except SQLAlchemyError:
        await session.rollback()
        raise


async def get_active_subscription_by_course(student_id: int, course_id: int, session: SessionDep):
    stmt = select(SubscriptionORM).where(SubscriptionORM.student_id==student_id, 
                                         SubscriptionORM.course_id==course_id, 
                                         SubscriptionORM.is_active==True,
                                         SubscriptionORM.end_date > datetime.now(timezone.utc))
    result = (await session.execute(stmt)).scalar_one_or_none()
    return result


async def get_user_subscriptions(page: int, limit: int, student_id: int, session: SessionDep, is_active: bool = None):
    offset = (page-1) * limit
    stmt = (select(SubscriptionORM)
            .options(joinedload(SubscriptionORM.course))
            .where(SubscriptionORM.student_id == student_id)
            .offset(offset)
            .limit(limit)
            .order_by(SubscriptionORM.end_date.desc()))

    if is_active is not None:
        stmt = stmt.where(SubscriptionORM.is_active == is_active)
    
    result = (await session.scalars(stmt)).unique().all()
    return result


async def count_user_subscriptions(student_id: int, session: SessionDep, is_active: bool = None) -> int:
    stmt = select(func.count()).select_from(SubscriptionORM).where(
        SubscriptionORM.student_id == student_id
    )
    if is_active is not None:
        stmt = stmt.where(SubscriptionORM.is_active == is_active)

    return int((await session.scalar(stmt)) or 0)
    


async def get_active_user_subscriptions(session: SessionDep, student_id: int):
    stmt = (select(SubscriptionORM)
            .options(joinedload(SubscriptionORM.course))
            .where(SubscriptionORM.end_date > datetime.now(timezone.utc), 
                   SubscriptionORM.is_active ==True, 
                   SubscriptionORM.student_id == student_id)
            .order_by(SubscriptionORM.end_date.desc()))
    result = (await session.execute(stmt)).scalars().all()
    return result


async def check_subscription_expiry(student_id: int, course_id: int, session: SessionDep):
    stmt = (select(SubscriptionORM)
            .where(SubscriptionORM.student_id == student_id, 
                   SubscriptionORM.course_id == course_id, 
                   SubscriptionORM.is_active == True,
                   SubscriptionORM.end_date > datetime.now(timezone.utc)))
    result = (await session.execute(stmt)).scalar_one_or_none()
    return result


async def get_subscription_with_course(subscription_id: int, session: SessionDep):
    stmt = (select(SubscriptionORM)
            .options(joinedload(SubscriptionORM.course))
            .where(SubscriptionORM.id == subscription_id))
    result = (await session.execute(stmt)).scalar_one_or_none()
    if result is None:
        raise NotFoundException(detail="Not found subscription, with course")
    return result


async def get_subscription_by_id(subscription_id: int, session: SessionDep):
    stmt = select(SubscriptionORM).where(SubscriptionORM.id == subscription_id)
    result = (await session.execute(stmt)).scalar_one_or_none()
    return result


async def cancel_subscription(subscription_id: int, session: SessionDep):
    stmt = update(SubscriptionORM).where(SubscriptionORM.id == subscription_id, SubscriptionORM.is_active==True).values(is_active=False)
    await session.execute(stmt)
    await session.commit()


async def deactivate_expired_subscriptions(session: AsyncSession):
    stmt = (update(SubscriptionORM)
    .where(SubscriptionORM.is_active==True, SubscriptionORM.end_date < datetime.now(timezone.utc))
    .values(is_active=False)
    .returning(SubscriptionORM.id))
    result = await session.execute(stmt)
    await session.commit()
    updated_ids = result.scalars().all()
    return len(updated_ids)


async def get_subscriptions_expiring_soon(session: AsyncSession, days: int = 3):
    now = datetime.now(timezone.utc)
    start_date = now + timedelta(days=days)
    end_date = start_date + timedelta(days=1)
    stmt = (
        select(SubscriptionORM)
        .options(joinedload(SubscriptionORM.student))
        .options(joinedload(SubscriptionORM.course))
        .where(
            SubscriptionORM.is_active == True,
            SubscriptionORM.end_date >= start_date,
            SubscriptionORM.end_date < end_date
        )
    )

    result = await session.execute(stmt)
    return result.scalars().all()