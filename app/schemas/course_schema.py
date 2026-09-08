from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from decimal import Decimal


class UpdateCourseSchema(BaseModel):
    title: str | None = Field(default=None, max_length=100)
    description: str | None = Field(default=None, max_length=2000)
    price: Decimal | None = Field(default=None, gt=0)


class ResponseCourseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    description: str
    price: Decimal
    teacher_id: int
    created_at: datetime


class CreateCourseSchema(BaseModel):
    title: str = Field(max_length=100)
    description: str = Field(max_length=2000)
    price: Decimal = Field(gt=0)


class SimpleCourseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    price: Decimal

