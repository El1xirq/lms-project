from fastapi import APIRouter, status, Depends, Query, BackgroundTasks

from app.database import SessionDep
from app.dependencies.auth import get_current_user
from app.crud.course import get_course_by_id
from app.crud.subscription import (get_active_subscription_by_course, 
                                   create_subscription, 
                                   get_subscription_with_course, 
                                   get_user_subscriptions,
                                   count_user_subscriptions,
                                   get_active_user_subscriptions,
                                   get_subscription_by_id,
                                   cancel_subscription)
from app.schemas.subscription_schema import ResponseCreateSubsSchema, ResponseSubsSchema, ResponseSubsPaginationSchema
from app.exceptions.domain import PermissionDeniedException, ConflictException, NotFoundException
from app.utils.email import send_subscription_email


router = APIRouter(prefix='/subscriptions', tags=['Subscriptions'])


@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ResponseCreateSubsSchema)
async def create_subscriptions_api(background_tasks: BackgroundTasks, course_id: int, session: SessionDep, user = Depends(get_current_user)):
    if user.role != "student":
        raise PermissionDeniedException(detail="Only students can subscribe to courses")

    course = await get_course_by_id(course_id, session)

    subscription_course = await get_active_subscription_by_course(student_id=user.id, course_id=course_id, session=session)
    if subscription_course is not None:
        raise ConflictException(detail="The user already has an active subscription to this course")

    new_subscription = await create_subscription(session, student_id=user.id, course_id=course_id)

    background_tasks.add_task(send_subscription_email, 
                              student_email=user.email,
                              course_title=course.title,
                              end_date=new_subscription.end_date)
    
    subscription_with_course = await get_subscription_with_course(subscription_id=new_subscription.id, session=session)
    return subscription_with_course


@router.get('/my', response_model=ResponseSubsPaginationSchema)
async def get_my_subscriptions(session: SessionDep, 
                               limit: int = Query(default=10, ge=1, le=100),
                               page: int = Query(default=1, ge=1),
                               user = Depends(get_current_user)):

    courses = await get_user_subscriptions(page, limit, student_id=user.id, session=session)
    total = await count_user_subscriptions(student_id=user.id, session=session)
    return ResponseSubsPaginationSchema(items=courses, total=total, page=page, limit=limit)


@router.get('/my/active', response_model=ResponseSubsSchema)
async def get_my_subscriptions_active(session: SessionDep, user=Depends(get_current_user)):
    courses = await get_active_user_subscriptions(session, user.id)

    total = len(courses)
    return ResponseSubsSchema(items=courses, total=total)


@router.delete('/{subs_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscriptions(subs_id: int, session: SessionDep, user = Depends(get_current_user)):
    subs = await get_subscription_by_id(subscription_id=subs_id, session=session)

    if subs is None:
        raise NotFoundException(detail="Subscription not found")
    if subs.student_id != user.id:
        raise PermissionDeniedException(detail="This is not your subscription")

    await cancel_subscription(subscription_id=subs_id, session=session)
    return None