from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import List

from app.schemas.course_schema import SimpleCourseSchema


class ResponseCreateSubsSchema(BaseModel):
    id: int
    student_id: int
    course_id: int
    start_date: datetime
    end_date: datetime
    is_active: bool
    course: SimpleCourseSchema

    model_config = ConfigDict(from_attributes=True)


class ResponseSubsCourseSchema(BaseModel):
    id: int
    course_id: int
    course_title: str
    start_date: datetime
    end_date: datetime
    is_active: bool

    model_config = ConfigDict(from_attributes=True)

class ResponseSubsSchema(BaseModel):
    items: List[ResponseSubsCourseSchema]
    total: int

    model_config = ConfigDict(from_attributes=True)

class ResponseSubsPaginationSchema(ResponseSubsSchema):
    page: int
    limit: int

