from fastapi import APIRouter, status, Query, Depends
from typing import List
from sqlalchemy import select

from app.crud.course import get_courses, get_course_by_id, create_course, update_course, delete_course
from app.database import SessionDep
from app.schemas.course_schema import ResponseCourseSchema, CreateCourseSchema, UpdateCourseSchema
from app.dependencies.auth import get_current_user
from app.models.subscription import SubscriptionORM
from app.exceptions.domain import PermissionDeniedException, ConflictException, InvalidRequestException


router = APIRouter(prefix='/courses', tags=['Course'])


@router.get('/', response_model=List[ResponseCourseSchema])
async def get_courses_api(session: SessionDep, skip: int = Query(default=0, ge=0), limit: int = Query(default=20, ge=1, le=100)):
    courses = await get_courses(skip, limit, session)
    return courses


@router.get('/{course_id}', response_model=ResponseCourseSchema)
async def get_course_id_api(course_id: int, session: SessionDep):
    course = await get_course_by_id(course_id, session)
    return course


@router.post('/', response_model=ResponseCourseSchema, status_code=status.HTTP_201_CREATED)
async def create_course_api(course: CreateCourseSchema, session: SessionDep, user = Depends(get_current_user)):
    if user.role != 'teacher':
        raise PermissionDeniedException(detail='You do not have permission to create a course')

    new_course = await create_course(course=course, teacher_id=user.id, session=session)
    return new_course


@router.patch('/{course_id}', response_model=ResponseCourseSchema)
async def update_course_api(course_data: UpdateCourseSchema, course_id: int, session: SessionDep, user=Depends(get_current_user)):
    course = await get_course_by_id(course_id, session)

    if user.role != "teacher":
        raise PermissionDeniedException(detail='You do not have permission to update a course')
    if user.id != course.teacher_id:
        raise PermissionDeniedException(detail='You are not the course owner')
    
    course_update = await update_course(course_data, course_id, session)
    if course_update is None:
        raise InvalidRequestException()
    return course_update


@router.delete('/{course_id}', status_code=204)
async def delete_course_api(course_id: int, session: SessionDep, user=Depends(get_current_user)):
    if user.role != 'teacher':
        raise PermissionDeniedException(detail='You do not have permission to delete a course')
    
    course = await get_course_by_id(course_id, session)

    if user.id != course.teacher_id:
        raise PermissionDeniedException(detail='You are not the course owner')

    stmt = (
        select(SubscriptionORM.id)
        .where(SubscriptionORM.course_id == course_id)
        .limit(1)
    )

    subscription = await session.scalar(stmt)
    if subscription is not None:
        raise ConflictException(detail='The course has subscription history and cannot be deleted')

    await delete_course(course_id, session)
    return None


    


    


    
