from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, update, delete

from app.models.course import CourseORM
from app.database import SessionDep
from app.schemas.course_schema import UpdateCourseSchema, CreateCourseSchema
from app.exceptions.domain import NotFoundException


async def create_course(course: CreateCourseSchema, teacher_id: int, session: SessionDep):
    try:
        new_course = CourseORM(title=course.title, description=course.description, price=course.price, teacher_id=teacher_id)
        session.add(new_course)
        await session.commit()
        await session.refresh(new_course)
        return new_course
    except SQLAlchemyError:
        await session.rollback()
        raise


async def get_courses(skip: int, limit: int, session: SessionDep):
    stmt = select(CourseORM).offset(skip).limit(limit).order_by(CourseORM.created_at.desc())
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_course_by_id(course_id: int, session: SessionDep):
    stmt = select(CourseORM).where(CourseORM.id == course_id)
    result = (await session.execute(stmt)).scalar_one_or_none()

    if result is None:
        raise NotFoundException("Courses not found")

    return result


async def update_course(update_course: UpdateCourseSchema, course_id: int, session: SessionDep):
    update_options = update_course.model_dump(exclude_none=True)
    if not update_options:
        return None

    stmt = update(CourseORM).where(CourseORM.id == course_id).values(update_options)
    await session.execute(stmt)
    await session.commit()

    course = await get_course_by_id(course_id, session)
    return course


async def delete_course(course_id: int, session: SessionDep):
    stmt = delete(CourseORM).where(CourseORM.id == course_id)
    await session.execute(stmt)
    await session.commit()
    return True



    

    